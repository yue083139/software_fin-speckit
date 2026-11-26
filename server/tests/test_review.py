"""經典搶答結束後依順位檢查（answer-review D1–D5）。"""
import io
import json

import openpyxl
import pytest

from quiz_server.guided_notes import parse_workbook


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def review(client, headers, question: int, team: str, correct: bool):
    return client.post("/api/teacher/review", json={"question": question, "team": team, "correct": correct},
                       headers=headers)


def reset(client, headers, question: int):
    return client.post("/api/teacher/review-reset", json={"question": question}, headers=headers)


def _exported(client, headers):
    data = client.get("/api/teacher/export", headers=headers).content
    return openpyxl.load_workbook(io.BytesIO(data))["學習單"]


def board(client, headers, number: int) -> dict:
    view = client.get("/api/teacher/state", headers=headers).json()
    return next(q for q in view["board"] if q["number"] == number)


@pytest.fixture
def classic_ended(loaded_client, teacher_headers):
    """經典搶答：第 3 題依序第2組「一」、第1組「零」、第3組「二」；第1組另送第 4 題；已結束。"""
    c = loaded_client
    t1, t2, t3 = join(c, "第1組"), join(c, "第2組"), join(c, "第3組")
    c.post("/api/teacher/start", headers=teacher_headers)
    assert submit(c, t2, 3, ["一"]).status_code == 200
    assert submit(c, t1, 3, ["零"]).status_code == 200
    assert submit(c, t3, 3, ["二"]).status_code == 200
    assert submit(c, t1, 4, ["作業系統"]).status_code == 200
    assert c.post("/api/teacher/end", headers=teacher_headers).json() == {"phase": "ended"}
    c.tokens = {"第1組": t1, "第2組": t2, "第3組": t3}
    return c


def test_unreviewed_question_keeps_fastest(classic_ended, teacher_headers):
    q3 = board(classic_ended, teacher_headers, 3)
    assert q3["winner"]["team"] == "第2組"
    assert q3["review"] == {"candidate": "第2組", "rejected": [], "locked": False}


def test_reject_falls_back_to_next_rank(classic_ended, teacher_headers):
    c = classic_ended
    r = review(c, teacher_headers, 3, "第2組", False)
    assert r.status_code == 200 and r.json() == {"question": 3, "team": "第2組", "correct": False}
    q3 = board(c, teacher_headers, 3)
    assert q3["winner"] == {"team": "第1組", "answers": ["零"]}
    assert q3["review"] == {"candidate": "第1組", "rejected": ["第2組"], "locked": False}
    scores = c.get("/api/teacher/state", headers=teacher_headers).json()["team_scores"]
    assert scores["第1組"] == 2 and scores["第2組"] == 0


def test_correct_locks_and_blocks_further_review(classic_ended, teacher_headers):
    c = classic_ended
    review(c, teacher_headers, 3, "第2組", False)
    assert review(c, teacher_headers, 3, "第1組", True).status_code == 200
    assert board(c, teacher_headers, 3)["review"] == {"candidate": "第1組", "rejected": ["第2組"],
                                                      "locked": True}
    r = review(c, teacher_headers, 3, "第1組", False)
    assert r.status_code == 409 and r.json()["detail"] == "本題已鎖定，請先重設本題"


def test_double_click_does_not_skip_a_team(classic_ended, teacher_headers):
    c = classic_ended
    assert review(c, teacher_headers, 3, "第2組", False).status_code == 200
    r = review(c, teacher_headers, 3, "第2組", False)
    assert r.status_code == 409 and r.json()["detail"] == "這一組不是目前要檢查的答案，請重新整理"
    assert board(c, teacher_headers, 3)["review"]["candidate"] == "第1組"


def test_all_rejected_has_no_winner_and_export_keeps_original(classic_ended, teacher_headers, fixture_bytes):
    c = classic_ended
    for team in ("第2組", "第1組", "第3組"):
        assert review(c, teacher_headers, 3, team, False).status_code == 200
    q3 = board(c, teacher_headers, 3)
    assert q3["winner"] is None
    assert q3["review"] == {"candidate": None, "rejected": ["第2組", "第1組", "第3組"],
                            "locked": False}
    r = review(c, teacher_headers, 3, "第2組", True)
    assert r.status_code == 409 and r.json()["detail"] == "本題沒有可檢查的答案"
    notes = parse_workbook(fixture_bytes("group.xlsx"))
    ws = _exported(c, teacher_headers)
    assert ws[notes.questions[2].slots[0].cell].value is None


