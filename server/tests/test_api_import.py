"""匯入端點（guided-notes-import D5–D7、guided-notes-sheets-sync D4、D7）。

Google 一律以 MockTransport 替身，不連網。
"""
import httpx
import pytest
from conftest import TEACHER_KEY
from fastapi.testclient import TestClient
from google_fake import CLIENT_ID, CLIENT_SECRET

from quiz_server.app import create_app
from quiz_server.google_auth import GoogleSession
from quiz_server.sources import XLSX_TYPE, SourceError, parse_sheet_url

SHEET_ID = "1PXXwWiBKJNpPkLRoJLMzZWsAh4Jzn2bThHTeRAiq3Hg"
EDIT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"


def upload(client, data: bytes, name: str = "group.xlsx", headers=None):
    return client.post("/api/teacher/import", files={"file": (name, data, XLSX_TYPE)},
                       headers=headers if headers is not None else {"X-Teacher-Key": TEACHER_KEY})


def test_upload_broadcasts_questions(client, fixture_bytes):
    tok = client.post("/api/student/join", json={"team": "第1組"}).json()["token"]
    with client.websocket_connect(f"/ws?role=student&token={tok}") as ws:
        ws.receive_json()
        r = upload(client, fixture_bytes("group.xlsx"))
        assert r.status_code == 200 and r.json()["count"] == 4
        view = ws.receive_json()["view"]
    # question-settings、mode-timed-scoring 起每題另帶 multiplier、time_limit（只增欄位）
    assert view["questions"] == [
        {"number": 1, "labels": ["（1）", "（2）"], "multiplier": 1, "time_limit": 20},
        {"number": 2, "labels": ["（1）", "（2）"], "multiplier": 1, "time_limit": 20},
        {"number": 3, "labels": [""], "multiplier": 1, "time_limit": 20},
        {"number": 4, "labels": [""], "multiplier": 1, "time_limit": 20},
    ]


def test_student_view_has_numbers_only(client, fixture_bytes):
    upload(client, fixture_bytes("variant.xlsx"), "variant.xlsx")
    tok = client.post("/api/student/join", json={"team": "第2組"}).json()["token"]
    with client.websocket_connect(f"/ws?role=student&token={tok}") as ws:
        raw = ws.receive_text()
    assert "H11" not in raw and "variant.xlsx" not in raw and "二元樹" not in raw


def test_upload_requires_teacher(client, fixture_bytes):
    assert upload(client, fixture_bytes("single.xlsx"), headers={}).status_code == 401


@pytest.mark.parametrize("name,data,msg", [
    ("notes.csv", b"a,b", "只接受 .xlsx"),
    ("notes.xlsx", b"not xlsx", "不是有效的 xlsx"),
])
def test_upload_rejects_bad_files(client, activity, name, data, msg):
    r = upload(client, data, name)
    assert r.status_code == 400 and msg in r.json()["detail"]
    assert activity.questions == ()


def test_upload_rejected_while_answering(client, fixture_bytes, teacher_headers, activity):
    upload(client, fixture_bytes("single.xlsx"))
    client.post("/api/teacher/start", headers=teacher_headers)
    r = upload(client, fixture_bytes("group.xlsx"))
    assert r.status_code == 409
    assert len(activity.questions) == 6


@pytest.mark.parametrize("url,expected", [
    (EDIT_URL, (SHEET_ID, "0")),
    (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing", (SHEET_ID, None)),
    (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=abc", (SHEET_ID, None)),
    (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?gid=123#x", (SHEET_ID, "123")),
])
def test_parse_sheet_url(url, expected):
    assert parse_sheet_url(url) == expected


@pytest.mark.parametrize("url", [
    f"http://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
    f"https://docs.google.com:8443/spreadsheets/d/{SHEET_ID}/edit",
    f"https://evil.example/spreadsheets/d/{SHEET_ID}/edit",
    f"https://docs.google.com.evil.example/spreadsheets/d/{SHEET_ID}/edit",
    "https://docs.google.com/spreadsheets/d/short/edit",
    "https://docs.google.com/document/d/" + SHEET_ID + "/edit",
])
def test_parse_sheet_url_rejects(url):
    with pytest.raises(SourceError):
        parse_sheet_url(url)


def _client_with(activity, handler):
    calls: list[str] = []

    def record(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return handler(request)

    google = GoogleSession(CLIENT_ID, CLIENT_SECRET, transport=httpx.MockTransport(record))
    app = create_app(activity=activity, teacher_key=TEACHER_KEY, google=google)
    return TestClient(app), calls


def import_url(c, url=EDIT_URL):
    return c.post("/api/teacher/import-url", json={"url": url}, headers={"X-Teacher-Key": TEACHER_KEY})


def test_import_url_requires_google_sign_in_and_sends_no_request(activity):
    c, calls = _client_with(activity, lambda req: httpx.Response(500))
    with c:
        r = import_url(c)
    assert r.status_code == 401 and r.json()["detail"] == "請先以 Google 帳號登入"
    assert calls == [] and activity.questions == ()


def test_import_url_bad_host_sends_no_request(activity):
    c, calls = _client_with(activity, lambda req: httpx.Response(500))
    with c:
        r = import_url(c, "https://evil.example/spreadsheets/d/" + SHEET_ID + "/edit")
    assert r.status_code == 400 and calls == []


def test_import_url_rejected_while_answering_sends_no_request(activity, fixture_bytes):
    c, calls = _client_with(activity, lambda req: httpx.Response(500))
    with c:
        upload(c, fixture_bytes("single.xlsx"))
        c.post("/api/teacher/start", headers={"X-Teacher-Key": TEACHER_KEY})
        r = import_url(c)
    assert r.status_code == 409 and calls == []


def test_upload_does_not_need_google(client, fixture_bytes, activity):
    assert upload(client, fixture_bytes("group.xlsx")).status_code == 200
    assert activity.source_sheet_id is None
