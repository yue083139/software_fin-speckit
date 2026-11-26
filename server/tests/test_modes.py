"""模式登記表與切換（game-mode-framework D1）。"""
from conftest import TEACHER_KEY

from quiz_server.modes import DEFAULT_MODE, MODES
from quiz_server.scoring import AccuracyRule, ClassicBuzzRule


def test_registry():
    assert DEFAULT_MODE == "classic"
    assert [m.key for m in MODES.values()] == ["classic", "accuracy", "timed"]
    assert MODES["timed"].sequential and not MODES["timed"].judged
    assert isinstance(MODES["classic"].rule, ClassicBuzzRule) and not MODES["classic"].judged
    assert isinstance(MODES["accuracy"].rule, AccuracyRule) and MODES["accuracy"].judged


def test_activity_rule_follows_mode(activity):
    import asyncio
    assert activity.mode.key == "classic" and activity.rule is MODES["classic"].rule
    asyncio.run(activity.set_mode("accuracy"))
    assert activity.rule is MODES["accuracy"].rule


def test_set_mode_api_and_views(loaded_client, teacher_headers):
    r = loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    assert r.status_code == 200 and r.json() == {"mode": "accuracy"}
    view = loaded_client.get("/api/teacher/state", headers=teacher_headers).json()
    assert view["mode"] == {"key": "accuracy", "label": "只計對錯", "judged": True, "sequential": False}
    assert {"key": "classic", "label": "經典搶答"} in view["modes"]
    assert view["score_label"] == "得分"
    token = loaded_client.post("/api/student/join", json={"team": "第1組"}).json()["token"]
    with loaded_client.websocket_connect(f"/ws?role=student&token={token}") as ws:
        student = ws.receive_json()["view"]
    assert student["mode"] == {"key": "accuracy", "label": "只計對錯", "sequential": False}


def test_classic_score_label(loaded_client, teacher_headers):
    view = loaded_client.get("/api/teacher/state", headers=teacher_headers).json()
    assert view["mode"]["key"] == "classic" and view["score_label"] == "得題數"


def test_unknown_mode_422(loaded_client, teacher_headers):
    r = loaded_client.post("/api/teacher/mode", json={"mode": "nope"}, headers=teacher_headers)
    assert r.status_code == 422


def test_mode_only_in_preparing(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    r = loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    assert r.status_code == 409
    assert loaded_client.app.state.activity.mode.key == "classic"


def test_reset_keeps_mode(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    loaded_client.post("/api/teacher/reveal", headers=teacher_headers)
    assert loaded_client.post("/api/teacher/reset", headers=teacher_headers).status_code == 200
    assert loaded_client.app.state.activity.mode.key == "accuracy"


def test_mode_requires_teacher(loaded_client):
    assert loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"}).status_code == 401
    assert loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"},
                              headers={"X-Teacher-Key": TEACHER_KEY + "x"}).status_code == 401
