"""探針：驗證 guided-notes-sheets-sync 提案依賴的 Google OAuth／Sheets／Drive 行為。

對應 OpenSpec design D1–D3＝SpecKit research R1–R3。

用法（`make dev` 不可同時執行，本探針要佔用 127.0.0.1:8000 接 OAuth 回呼）：
    uv run --project server python probes/google_sheets_probe.py <Google 試算表連結>

前置：本機 `.env` 或環境變數有 GOOGLE_CLIENT_ID、GOOGLE_CLIENT_SECRET；
連結指向「題組＋單題」範本在自己雲端硬碟的副本。
步驟：
  1 登入：授權碼＋PKCE，重新導向 http://127.0.0.1:8000/api/google/callback（D1）
  2 讀取：spreadsheets.get 取值與合併 → 記憶體內工作表 → 現行解析器；與 group.xlsx 夾具逐題比對（D2）
  3 複製：候選 A Drive files.copy；候選 B Sheets create＋sheets.copyTo；比對合併範圍（D3）
  4 寫入：對候選 A 副本以 RAW 寫「=1+1」，讀回確認是文字（D3）
  5 換新：以 refresh token 換新 access token（D1，v1.2）
  6 撤銷：撤銷端點，權杖放表單本體（D1，v1.2）
輸出不印權杖、授權碼與試算表 id（以前 4 碼＋…遮蔽）；副本留在雲端硬碟，名稱含「探針」，可手動刪除。
"""
import base64
import hashlib
import http.server
import io
import json
import os
import re
import secrets
import sys
import threading
import webbrowser
from pathlib import Path
from urllib.parse import parse_qs, urlencode, urlsplit

import httpx
import openpyxl

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "server"))
from quiz_server.guided_notes import parse_workbook  # noqa: E402

REDIRECT = "http://127.0.0.1:8000/api/google/callback"
AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"  # noqa: S105 端點網址，不是密碼
SHEETS = "https://sheets.googleapis.com/v4/spreadsheets"
DRIVE = "https://www.googleapis.com/drive/v3/files"
SCOPES = "openid email https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive"
REVOKE_URL = "https://oauth2.googleapis.com/revoke"
FIXTURE = ROOT / "tests" / "fixtures" / "guided-notes" / "group.xlsx"


def mask(s: str) -> str:
    return f"{s[:4]}…" if s else "（空）"


def load_env() -> None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*([A-Z_]+)\s*=\s*(.*?)\s*$", line)
            if m and m.group(1) not in os.environ:
                os.environ[m.group(1)] = m.group(2).strip('"')


