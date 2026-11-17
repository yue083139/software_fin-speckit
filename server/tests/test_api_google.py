"""Google 登入與雲端讀寫端點（guided-notes-sheets-sync D1、D3、D6、D7）。全程 MockTransport，不連網。"""
from urllib.parse import parse_qs

import httpx
import pytest
from conftest import TEACHER_KEY
from fastapi.testclient import TestClient
from google_fake import ACCESS2, CLIENT_ID, CLIENT_SECRET, CODE, COPY_ID, REFRESH, FakeGoogle, sign_in

from quiz_server.app import create_app
from quiz_server.google_auth import GoogleSession

H = {"X-Teacher-Key": TEACHER_KEY}
URL = "https://docs.google.com/spreadsheets/d/" + "1" + "A" * 43 + "/edit#gid=0"


class Clock:
    def __init__(self) -> None:
        self.t = 1000.0

    def __call__(self) -> float:
        return self.t


@pytest.fixture
def fake(fixture_bytes):
    return FakeGoogle(fixture_bytes("group.xlsx"))


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def gclient(activity, fake, clock):
    session = GoogleSession(CLIENT_ID, CLIENT_SECRET, transport=fake.transport(), clock=clock)
    with TestClient(create_app(activity=activity, teacher_key=TEACHER_KEY, google=session)) as c:
        yield c


def _state(url: str) -> str:
    return parse_qs(httpx.URL(url).query.decode())["state"][0]


# ---- 登入 ----

def test_login_url_and_cookie(gclient):
    r = gclient.post("/api/teacher/google/login", headers=H)
    assert r.status_code == 200
    q = {k: v[0] for k, v in parse_qs(httpx.URL(r.json()["url"]).query.decode()).items()}
    assert q["prompt"] == "consent" and q["access_type"] == "offline"
    assert q["code_challenge_method"] == "S256" and len(q["code_challenge"]) == 43
    assert q["redirect_uri"] == "http://127.0.0.1:8000/api/google/callback"
    assert set(q["scope"].split()) == {"openid", "email", "https://www.googleapis.com/auth/spreadsheets",
                                       "https://www.googleapis.com/auth/drive"}
    cookie = r.headers["set-cookie"]
    assert "qz_gstate=" in cookie and "HttpOnly" in cookie and "samesite=lax" in cookie.lower()
    assert q["state"] not in cookie  # cookie 只存雜湊


def test_login_requires_teacher(gclient):
    assert gclient.post("/api/teacher/google/login").status_code == 401
    assert gclient.get("/api/teacher/google").status_code == 401


def test_callback_signs_in(gclient, fake):
    sign_in(gclient, H)
    assert gclient.get("/api/teacher/google", headers=H).json() == {
        "configured": True, "signed_in": True, "email": "teacher@example.com"}
    form = parse_qs(next(r for r in fake.calls if r.url.path == "/token").content.decode())
    assert form["code"] == [CODE] and len(form["code_verifier"][0]) >= 43


def test_forged_state_rejected(gclient, fake):
    gclient.post("/api/teacher/google/login", headers=H)
    r = gclient.get("/api/google/callback", params={"state": "forged", "code": CODE})
    assert r.status_code == 400 and "登入失敗" in r.text
    assert fake.calls == []


def test_state_replay_rejected(gclient):
    url = gclient.post("/api/teacher/google/login", headers=H).json()["url"]
    cookie = gclient.cookies.get("qz_gstate")
    assert gclient.get("/api/google/callback", params={"state": _state(url), "code": CODE}).status_code == 200
    gclient.cookies.set("qz_gstate", cookie, path="/api/google")
    r = gclient.get("/api/google/callback", params={"state": _state(url), "code": CODE})
    assert r.status_code == 400


def test_state_expires(gclient, clock, fake):
    url = gclient.post("/api/teacher/google/login", headers=H).json()["url"]
    clock.t += 601
    r = gclient.get("/api/google/callback", params={"state": _state(url), "code": CODE})
    assert r.status_code == 400 and fake.calls == []


def test_other_browser_without_cookie_rejected(gclient, activity, fake):
    """看得到授權網址的他人在自己的瀏覽器完成授權：沒有 cookie ⇒ 400（登入 CSRF，紅隊 v1.2）。"""
    url = gclient.post("/api/teacher/google/login", headers=H).json()["url"]
    gclient.cookies.clear()
    r = gclient.get("/api/google/callback", params={"state": _state(url), "code": CODE})
    assert r.status_code == 400 and fake.calls == []
    assert gclient.get("/api/teacher/google", headers=H).json()["signed_in"] is False


def test_cookie_of_another_login_rejected(gclient, fake):
    """瀏覽器帶的是另一次登入的 cookie（例：他人在自己瀏覽器先按過登入）⇒ 雜湊不符 400。"""
    url = gclient.post("/api/teacher/google/login", headers=H).json()["url"]
    gclient.post("/api/teacher/google/login", headers=H)  # 覆寫成第二次登入的 cookie
    r = gclient.get("/api/google/callback", params={"state": _state(url), "code": CODE})
    assert r.status_code == 400 and fake.calls == []


def test_callback_does_not_echo_params(gclient):
    url = gclient.post("/api/teacher/google/login", headers=H).json()["url"]
    payload = "<script>alert(1)</script>"
    r = gclient.get("/api/google/callback", params={"state": _state(url), "error": payload})
    assert r.status_code == 400 and payload not in r.text and "script" not in r.text


