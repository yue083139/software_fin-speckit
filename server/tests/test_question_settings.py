"""題目設定：雙倍分數題（question-settings D2、D3）。"""
import json

import pytest


def setq(client, headers, question: int, multiplier):
    body = {"question": question, "multiplier": multiplier}
    return client.post("/api/teacher/question-settings", json=body, headers=headers)


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def multipliers(view) -> dict[int, int]:
    return {q["number"]: q["multiplier"] for q in view["questions"]}


def test_set_double(loaded_client, teacher_headers):
    r = setq(loaded_client, teacher_headers, 3, 2)
    assert r.status_code == 200 and r.json() == {"question": 3, "multiplier": 2, "time_limit": 20}
    view = loaded_client.get("/api/teacher/state", headers=teacher_headers).json()
    assert multipliers(view) == {1: 1, 2: 1, 3: 2, 4: 1}


@pytest.mark.parametrize("value", [0, 3, -1])
def test_bad_multiplier_422(loaded_client, teacher_headers, value):
    assert setq(loaded_client, teacher_headers, 3, value).status_code == 422


def test_errors(loaded_client, teacher_headers):
    assert setq(loaded_client, teacher_headers, 99, 2).status_code == 404
    no_key = loaded_client.post("/api/teacher/question-settings", json={"question": 3, "multiplier": 2})
    assert no_key.status_code == 401
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    assert setq(loaded_client, teacher_headers, 3, 2).status_code == 409
    assert loaded_client.app.state.activity.attrs_of(3).multiplier == 1


def test_reimport_clears_and_reset_keeps(loaded_client, teacher_headers, fixture_bytes):
    setq(loaded_client, teacher_headers, 3, 2)
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    loaded_client.post("/api/teacher/reset", headers=teacher_headers)
    act = loaded_client.app.state.activity
    assert act.attrs_of(3).multiplier == 2  # 重置保留
    upload = {"file": ("group.xlsx", fixture_bytes("group.xlsx"), "application/octet-stream")}
    loaded_client.post("/api/teacher/import", headers=teacher_headers, files=upload)
    assert all(act.attrs_of(q.number).multiplier == 1 for q in act.questions)  # 重新匯入清除


def test_student_sees_multiplier(loaded_client, teacher_headers):
    setq(loaded_client, teacher_headers, 3, 2)
    token = join(loaded_client, "第1組")
    with loaded_client.websocket_connect(f"/ws?role=student&token={token}") as ws:
        view = ws.receive_json()["view"]
    assert multipliers(view)[3] == 2


def test_score_label(loaded_client, teacher_headers):
    def label() -> str:
        return loaded_client.get("/api/teacher/state", headers=teacher_headers).json()["score_label"]
    assert label() == "得題數"
    setq(loaded_client, teacher_headers, 3, 2)
    assert label() == "得分"
    setq(loaded_client, teacher_headers, 3, 1)
    assert label() == "得題數"
    loaded_client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    assert label() == "得分"


def test_double_question_scores_two(loaded_client, teacher_headers):
    setq(loaded_client, teacher_headers, 3, 2)
    t1, t2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    submit(loaded_client, t1, 3, ["位址"])
    submit(loaded_client, t2, 3, ["地址"])
    submit(loaded_client, t2, 4, ["堆疊"])
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    with loaded_client.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        view = ws.receive_json()["view"]
    assert view["team_scores"]["第1組"] == 2 and view["team_scores"]["第2組"] == 1
    q3 = next(r for r in view["results"] if r["number"] == 3)
    assert q3["multiplier"] == 2 and q3["winner"]["team"] == "第1組"
    assert view["score_label"] == "得分"
    # 倍率不改變隔離：結束前 B 組 payload 不含 A 組答案（既有負例照舊）
    assert "results" in view and json.dumps(view, ensure_ascii=False).count("位址") >= 1
