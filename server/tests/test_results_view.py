"""作答狀況與結果（results-view D1–D3）。"""
import json

from conftest import TEACHER_KEY


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    body = {"question": question, "answers": answers}
    return client.post("/api/student/submit", json=body, headers={"X-Team-Token": token})


def test_teacher_board_live(loaded_client, teacher_headers):
    t1, t2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    with loaded_client.websocket_connect(f"/ws?role=teacher&key={TEACHER_KEY}") as wt:
        wt.receive_json()
        submit(loaded_client, t2, 3, ["位址"])
        board = wt.receive_json()["view"]["board"]
        q3 = next(b for b in board if b["number"] == 3)
        assert q3["winner"] == {"team": "第2組", "answers": ["位址"]}
        submit(loaded_client, t1, 3, ["地址"])
        view = wt.receive_json()["view"]
    q3 = next(b for b in view["board"] if b["number"] == 3)
    ranking = [(r["team"], r["rank"], r["is_winner"]) for r in q3["ranking"]]
    assert ranking == [("第2組", 1, True), ("第1組", 2, False)]
    assert view["team_scores"] == {"第1組": 0, "第2組": 1, "第3組": 0, "第4組": 0}


def test_student_results_only_when_ended(loaded_client, teacher_headers):
    t1, t2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    submit(loaded_client, t1, 1, ["CPU", "作業系統"])
    with loaded_client.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        during = ws.receive_json()["view"]
        loaded_client.post("/api/teacher/end", headers=teacher_headers)
        after = ws.receive_json()["view"]
    assert "results" not in during and "team_scores" not in during
    q1 = next(r for r in after["results"] if r["number"] == 1)
    assert q1["winner"] == {"team": "第1組", "answers": ["CPU", "作業系統"]}
    assert after["team_scores"]["第1組"] == 1


def test_teacher_and_student_agree(loaded_client, teacher_headers):
    t1, t2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    submit(loaded_client, t1, 3, ["甲"])
    submit(loaded_client, t2, 3, ["乙"])
    submit(loaded_client, t2, 4, ["丙"])
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    teacher = loaded_client.get("/api/teacher/state", headers=teacher_headers).json()
    with loaded_client.websocket_connect(f"/ws?role=student&token={t1}") as ws:
        student = ws.receive_json()["view"]
    assert json.dumps(teacher["board"], sort_keys=True) == json.dumps(student["results"], sort_keys=True)
    assert teacher["team_scores"] == student["team_scores"]


def test_teacher_board_empty_before_import(client, teacher_headers):
    view = client.get("/api/teacher/state", headers=teacher_headers).json()
    assert view["board"] == [] and view["team_scores"] == {f"第{i}組": 0 for i in range(1, 5)}
