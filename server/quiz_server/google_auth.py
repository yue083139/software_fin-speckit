"""老師 Google 帳號 OAuth 2.0 登入（guided-notes-sheets-sync D1、D6）。

授權碼流程＋PKCE（S256）＋`prompt=consent`；`state` 一次性、10 分鐘，並以 cookie 綁定發起登入的瀏覽器。
權杖只存在本物件（伺服器記憶體）：不落地、不入日誌、不出現在任何回應。
"""
import base64
import hashlib
import json
import re
import secrets
import time
from collections.abc import Callable
from urllib.parse import urlencode

import httpx

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105 端點網址，不是密碼
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
REDIRECT_URI = "http://127.0.0.1:8000/api/google/callback"
SCOPES = "openid email https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive"
STATE_TTL = 600
REFRESH_MARGIN = 60
TIMEOUT_SECONDS = 15
COOKIE_NAME = "qz_gstate"

# 設定精靈白名單（easy-setup D2）：以 fullmatch 比對原值（`$` 會放過尾端換行），
# 字元集本身排除換行、`=`、引號、`#`
CLIENT_ID_PATTERN = re.compile(r"[0-9]{4,30}-[a-z0-9]{8,64}\.apps\.googleusercontent\.com")
CLIENT_SECRET_PATTERN = re.compile(r"GOCSPX-[A-Za-z0-9_-]{20,64}")
MAX_LEN = 128
BAD_CLIENT_ID = "用戶端 ID 格式不符（應以 .apps.googleusercontent.com 結尾）"
BAD_CLIENT_SECRET = "用戶端密鑰格式不符（應以 GOCSPX- 開頭）"  # noqa: S105 錯誤訊息，不是密碼
NOT_CONFIGURED = "伺服器未設定 Google OAuth 用戶端"
NOT_SIGNED_IN = "請先以 Google 帳號登入"
EXPIRED = "Google 登入已過期，請重新登入"


class GoogleConfigError(ValueError):
    """伺服器未設定 OAuth 用戶端；API 層轉 400。"""


class GoogleConfigInvalid(ValueError):
    """設定精靈送來的用戶端 ID 或密鑰不符白名單；API 層轉 422，訊息不含輸入值。"""


def validate_client(client_id: str, client_secret: str) -> None:
    if len(client_id) > MAX_LEN or not CLIENT_ID_PATTERN.fullmatch(client_id):
        raise GoogleConfigInvalid(BAD_CLIENT_ID)
    if len(client_secret) > MAX_LEN or not CLIENT_SECRET_PATTERN.fullmatch(client_secret):
        raise GoogleConfigInvalid(BAD_CLIENT_SECRET)


class GoogleAuthError(Exception):
    """未登入或登入已過期；API 層轉 401。"""


class GoogleCallbackError(Exception):
    """回呼不合法（state／cookie 不符、過期、重放、帶 error）；API 層轉 400 固定文案。"""


class GoogleApiError(Exception):
    """Google 端錯誤；API 層轉 502。訊息只含 Google 錯誤 status，不含網址與權杖。"""


def state_digest(state: str) -> str:
    return hashlib.sha256(state.encode()).hexdigest()


def google_error(resp: httpx.Response) -> GoogleApiError:
    try:
        status = resp.json().get("error", {})
        status = status.get("status") if isinstance(status, dict) else status
    except ValueError:
        status = None
    return GoogleApiError(f"Google 服務錯誤：{status}" if status else "Google 服務錯誤")


def _email_from_id_token(id_token: str | None) -> str | None:
    parts = (id_token or "").split(".")
    if len(parts) != 3:
        return None
    try:
        seg = parts[1] + "=" * (-len(parts[1]) % 4)
        email = json.loads(base64.urlsafe_b64decode(seg)).get("email")
    except (ValueError, json.JSONDecodeError):
        return None
    return email if isinstance(email, str) else None


