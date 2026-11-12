"""判定階段與參考答案建議（game-mode-framework D3、D4、D7）。"""
import asyncio

import pytest

from quiz_server.guided_notes import Slot
from quiz_server.judging import suggest
from quiz_server.phases import Phase


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def judge(client, headers, question: int, team: str, correct: bool):
    return client.post("/api/teacher/judge", json={"question": question, "team": team, "correct": correct},
                       headers=headers)


@pytest.fixture
def accuracy(loaded_client, teacher_headers):
    """只計對錯模式、兩組各送出第 3 題、第1組另送第 4 題，已結束進入判定。"""
    c = loaded_client
    assert c.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers).status_code == 200
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    c.post("/api/teacher/start", headers=teacher_headers)
    assert submit(c, t1, 3, ["地址"]).status_code == 200
    assert submit(c, t2, 3, ["位址"]).status_code == 200
    assert submit(c, t1, 4, ["作業系統"]).status_code == 200
    r = c.post("/api/teacher/end", headers=teacher_headers)
    assert r.status_code == 200 and r.json() == {"phase": "judging"}
    return c


def test_classic_end_goes_to_ended(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    assert loaded_client.post("/api/teacher/end", headers=teacher_headers).json() == {"phase": "ended"}


def test_reveal_blocked_until_all_judged(accuracy, teacher_headers):
    c = accuracy
    assert judge(c, teacher_headers, 3, "第1組", False).status_code == 200
    assert judge(c, teacher_headers, 3, "第2組", True).status_code == 200
    r = c.post("/api/teacher/reveal", headers=teacher_headers)
    assert r.status_code == 409 and "1 筆" in r.json()["detail"]
    assert c.get("/api/teacher/state", headers=teacher_headers).json()["pending_judgments"] == 1
    assert judge(c, teacher_headers, 4, "第1組", True).status_code == 200
    assert c.post("/api/teacher/reveal", headers=teacher_headers).json() == {"phase": "ended"}


def test_end_during_judging_is_409(accuracy, teacher_headers):
    r = accuracy.post("/api/teacher/end", headers=teacher_headers)
    assert r.status_code == 409
    assert accuracy.app.state.activity.phase is Phase.JUDGING


def test_judge_errors(accuracy, loaded_client, teacher_headers):
    c = accuracy
    assert judge(c, teacher_headers, 3, "第3組", True).status_code == 404  # 該組沒送出
    assert judge(c, teacher_headers, 99, "第1組", True).status_code == 404
    body = {"question": 3, "team": "第1組", "correct": True}
    assert c.post("/api/teacher/judge", json=body).status_code == 401
    assert c.post("/api/teacher/judge", json={"question": 3, "team": "第1組"},
                  headers=teacher_headers).status_code == 422


def test_judge_outside_judging_is_409(loaded_client, teacher_headers):
    c = loaded_client
    t1 = join(c, "第1組")
    c.post("/api/teacher/start", headers=teacher_headers)
    submit(c, t1, 3, ["甲"])
    assert judge(c, teacher_headers, 3, "第1組", True).status_code == 409
    assert c.post("/api/teacher/accept-suggestions", headers=teacher_headers).status_code == 409
    assert c.post("/api/teacher/reveal", headers=teacher_headers).status_code == 409


def test_rejudge_overrides_and_scores(accuracy, teacher_headers):
    c = accuracy
    judge(c, teacher_headers, 3, "第1組", True)
    judge(c, teacher_headers, 3, "第1組", False)
    judge(c, teacher_headers, 3, "第2組", True)
    judge(c, teacher_headers, 4, "第1組", True)
    c.post("/api/teacher/reveal", headers=teacher_headers)
    view = c.get("/api/teacher/state", headers=teacher_headers).json()
    q3 = next(b for b in view["board"] if b["number"] == 3)
    assert q3["winner"] == {"team": "第2組", "answers": ["位址"]}
    assert [(r["team"], r["rank"], r["correct"], r["score"]) for r in q3["ranking"]] == [
        ("第1組", 1, False, 0), ("第2組", 2, True, 1)]
    assert view["team_scores"]["第1組"] == 1 and view["team_scores"]["第2組"] == 1


def test_submit_rejected_in_judging(accuracy):
    t3 = join(accuracy, "第3組")
    assert submit(accuracy, t3, 3, ["晚到"]).status_code == 409


def test_concurrent_judge_and_accept_suggestions(fixture_bytes):
    """老師判定與「採用全部建議」並發：老師的判定不得被建議覆蓋。

    拿掉鎖時，accept_suggestions 在讀出「未判定清單」與寫入之間讓出，老師的判定先寫入、再被建議蓋掉。
    """
    from quiz_server.activity import Activity

    async def one_round() -> bool | None:
        a = Activity()
        await a.load_questions(fixture_bytes("reference.xlsx"), "reference.xlsx")
        await a.set_mode("accuracy")
        await a.start()
        await a.submit("第1組", 1, ["GPU"])  # 參考答案 CPU ⇒ 建議錯誤
        await a.end()
        await asyncio.gather(a.judge(1, "第1組", True), a.accept_suggestions())
        return a.judgments[1]["第1組"]

    for _ in range(20):
        assert asyncio.run(one_round()) is True


def _slots(*refs):
    return tuple(Slot("s", f"A{i}", "", False, "", ref) for i, ref in enumerate(refs, 1))


@pytest.mark.parametrize(("answers", "refs", "expected"), [
    (("CPU",), ("CPU",), True),
    (("ｃｐｕ",), ("CPU",), True),            # 全形與大小寫
    ((" C P U ",), ("CPU",), True),           # 空白
    (("GPU",), ("CPU",), False),
    (("二進位", "1"), ("二進位", "0"), False),  # 題組一格不同
    (("二進位", "0"), ("二進位", "0"), True),
    (("甲",), (None,), None),                  # 缺參考答案
    (("甲", "乙"), ("甲", None), None),
])
def test_suggest(answers, refs, expected):
    assert suggest(answers, _slots(*refs)) is expected


def test_accept_suggestions_fills_only_unjudged(client, teacher_headers, fixture_bytes):
    c = client
    c.post("/api/teacher/import", headers=teacher_headers,
           files={"file": ("reference.xlsx", fixture_bytes("reference.xlsx"), "application/octet-stream")})
    c.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    c.post("/api/teacher/start", headers=teacher_headers)
    submit(c, t1, 1, ["cpu"])      # 建議正確
    submit(c, t2, 1, ["GPU"])      # 建議錯誤，但老師先判正確
    submit(c, t1, 3, ["記事本"])   # 第 3 題無參考答案 ⇒ 無建議
    c.post("/api/teacher/end", headers=teacher_headers)
    judge(c, teacher_headers, 1, "第2組", True)
    teacher = c.get("/api/teacher/state", headers=teacher_headers).json()
    q1 = next(b for b in teacher["board"] if b["number"] == 1)
    assert q1["reference"] == ["CPU"]
    assert {r["team"]: r["suggestion"] for r in q1["ranking"]} == {"第1組": True, "第2組": False}
    r = c.post("/api/teacher/accept-suggestions", headers=teacher_headers)
    assert r.json() == {"applied": 1}
    act = c.app.state.activity
    assert act.judgments[1] == {"第1組": True, "第2組": True}
    assert act.pending_judgments() == 1  # 第 3 題仍待判
