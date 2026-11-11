"""身分、組別憑證、階段同步與老師金鑰（app-skeleton D4–D6）。"""
import pytest
from conftest import TEACHER_KEY
from starlette.websockets import WebSocketDisconnect


def join(client, team: str) -> str:
    r = client.post("/api/student/join", json={"team": team})
    assert r.status_code == 200, r.text
    return r.json()["token"]


def _recv_phase(ws) -> str:
    return ws.receive_json()["view"]["phase"]


def test_phase_sync_all_clients(client, teacher_headers):
    t1, t2 = join(client, "第1組"), join(client, "第2組")
    with client.websocket_connect(f"/ws?role=teacher&key={TEACHER_KEY}") as t, \
         client.websocket_connect(f"/ws?role=student&token={t1}") as s1, \
         client.websocket_connect(f"/ws?role=student&token={t2}") as s2:
        assert [_recv_phase(w) for w in (t, s1, s2)] == ["preparing"] * 3
        assert client.post("/api/teacher/start", headers=teacher_headers).status_code == 200
        assert [_recv_phase(w) for w in (t, s1, s2)] == ["answering"] * 3
        assert client.post("/api/teacher/end", headers=teacher_headers).status_code == 200
        assert [_recv_phase(w) for w in (t, s1, s2)] == ["ended"] * 3


def test_per_connection_seq_increments_by_one(client, teacher_headers):
    tok = join(client, "第1組")
    with client.websocket_connect(f"/ws?role=student&token={tok}") as s:
        first = s.receive_json()
        client.post("/api/teacher/start", headers=teacher_headers)
        second = s.receive_json()
    assert (first["seq"], second["seq"]) == (1, 2)
    assert "version" not in second


@pytest.mark.parametrize("headers", [{}, {"X-Teacher-Key": "wrong"}])
@pytest.mark.parametrize("path", ["/api/teacher/start", "/api/teacher/end", "/api/teacher/reset"])
def test_teacher_api_requires_key(client, activity, headers, path):
    r = client.post(path, headers=headers)
    assert r.status_code == 401
    assert activity.phase.value == "preparing"


def test_teacher_state_requires_key(client):
    assert client.get("/api/teacher/state").status_code == 401


@pytest.mark.parametrize("query", ["/ws?role=teacher", "/ws?role=teacher&key=wrong"])
def test_teacher_ws_requires_key(client, query):
    with pytest.raises(WebSocketDisconnect) as e:
        with client.websocket_connect(query) as ws:
            ws.receive_json()
    assert e.value.code == 4401


def test_join_once_per_team(client):
    join(client, "第1組")
    r = client.post("/api/student/join", json={"team": "第1組"})
    assert r.status_code == 409


def test_join_unknown_team_404(client):
    assert client.post("/api/student/join", json={"team": "第9組"}).status_code == 404


def test_release_allows_rejoin_and_revokes_old_token(client, teacher_headers):
    old = join(client, "第1組")
    r = client.post("/api/teacher/release", json={"team": "第1組"}, headers=teacher_headers)
    assert r.status_code == 200
    join(client, "第1組")
    with client.websocket_connect(f"/ws?role=student&token={old}") as ws:
        assert ws.receive_json()["view"]["team_valid"] is False


def test_release_requires_teacher(client):
    join(client, "第1組")
    assert client.post("/api/teacher/release", json={"team": "第1組"}).status_code == 401


@pytest.mark.parametrize("query", ["/ws?role=student", "/ws?role=student&token=forged",
                                   "/ws?role=student&team=第1組"])
def test_bad_token_gets_minimal_view(client, query):
    join(client, "第1組")
    with client.websocket_connect(query) as ws:
        view = ws.receive_json()["view"]
    assert view == {"role": "student", "phase": "preparing", "team": None, "team_valid": False}


def test_teacher_sees_joined_teams(client, teacher_headers):
    join(client, "第3組")
    assert client.get("/api/teacher/state", headers=teacher_headers).json()["joined"] == ["第3組"]


def test_illegal_transition_is_409(client, teacher_headers, activity):
    r = client.post("/api/teacher/end", headers=teacher_headers)
    assert r.status_code == 409
    assert activity.phase.value == "preparing"


def test_configure_teams_broadcasts_and_revokes_tokens(client, teacher_headers):
    tok = join(client, "第1組")
    assert client.post("/api/teacher/teams", json={"count": 5}, headers=teacher_headers).status_code == 200
    assert client.get("/api/public/info").json()["teams"] == [f"第{i}組" for i in range(1, 6)]
    with client.websocket_connect(f"/ws?role=student&token={tok}") as ws:
        assert ws.receive_json()["view"]["team_valid"] is False


def test_configure_teams_rejected_while_answering(client, teacher_headers):
    client.post("/api/teacher/start", headers=teacher_headers)
    assert client.post("/api/teacher/teams", json={"count": 5}, headers=teacher_headers).status_code == 409


def test_configure_teams_out_of_range(client, teacher_headers):
    assert client.post("/api/teacher/teams", json={"count": 20}, headers=teacher_headers).status_code == 422


def test_binary_frame_is_ignored(client, teacher_headers):
    tok = join(client, "第1組")
    with client.websocket_connect(f"/ws?role=student&token={tok}") as ws:
        ws.receive_json()
        ws.send_bytes(b"\x00\x01")
        client.post("/api/teacher/start", headers=teacher_headers)
        assert ws.receive_json()["view"]["phase"] == "answering"