class GoogleSession:
    def __init__(self, client_id: str | None, client_secret: str | None,
                 transport: httpx.AsyncBaseTransport | None = None,
                 clock: Callable[[], float] = time.monotonic) -> None:
        self._client_id = client_id or ""
        self._client_secret = client_secret or ""
        self._transport = transport
        self._clock = clock
        self._pending: dict[str, tuple[str, float]] = {}
        self._access_token: str | None = None
        self._refresh_token: str | None = None
        self._expires_at = 0.0
        self.email: str | None = None
        # 設定世代：reconfigure 遞增；complete() await 回來若世代已變即丟棄（easy-setup D2 v1.1）
        self._generation = 0

    def reconfigure(self, client_id: str | None, client_secret: str | None) -> None:
        """設定精靈存檔後立即生效：換用戶端並作廢進行中的登入與既有權杖。"""
        self._client_id = client_id or ""
        self._client_secret = client_secret or ""
        self._generation += 1
        self._pending.clear()
        self._clear()

    @property
    def client_id_hint(self) -> str | None:
        """遮罩後的用戶端 ID（前 6 碼）：老師認得出是哪一組設定，又不整串外露。"""
        if not self.configured:
            return None
        suffix = "apps.googleusercontent.com"
        return self._client_id[:6] + "…" + (suffix if self._client_id.endswith(suffix) else "")

    @property
    def configured(self) -> bool:
        return bool(self._client_id and self._client_secret)

    @property
    def signed_in(self) -> bool:
        return self._access_token is not None

    def status(self) -> dict[str, object]:
        return {"configured": self.configured, "signed_in": self.signed_in,
                "email": self.email if self.signed_in else None,
                "client_id_hint": self.client_id_hint, "redirect_uri": REDIRECT_URI}

    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(transport=self._transport, timeout=TIMEOUT_SECONDS, follow_redirects=False)

    def begin(self) -> tuple[str, str]:
        """回傳 (授權網址, state)；呼叫端把 `state_digest(state)` 設進 cookie。"""
        if not self.configured:
            raise GoogleConfigError(NOT_CONFIGURED)
        now = self._clock()
        self._pending = {s: v for s, v in self._pending.items() if v[1] > now}
        state = secrets.token_urlsafe(32)
        verifier = secrets.token_urlsafe(64)
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
        self._pending[state] = (verifier, now + STATE_TTL)
        url = AUTH_URL + "?" + urlencode({
            "client_id": self._client_id, "redirect_uri": REDIRECT_URI, "response_type": "code",
            "scope": SCOPES, "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
            # Google 只在顯示同意畫面時發 refresh token；權杖不落地，重啟後再登入也要拿到
            "access_type": "offline", "prompt": "consent",
        })
        return url, state

    async def complete(self, state: str | None, code: str | None, cookie: str | None,
                       error: str | None = None) -> None:
        entry = self._pending.pop(state, None) if state else None  # 先作廢：任何結果都不可重放
        if (entry is None or entry[1] <= self._clock() or error or not code or not cookie
                or not secrets.compare_digest(cookie.encode(), state_digest(state or "").encode())):
            raise GoogleCallbackError
        verifier = entry[0]
        generation = self._generation
        data = {"client_id": self._client_id, "client_secret": self._client_secret, "code": code,
                "code_verifier": verifier, "grant_type": "authorization_code", "redirect_uri": REDIRECT_URI}
        body = await self._token_request(data)
        if generation != self._generation:
            raise GoogleCallbackError  # 等 Google 回應時設定被換掉：舊用戶端的授權不得落地
        self._store(body)
        self.email = _email_from_id_token(body.get("id_token"))

    async def token(self) -> str:
        if self._access_token is None:
            raise GoogleAuthError(NOT_SIGNED_IN)
        if self._clock() < self._expires_at - REFRESH_MARGIN:
            return self._access_token
        if self._refresh_token is None:
            if self._clock() < self._expires_at:
                return self._access_token
            self._clear()
            raise GoogleAuthError(EXPIRED)
        try:
            body = await self._token_request({
                "client_id": self._client_id, "client_secret": self._client_secret,
                "refresh_token": self._refresh_token, "grant_type": "refresh_token"})
        except GoogleApiError:
            self._clear()
            raise GoogleAuthError(EXPIRED) from None
        self._store(body)
        return self._access_token  # type: ignore[return-value]

    async def logout(self) -> None:
        token = self._refresh_token or self._access_token
        self._clear()
        if not token:
            return
        try:
            async with self.client() as c:
                # 權杖放表單本體，不放網址：網址會進 httpx 例外訊息與日誌（D1 v1.2）
                await c.post(REVOKE_URL, data={"token": token})
        except httpx.HTTPError:
            pass  # 撤銷失敗也已清空本機權杖

    async def _token_request(self, data: dict[str, str]) -> dict:
        try:
            async with self.client() as c:
                resp = await c.post(TOKEN_URL, data=data)
        except httpx.HTTPError:
            raise GoogleApiError("Google 服務錯誤") from None
        if resp.status_code != 200:
            raise google_error(resp)
        return resp.json()

    def _store(self, body: dict) -> None:
        token = body.get("access_token")
        if not isinstance(token, str):
            raise GoogleApiError("Google 服務錯誤")
        self._access_token = token
        self._expires_at = self._clock() + float(body.get("expires_in", 3600))
        if isinstance(body.get("refresh_token"), str):
            self._refresh_token = body["refresh_token"]

    def _clear(self) -> None:
        self._access_token = self._refresh_token = None
        self._expires_at = 0.0
        self.email = None