def step1_login(client_id: str, secret: str) -> dict:
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    state = secrets.token_urlsafe(32)
    got: dict[str, str] = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            q = parse_qs(urlsplit(self.path).query)
            got.update({k: v[0] for k, v in q.items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("探針已收到回呼，可關閉此分頁。".encode())

        def log_message(self, *args):
            pass

    srv = http.server.HTTPServer(("127.0.0.1", 8000), Handler)
    threading.Thread(target=srv.handle_request, daemon=True).start()
    url = AUTH_URL + "?" + urlencode({
        "client_id": client_id, "redirect_uri": REDIRECT, "response_type": "code", "scope": SCOPES,
        "state": state, "code_challenge": challenge, "code_challenge_method": "S256",
        "access_type": "offline", "prompt": "consent",
    })
    print("1 登入：已開啟瀏覽器，請以測試使用者帳號同意")
    webbrowser.open(url)
    while "code" not in got and "error" not in got:
        threading.Event().wait(0.5)
    srv.server_close()
    if "error" in got:
        sys.exit(f"1 登入 FAIL：Google 回 error={got['error']}")
    print(f"  回呼 state 相符：{got.get('state') == state}")
    r = httpx.post(TOKEN_URL, data={
        "client_id": client_id, "client_secret": secret, "code": got["code"], "code_verifier": verifier,
        "grant_type": "authorization_code", "redirect_uri": REDIRECT,
    }, timeout=15)
    body = r.json()
    print(f"  換權杖 HTTP {r.status_code}；有 refresh_token：{'refresh_token' in body}；"
          f"scope：{body.get('scope')}；expires_in：{body.get('expires_in')}")
    if r.status_code != 200:
        sys.exit(f"1 登入 FAIL：{body.get('error')}")
    payload = body.get("id_token", "").split(".")
    email = None
    if len(payload) == 3:
        seg = payload[1] + "=" * (-len(payload[1]) % 4)
        email = json.loads(base64.urlsafe_b64decode(seg)).get("email")
    print(f"  id_token 有 email：{bool(email)}（{mask(email or '')}）")
    print("1 登入 OK")
    return body


def grid_to_workbook(sheet: dict) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet["properties"]["title"]
    for r, row in enumerate(sheet.get("data", [{}])[0].get("rowData", []), 1):
        for c, cell in enumerate(row.get("values", []), 1):
            if "formattedValue" in cell:
                ws.cell(r, c, cell["formattedValue"])
    for m in sheet.get("merges", []):
        ws.merge_cells(start_row=m["startRowIndex"] + 1, start_column=m["startColumnIndex"] + 1,
                       end_row=m["endRowIndex"], end_column=m["endColumnIndex"])
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()


def summary(notes) -> list[tuple[int, list[str]]]:
    return [(q.number, [s.cell for s in q.slots]) for q in notes.questions]


def merges_of(client: httpx.Client, sid: str) -> list[list[tuple]]:
    r = client.get(f"{SHEETS}/{sid}", params={"fields": "sheets(properties.title,merges)"})
    r.raise_for_status()
    return [sorted((m["startRowIndex"], m["startColumnIndex"], m["endRowIndex"], m["endColumnIndex"])
                   for m in s.get("merges", [])) for s in r.json()["sheets"]]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    load_env()
    client_id, secret = os.environ.get("GOOGLE_CLIENT_ID", ""), os.environ.get("GOOGLE_CLIENT_SECRET", "")
    if not client_id or not secret:
        sys.exit("缺 GOOGLE_CLIENT_ID 或 GOOGLE_CLIENT_SECRET")
    m = re.search(r"/spreadsheets/d/([A-Za-z0-9_-]{20,})", sys.argv[1])
    if not m:
        sys.exit("連結不是 Google 試算表")
    sid = m.group(1)
    print(f"試算表 id：{mask(sid)}")

    tokens = step1_login(client_id, secret)
    token = tokens["access_token"]
    client = httpx.Client(headers={"Authorization": f"Bearer {token}"}, timeout=20)

    fields = "properties.title,sheets(properties(title,sheetId),merges,data.rowData.values.formattedValue)"
    r = client.get(f"{SHEETS}/{sid}", params={"includeGridData": "true", "fields": fields})
    print(f"2 讀取：HTTP {r.status_code}")
    r.raise_for_status()
    doc = r.json()
    first = doc["sheets"][0]
    print(f"  標題長度 {len(doc['properties']['title'])}；分頁 {first['properties']['title']}；"
          f"合併數 {len(first.get('merges', []))}")
    from_api = summary(parse_workbook(grid_to_workbook(first)))
    from_xlsx = summary(parse_workbook(FIXTURE.read_bytes()))
    print(f"  API 解析：{from_api}")
    print(f"  夾具解析：{from_xlsx}")
    print(f"2 讀取 {'OK' if from_api == from_xlsx else 'FAIL（與夾具不同）'}")

    original = merges_of(client, sid)
    r = client.post(f"{DRIVE}/{sid}/copy", json={"name": "探針A-搶答結果"}, params={"fields": "id"})
    print(f"3A Drive files.copy：HTTP {r.status_code}")
    copy_a = r.json().get("id") if r.status_code == 200 else None
    if copy_a:
        print(f"  副本 {mask(copy_a)} 合併與原檔相同：{merges_of(client, copy_a) == original}")
    else:
        print(f"  錯誤：{r.json().get('error', {}).get('status')}")

    r = client.post(SHEETS, json={"properties": {"title": "探針B-搶答結果"}},
                    params={"fields": "spreadsheetId"})
    print(f"3B Sheets create：HTTP {r.status_code}")
    if r.status_code == 200:
        copy_b = r.json()["spreadsheetId"]
        gid = first["properties"]["sheetId"]
        r2 = client.post(f"{SHEETS}/{sid}/sheets/{gid}:copyTo", json={"destinationSpreadsheetId": copy_b})
        print(f"  sheets.copyTo：HTTP {r2.status_code}；新分頁名：{r2.json().get('title')}")
        if r2.status_code == 200:
            print(f"  副本 B 該分頁合併與原檔相同：{merges_of(client, copy_b)[-1] == original[0]}")

    if copy_a:
        title = first["properties"]["title"]
        cell = from_api[2][1][0]
        rng = f"'{title}'!{cell}"
        r = client.post(f"{SHEETS}/{copy_a}/values:batchUpdate", json={
            "valueInputOption": "RAW", "data": [{"range": rng, "values": [["=1+1"]]}]})
        print(f"4 寫入 {cell}：HTTP {r.status_code}")
        # UNFORMATTED_VALUE：存成文字讀回 "=1+1"，若被當公式會讀回數字 2
        r = client.get(f"{SHEETS}/{copy_a}/values/{rng}", params={"valueRenderOption": "UNFORMATTED_VALUE"})
        got = r.json().get("values", [[None]])[0][0]
        r0 = client.get(f"{SHEETS}/{sid}/values/{rng}", params={"valueRenderOption": "UNFORMATTED_VALUE"})
        r0.raise_for_status()  # 讀取失敗不得被當成「原檔未被寫入」
        orig = r0.json().get("values", [[None]])[0][0]
        print(f"  副本讀回：{got!r}；原檔同格（HTTP {r0.status_code}）：{orig!r}（原檔應未被寫入）")
        print(f"4 寫入 {'OK' if got == '=1+1' else 'FAIL'}")
    r = httpx.post(TOKEN_URL, data={
        "client_id": client_id, "client_secret": secret,
        "refresh_token": tokens.get("refresh_token", ""), "grant_type": "refresh_token",
    }, timeout=15)
    print(f"5 換新：HTTP {r.status_code}；有 access_token：{'access_token' in r.json()}；"
          f"新 token 與舊不同：{r.json().get('access_token') not in (None, token)}")
    print(f"5 換新 {'OK' if r.status_code == 200 else 'FAIL'}")
    # 權杖放表單本體，不放網址（D1 v1.2：網址會進 httpx 例外訊息與日誌）
    r = httpx.post(REVOKE_URL, data={"token": tokens.get("refresh_token", token)}, timeout=15)
    print(f"6 撤銷：HTTP {r.status_code}")
    r2 = httpx.post(TOKEN_URL, data={
        "client_id": client_id, "client_secret": secret,
        "refresh_token": tokens.get("refresh_token", ""), "grant_type": "refresh_token",
    }, timeout=15)
    print(f"  撤銷後再換新：HTTP {r2.status_code}；error：{r2.json().get('error')}")
    print(f"6 撤銷 {'OK' if r.status_code == 200 and r2.status_code != 200 else 'FAIL'}")
    print("完成（副本留在雲端硬碟，名稱含「探針」）")


if __name__ == "__main__":
    main()
