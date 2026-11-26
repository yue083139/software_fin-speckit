"""student-qr D2：老師端點、老師 WebSocket、Google 回呼只接受本機 Host，且不得帶 Cloudflare 轉送標頭。

TestClient 預設 Host 為 `testserver`；conftest 把它加進本機允許清單，本檔以明確的 Host 標頭驗證公開網域被拒。
"""
import pytest
from conftest import TEACHER_KEY
from starlette.websockets import WebSocketDisconnect

PUBLIC = {"host": "penny-cheap-centered-fewer.trycloudflare.com"}
TUNNELED_LOCAL = {"host": "127.0.0.1:8000", "cf-connecting-ip": "203.0.113.9"}


@pytest.mark.parametrize("headers", [PUBLIC, TUNNELED_LOCAL, {"host": "192.168.1.5:8000"}])
def test_teacher_rest_rejects_non_local(client, teacher_headers, headers):
    r = client.get("/api/teacher/state", headers={**teacher_headers, **headers})
    assert r.status_code == 403
    assert r.json() == {"detail": "老師頁只能在本機開啟"}
    # 先擋 Host、不驗金鑰：錯金鑰也是 403，不洩漏金鑰對錯
    r = client.post("/api/teacher/start", headers={"X-Teacher-Key": "wrong", **headers})
    assert r.status_code == 403


@pytest.mark.parametrize("host", ["127.0.0.1:8000", "localhost:8000", "LOCALHOST", "[::1]:8000"])
def test_teacher_rest_accepts_local(client, teacher_headers, host):
    assert client.get("/api/teacher/state", headers={**teacher_headers, "host": host}).status_code == 200


def test_teacher_ws_rejects_public_host(client):
    with pytest.raises(WebSocketDisconnect) as exc:
        with client.websocket_connect(f"/ws?role=teacher&key={TEACHER_KEY}", headers=PUBLIC) as ws:
            ws.receive_json()
    assert exc.value.code == 4403


def test_student_endpoints_work_over_public_host(client):
    assert client.get("/api/public/info", headers=PUBLIC).status_code == 200
    r = client.post("/api/student/join", json={"team": "第1組"}, headers=PUBLIC)
    assert r.status_code == 200
    token = r.json()["token"]
    with client.websocket_connect(f"/ws?role=student&token={token}", headers=PUBLIC) as ws:
        assert ws.receive_json()["view"]["team"] == "第1組"
    assert client.get("/", headers=PUBLIC).status_code in (200, 404)  # 靜態頁有無建置皆可


def test_google_callback_rejects_public_host(client):
    r = client.get("/api/google/callback?state=probe-state-zz&code=probe-code-zz", headers=PUBLIC)
    assert r.status_code == 403
    assert "probe-" not in r.text  # 不回顯查詢參數


def test_student_url_only_in_teacher_view(activity, fixture_bytes):
    import asyncio

    from quiz_server.views import student_view, teacher_view
    activity.public_url = "https://penny-cheap-centered-fewer.trycloudflare.com/"
    asyncio.run(activity.load_questions(fixture_bytes("group.xlsx"), "group.xlsx"))
    assert teacher_view(activity)["student_url"] == activity.public_url
    assert "student_url" not in student_view(activity, "第1組")
    assert "trycloudflare" not in str(student_view(activity, "第1組"))


# teacher-key-error：金鑰錯誤先完成交握、不送任何訊息再以 4401 關閉，瀏覽器才拿得到 4401


@pytest.mark.parametrize("query", ["/ws?role=teacher", "/ws?role=teacher&key=wrong"])
def test_teacher_ws_bad_key_accepts_then_closes_4401(client, query):
    with client.websocket_connect(query) as ws:  # 交握前就關的話，這裡會直接拋例外
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()  # 第一則就是關閉：關閉前沒有任何 view
    assert exc.value.code == 4401


def test_public_host_takes_precedence_over_bad_key(client):
    with client.websocket_connect("/ws?role=teacher&key=wrong", headers=PUBLIC) as ws:
        with pytest.raises(WebSocketDisconnect) as exc:
            ws.receive_text()
    assert exc.value.code == 4403


def test_good_connection_unaffected_after_bad_key(client, teacher_headers, fixture_bytes):
    with client.websocket_connect("/ws?role=teacher&key=wrong") as bad:
        with pytest.raises(WebSocketDisconnect):
            bad.receive_text()
    # 錯金鑰連線關閉後，正常活動與推播不受影響
    with client.websocket_connect(f"/ws?role=teacher&key={TEACHER_KEY}") as ws:
        assert ws.receive_json()["view"]["role"] == "teacher"
        upload = {"file": ("group.xlsx", fixture_bytes("group.xlsx"), "application/octet-stream")}
        r = client.post("/api/teacher/import", headers=teacher_headers, files=upload)
        assert r.status_code == 200
        assert ws.receive_json()["view"]["source"] == "group.xlsx"
