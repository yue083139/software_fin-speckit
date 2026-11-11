"""匯入端點（guided-notes-import D5–D7）。連結下載一律以 httpx MockTransport 替身，不連網。"""
import httpx
import pytest
from conftest import TEACHER_KEY
from fastapi.testclient import TestClient

from quiz_server.app import create_app
from quiz_server.sources import XLSX_TYPE, SourceError, export_url

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
    assert view["questions"] == [
        {"number": 1, "labels": ["（1）", "（2）"]},
        {"number": 2, "labels": ["（1）", "（2）"]},
        {"number": 3, "labels": [""]},
        {"number": 4, "labels": [""]},
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
    (EDIT_URL, f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx&gid=0"),
    (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"),
    (f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=abc",
     f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"),
])
def test_export_url_rewrite(url, expected):
    assert export_url(url) == expected


@pytest.mark.parametrize("url", [
    f"http://docs.google.com/spreadsheets/d/{SHEET_ID}/edit",
    f"https://docs.google.com:8443/spreadsheets/d/{SHEET_ID}/edit",
    f"https://evil.example/spreadsheets/d/{SHEET_ID}/edit",
    f"https://docs.google.com.evil.example/spreadsheets/d/{SHEET_ID}/edit",
    "https://docs.google.com/spreadsheets/d/short/edit",
    "https://docs.google.com/document/d/" + SHEET_ID + "/edit",
])
def test_export_url_rejects(url):
    with pytest.raises(SourceError):
        export_url(url)


def _client_with(activity, handler):
    calls: list[str] = []

    def record(request: httpx.Request) -> httpx.Response:
        calls.append(str(request.url))
        return handler(request)

    app = create_app(activity=activity, teacher_key=TEACHER_KEY, http_transport=httpx.MockTransport(record))
    return TestClient(app), calls


def import_url(c, url=EDIT_URL):
    return c.post("/api/teacher/import-url", json={"url": url}, headers={"X-Teacher-Key": TEACHER_KEY})


def test_import_url_follows_google_redirect(activity, fixture_bytes):
    data = fixture_bytes("group.xlsx")

    def handler(req: httpx.Request) -> httpx.Response:
        if req.url.host == "docs.google.com":
            return httpx.Response(307, headers={"location": "https://doc-0s-1c.googleusercontent.com/export/x"})
        return httpx.Response(200, headers={"content-type": XLSX_TYPE}, content=data)

    c, calls = _client_with(activity, handler)
    with c:
        r = import_url(c)
    assert r.status_code == 200 and r.json()["count"] == 4
    assert calls[0].startswith(f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx")


def test_import_url_redirect_to_foreign_host_is_refused(activity):
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"location": "http://127.0.0.1:9/internal"})

    c, calls = _client_with(activity, handler)
    with c:
        r = import_url(c)
    assert r.status_code == 400 and "非 Google" in r.json()["detail"]
    assert all("127.0.0.1" not in u for u in calls)


def test_import_url_private_sheet(activity):
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": "text/html"}, content=b"<html>login</html>")

    c, _ = _client_with(activity, handler)
    with c:
        r = import_url(c)
    assert r.status_code == 400 and "知道連結者可檢視" in r.json()["detail"]


def test_import_url_too_large(activity):
    def handler(req: httpx.Request) -> httpx.Response:
        return httpx.Response(200, headers={"content-type": XLSX_TYPE}, content=b"0" * (5 * 1024 * 1024 + 1))

    c, _ = _client_with(activity, handler)
    with c:
        r = import_url(c)
    assert r.status_code == 400 and "5 MB" in r.json()["detail"]


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