def test_not_configured(activity):
    app = create_app(activity=activity, teacher_key=TEACHER_KEY, google=GoogleSession(None, None))
    with TestClient(app) as c:
        assert c.get("/api/teacher/google", headers=H).json()["configured"] is False
        r = c.post("/api/teacher/google/login", headers=H)
    assert r.status_code == 400 and r.json()["detail"] == "伺服器未設定 Google OAuth 用戶端"


def test_refresh_before_expiry(gclient, fake, clock):
    sign_in(gclient, H)
    clock.t += 3599 - 30  # 進入 60 秒換新邊界
    assert gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H).status_code == 200
    assert any(parse_qs(r.content.decode()).get("grant_type") == ["refresh_token"]
               for r in fake.calls if r.url.path == "/token")
    assert any(r.headers.get("authorization") == f"Bearer {ACCESS2}" for r in fake.calls)


def test_no_refresh_token_expires_to_401(gclient, fake, clock):
    fake.give_refresh = False
    sign_in(gclient, H)
    clock.t += 3600
    r = gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    assert r.status_code == 401 and r.json()["detail"] == "Google 登入已過期，請重新登入"
    assert gclient.get("/api/teacher/google", headers=H).json()["signed_in"] is False


def test_refresh_failure_is_401(gclient, fake, clock):
    fake.refresh_ok = False
    sign_in(gclient, H)
    clock.t += 3600
    r = gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    assert r.status_code == 401 and r.json()["detail"] == "Google 登入已過期，請重新登入"


def test_logout_revokes_with_token_in_body(gclient, fake):
    sign_in(gclient, H)
    assert gclient.post("/api/teacher/google/logout", headers=H).json() == {"signed_in": False}
    revoke = next(r for r in fake.calls if r.url.path == "/revoke")
    assert REFRESH not in str(revoke.url) and parse_qs(revoke.content.decode())["token"] == [REFRESH]
    assert gclient.get("/api/teacher/google", headers=H).json()["signed_in"] is False


# ---- 匯入與寫回 ----

def test_import_url_reads_copy(gclient, fake, activity):
    sign_in(gclient, H)
    r = gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    assert r.status_code == 200
    assert r.json() == {"source": "題組＋單題範本", "count": 4,
                        "sheet_url": f"https://docs.google.com/spreadsheets/d/{COPY_ID}/edit"}
    assert activity.source_sheet_id == COPY_ID
    assert not any("export" in r.url.path for r in fake.calls)


def _play_and_end(c):
    t1 = c.post("/api/student/join", json={"team": "第1組"}).json()["token"]
    c.post("/api/teacher/start", headers=H)
    c.post("/api/student/submit", json={"question": 1, "answers": ["CPU", "作業系統"]},
           headers={"X-Team-Token": t1})
    c.post("/api/teacher/end", headers=H)


def test_export_sheet_writes_copy(gclient, fake):
    sign_in(gclient, H)
    gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    _play_and_end(gclient)
    r = gclient.post("/api/teacher/export-sheet", headers=H)
    assert r.status_code == 200 and r.json()["url"].endswith(f"/{COPY_ID}/edit")
    assert fake.writes[0]["data"] == [{"range": "'學習單'!H5", "values": [["CPU"]]},
                                      {"range": "'學習單'!H6", "values": [["作業系統"]]}]
    # 下載 xlsx 備援仍可用
    assert gclient.get("/api/teacher/export", headers=H).status_code == 200


def test_export_sheet_error_order(gclient, fake, fixture_bytes):
    # 未匯入、非 ended ⇒ 409 階段先於來源與登入
    r = gclient.post("/api/teacher/export-sheet", headers=H)
    assert r.status_code == 409 and r.json()["detail"] == "搶答結束後才能匯出"
    gclient.post("/api/teacher/import", headers=H,
                 files={"file": ("group.xlsx", fixture_bytes("group.xlsx"), "application/octet-stream")})
    _play_and_end(gclient)
    r = gclient.post("/api/teacher/export-sheet", headers=H)
    assert r.status_code == 409 and r.json()["detail"] == "題目不是從 Google 試算表匯入，請改用下載 xlsx"
    assert fake.calls == []
    assert gclient.post("/api/teacher/export-sheet").status_code == 401


def test_export_sheet_requires_sign_in(gclient, fake, activity):
    sign_in(gclient, H)
    gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    _play_and_end(gclient)
    gclient.post("/api/teacher/google/logout", headers=H)
    n = len(fake.calls)
    r = gclient.post("/api/teacher/export-sheet", headers=H)
    assert r.status_code == 401 and len(fake.calls) == n


def test_export_sheet_google_error_502(gclient, fake):
    sign_in(gclient, H)
    gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    _play_and_end(gclient)
    fake.fail["write"] = 403
    r = gclient.post("/api/teacher/export-sheet", headers=H)
    assert r.status_code == 502 and r.json()["detail"] == "Google 服務錯誤：PERMISSION_DENIED"


def test_import_error_order(gclient, fake):
    # 400 連結先於 401 登入
    r = gclient.post("/api/teacher/import-url", json={"url": "https://evil.example/x"}, headers=H)
    assert r.status_code == 400
    r = gclient.post("/api/teacher/import-url", json={"url": URL}, headers=H)
    assert r.status_code == 401
    assert fake.calls == []
