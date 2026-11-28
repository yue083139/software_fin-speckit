"""測試用 Google 替身（httpx MockTransport；不連網）：權杖、撤銷、Sheets 讀寫、Drive 複製與刪除。

試算表內容由 xlsx 夾具轉成 Sheets API 的格狀資料（effectiveValue＋formattedValue＋merges），
與 2026-11-17 探針實測的回應形狀一致（probes/results/2026-11-17-google-sheets.txt）。
假權杖用「前綴＋0×n」形狀（CLAUDE.md「真實資料不入庫」）。
"""
import base64
import io
import json
from urllib.parse import parse_qs

import httpx
import openpyxl

ACCESS = "ya29." + "0" * 40
ACCESS2 = "ya29." + "0" * 41
REFRESH = "1//" + "0" * 40
CLIENT_ID = "test-client.apps.googleusercontent.com"
CLIENT_SECRET = "GOCSPX-" + "0" * 28
CODE = "4/" + "0" * 30
ORIGINAL_ID = "1" + "A" * 43
COPY_ID = "1" + "C" * 43
EMAIL = "teacher@example.com"


def id_token(email: str = EMAIL) -> str:
    seg = base64.urlsafe_b64encode(json.dumps({"email": email}).encode()).rstrip(b"=").decode()
    return f"e30.{seg}.sig"


def sheet_json(data: bytes, sheet_id_base: int = 0) -> list[dict]:
    """xlsx → Sheets API `sheets` 陣列。數字給 numberValue，字串給 stringValue。"""
    wb = openpyxl.load_workbook(io.BytesIO(data))
    sheets = []
    for i, ws in enumerate(wb.worksheets):
        rows = []
        for r in range(1, ws.max_row + 1):
            values = []
            for c in range(1, ws.max_column + 1):
                v = ws.cell(r, c).value
                if v is None:
                    values.append({})
                elif isinstance(v, bool):
                    values.append({"effectiveValue": {"boolValue": v}, "formattedValue": str(v).upper()})
                elif isinstance(v, int | float):
                    values.append({"effectiveValue": {"numberValue": float(v)}, "formattedValue": f"{v:g}"})
                else:
                    values.append({"effectiveValue": {"stringValue": str(v)}, "formattedValue": str(v)})
            rows.append({"values": values})
        merges = [{"sheetId": sheet_id_base + i, "startRowIndex": m.min_row - 1, "endRowIndex": m.max_row,
                   "startColumnIndex": m.min_col - 1, "endColumnIndex": m.max_col}
                  for m in ws.merged_cells.ranges]
        sheets.append({"properties": {"title": ws.title, "sheetId": sheet_id_base + i},
                       "merges": merges, "data": [{"rowData": rows}]})
    return sheets


class FakeGoogle:
    def __init__(self, data: bytes, title: str = "題組＋單題範本") -> None:
        self.title = title
        self.sheets = sheet_json(data)
        self.calls: list[httpx.Request] = []
        self.writes: list[dict] = []
        self.deleted: list[str] = []
        self.refresh_ok = True
        self.give_refresh = True
        self.fail: dict[str, int] = {}  # 動作名 → 狀態碼
        self.revoked: list[bytes] = []

    def transport(self) -> httpx.MockTransport:
        return httpx.MockTransport(self.handle)

    def _err(self, code: int) -> httpx.Response:
        return httpx.Response(code, json={"error": {"code": code, "status": "PERMISSION_DENIED"}})

    def handle(self, req: httpx.Request) -> httpx.Response:
        self.calls.append(req)
        url, method = req.url, req.method
        if url.host == "oauth2.googleapis.com" and url.path == "/token":
            form = {k: v[0] for k, v in parse_qs(req.content.decode()).items()}
            if form.get("grant_type") == "authorization_code":
                if "token" in self.fail:
                    return self._err(self.fail["token"])
                body = {"access_token": ACCESS, "expires_in": 3599, "id_token": id_token(),
                        "token_type": "Bearer"}
                if self.give_refresh:
                    body["refresh_token"] = REFRESH
                return httpx.Response(200, json=body)
            if form.get("grant_type") == "refresh_token":
                if not self.refresh_ok:
                    return httpx.Response(400, json={"error": "invalid_grant"})
                return httpx.Response(200, json={"access_token": ACCESS2, "expires_in": 3599})
        if url.host == "oauth2.googleapis.com" and url.path == "/revoke":
            self.revoked.append(req.content)
            if "revoke" in self.fail:
                raise httpx.ConnectError("boom " + str(url))
            return httpx.Response(200)
        if url.host == "www.googleapis.com" and url.path.endswith("/copy") and method == "POST":
            if "copy" in self.fail:
                return self._err(self.fail["copy"])
            return httpx.Response(200, json={"id": COPY_ID})
        if url.host == "www.googleapis.com" and method == "DELETE":
            self.deleted.append(url.path.rsplit("/", 1)[-1])
            return httpx.Response(204)
        if url.host == "sheets.googleapis.com":
            if url.path.endswith("values:batchUpdate"):
                if "write" in self.fail:
                    return self._err(self.fail["write"])
                self.writes.append(json.loads(req.content))
                return httpx.Response(200, json={})
            sid = url.path.rsplit("/", 1)[-1]
            if "read" in self.fail:
                return self._err(self.fail["read"])
            if url.params.get("includeGridData") == "true":
                return httpx.Response(200, json={"sheets": self.sheets})
            return httpx.Response(200, json={"properties": {"title": self.title},
                                             "sheets": [{"properties": s["properties"]} for s in self.sheets],
                                             "spreadsheetId": sid})
        return httpx.Response(404, json={"error": {"status": "NOT_FOUND"}})

    def requests_to(self, sheet_id: str) -> list[httpx.Request]:
        return [r for r in self.calls if sheet_id in str(r.url)]


def sign_in(client, headers) -> None:
    """走完 login → 回呼（TestClient 會帶回 login 設的 cookie）。"""
    url = client.post("/api/teacher/google/login", headers=headers).json()["url"]
    state = parse_qs(httpx.URL(url).query.decode())["state"][0]
    r = client.get("/api/google/callback", params={"state": state, "code": CODE})
    assert r.status_code == 200, r.text