def test_export_writes_fallback_answer(classic_ended, teacher_headers, fixture_bytes):
    c = classic_ended
    review(c, teacher_headers, 3, "第2組", False)
    review(c, teacher_headers, 3, "第1組", True)
    notes = parse_workbook(fixture_bytes("group.xlsx"))
    ws = _exported(c, teacher_headers)
    assert ws[notes.questions[2].slots[0].cell].value == "零"


def test_reset_returns_to_rank_one(classic_ended, teacher_headers):
    c = classic_ended
    r = reset(c, teacher_headers, 3)
    assert r.status_code == 409 and r.json()["detail"] == "本題尚未檢查"
    review(c, teacher_headers, 3, "第2組", False)
    review(c, teacher_headers, 3, "第1組", True)
    assert reset(c, teacher_headers, 3).json() == {"question": 3}
    assert board(c, teacher_headers, 3)["review"] == {"candidate": "第2組", "rejected": [], "locked": False}


def test_no_submission_and_unknown_question(classic_ended, teacher_headers):
    r = review(classic_ended, teacher_headers, 1, "第1組", True)
    assert r.status_code == 409 and r.json()["detail"] == "本題沒有可檢查的答案"
    assert review(classic_ended, teacher_headers, 99, "第1組", True).status_code == 404
    assert reset(classic_ended, teacher_headers, 99).status_code == 404


def test_only_classic_and_only_ended(loaded_client, teacher_headers):
    c = loaded_client
    t1 = join(c, "第1組")
    c.post("/api/teacher/start", headers=teacher_headers)
    submit(c, t1, 3, ["一"])
    r = review(c, teacher_headers, 3, "第1組", True)
    assert r.status_code == 409 and r.json()["detail"] == "搶答結束後才能檢查"
    assert reset(c, teacher_headers, 3).json()["detail"] == "搶答結束後才能檢查"
    c.post("/api/teacher/end", headers=teacher_headers)
    c.post("/api/teacher/reset", headers=teacher_headers)
    c.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    c.post("/api/teacher/start", headers=teacher_headers)
    c.post("/api/teacher/end", headers=teacher_headers)
    r = review(c, teacher_headers, 3, "第1組", True)
    assert r.status_code == 409 and r.json()["detail"] == "只有經典搶答可以檢查"
    view = c.get("/api/teacher/state", headers=teacher_headers).json()
    assert all("review" not in q for q in view["board"])  # 非經典模式不帶檢查狀態


def test_error_order_401_then_422(classic_ended, teacher_headers):
    assert classic_ended.post("/api/teacher/review", json={"question": "x"}).status_code == 401
    r = classic_ended.post("/api/teacher/review", json={"question": "x"}, headers=teacher_headers)
    assert r.status_code == 422
    r = classic_ended.post("/api/teacher/review-reset", json={}, headers=teacher_headers)
    assert r.status_code == 422


def test_successful_review_pushes_once_and_failures_push_nothing(classic_ended, teacher_headers):
    """D2：狀態有改變的成功操作恰推播一次；失敗不推播。
    學生 ended 看得到遞補後得主與 ✓／✗。"""
    c = classic_ended
    with c.websocket_connect(f"/ws?role=student&token={c.tokens['第3組']}") as ws:
        first = json.loads(ws.receive_text())
        assert review(c, teacher_headers, 3, "第1組", False).status_code == 409  # 非候選：不推播
        assert review(c, teacher_headers, 3, "第2組", False).status_code == 200
        second = json.loads(ws.receive_text())
        assert second["seq"] == first["seq"] + 1
        q3 = next(q for q in second["view"]["results"] if q["number"] == 3)
        assert q3["winner"]["team"] == "第1組"
        assert [(r["team"], r["correct"]) for r in q3["ranking"]] == [
            ("第2組", False), ("第1組", None), ("第3組", None)]
        assert "review" not in q3  # 檢查狀態只在老師 view
        assert reset(c, teacher_headers, 4).status_code == 409  # 未檢查的題重設：不推播
        assert review(c, teacher_headers, 3, "第1組", True).status_code == 200
        third = json.loads(ws.receive_text())
        assert third["seq"] == second["seq"] + 1


def test_reset_activity_clears_reviews(classic_ended, teacher_headers):
    c = classic_ended
    review(c, teacher_headers, 3, "第2組", False)
    c.post("/api/teacher/reset", headers=teacher_headers)
    assert c.app.state.activity.judgments == {q.number: {} for q in c.app.state.activity.questions}
