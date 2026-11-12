"""時間計分：逐題開放、伺服器計時、判定與揭曉、名次（mode-timed-scoring D1–D6）。

以可注入的假時鐘驗證截止與作答毫秒；計時器以假的 sleep 驗證「提早醒來會再睡」。
"""
import asyncio
import json

import pytest
from conftest import TEACHER_KEY

from quiz_server.activity import Activity
from quiz_server.phases import Phase, PhaseError

SECRET_A = "甲組祕密答案"


class FakeClock:
    def __init__(self) -> None:
        self.t = 100.0

    def __call__(self) -> float:
        return self.t


async def never_sleep(_: float) -> None:
    await asyncio.Event().wait()  # 計時器在這些測試裡不觸發，由測試自己呼叫 close_due


async def timed_activity(fixture_bytes, clock, sleep=never_sleep, limit: int = 20) -> Activity:
    a = Activity(clock=clock, wall=lambda: 1_700_000_000.0, sleep=sleep)
    await a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx")  # 題 1、2 為題組，3、4 單題
    await a.set_mode("timed")
    for n in (1, 2, 3, 4):
        await a.set_question(n, time_limit=limit)
    await a.start()
    return a


def run(coro):
    return asyncio.run(coro)


def test_open_in_order_and_only_current_accepted(fixture_bytes):
    async def go():
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        with pytest.raises(PhaseError):
            await a.submit("第1組", 1, ["甲", "乙"])  # 尚未開題
        clock.t += 30  # 開始搶答與開題之間隔 30 秒：作答毫秒必須自開題起算，不是自開始搶答（實作輪紅隊）
        assert await a.open_next() == 1
        with pytest.raises(PhaseError):
            await a.open_next()  # 目前題未揭曉
        with pytest.raises(PhaseError, match="沒有開放"):
            await a.submit("第1組", 3, ["甲"])
        clock.t += 2.5
        sub = await a.submit("第1組", 1, ["甲", "乙"])
        assert sub.elapsed_ms == 2500  # 取自伺服器時鐘，自開題起算
        assert a.current.deadline_epoch_ms == (1_700_000_000 + 20) * 1000
    run(go())


def test_deadline_on_submit_path(fixture_bytes):
    """截止比對在送出路徑：時鐘已過時限、計時器尚未有機會執行時，送出仍被拒（計時器晚到不會多收）。"""
    async def go(offset: float):
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        await a.open_next()
        clock.t += offset  # 之後第一個讓出點就是送出本身，計時器還沒跑過
        return a, await a.submit("第1組", 1, ["甲", "乙"])

    _, sub = run(go(20.0))
    assert sub.elapsed_ms == 20000  # 剛好時限：收

    async def late():
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        await a.open_next()
        clock.t += 20.001
        with pytest.raises(PhaseError, match="時間已到"):
            await a.submit("第2組", 1, ["甲", "乙"])
        assert a.submissions[1] == [] and not a.current.closed
    run(late())


def test_close_due_only_after_deadline_and_not_on_all_submitted(fixture_bytes):
    async def go():
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        await a.open_next()
        for team in a.teams:
            await a.submit(team, 1, ["甲", "乙"])
        assert not a.current.closed  # 全員送出不提早關閉（作答隔離）
        clock.t += 19.999
        await a.close_due()
        assert not a.current.closed
        clock.t += 0.001
        version = a.version
        await a.close_due()
        assert a.current.closed and a.version == version + 1
    run(go())


def test_timer_retries_after_early_wake(fixture_bytes):
    """計時器提早醒來（尚差 3 毫秒）時必須再睡一次並關閉，不能就此結束（v1.1 紅隊：Windows 計時解析度）。"""
    clock = FakeClock()
    calls: list[float] = []

    async def early_sleep(seconds: float) -> None:
        calls.append(seconds)
        clock.t += seconds - 0.003 if len(calls) == 1 else seconds
        await asyncio.sleep(0)

    async def go():
        a = await timed_activity(fixture_bytes, clock, sleep=early_sleep, limit=5)
        await a.open_next()
        for _ in range(20):
            await asyncio.sleep(0)
            if a.current.closed:
                break
        assert a.current.closed
        assert len(calls) == 2 and calls[1] == pytest.approx(0.003)
    run(go())


def test_judge_and_reveal_preconditions(fixture_bytes):
    async def go():
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        await a.open_next()
        clock.t += 2
        await a.submit("第1組", 1, ["甲", "乙"])
        with pytest.raises(PhaseError):
            await a.judge(1, "第1組", True)  # 未關閉不可判
        with pytest.raises(PhaseError):
            await a.accept_suggestions()  # 開放中不可批次採用建議
        with pytest.raises(PhaseError):
            await a.reveal_question()
        await a.close_question()
        with pytest.raises(PhaseError, match="1 筆"):
            await a.reveal_question()
        with pytest.raises(PhaseError):
            await a.end()  # 未揭曉不可結束
        await a.judge(1, "第1組", True)
        assert await a.reveal_question() == 1
        with pytest.raises(PhaseError):
            await a.judge(1, "第1組", False)  # 已揭曉不可改判
        assert await a.open_next() == 2
        with pytest.raises(PhaseError):
            await a.end()
        await a.close_question()
        await a.reveal_question()  # 無人作答：沒有未判定
        await a.end()
        assert a.phase is Phase.ENDED
    run(go())


def test_open_next_rejected_outside_sequential(fixture_bytes):
    async def go():
        a = Activity()
        await a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx")
        await a.start()
        with pytest.raises(PhaseError, match="不逐題"):
            await a.open_next()
    run(go())


def test_all_opened(fixture_bytes):
    async def go():
        a = await timed_activity(fixture_bytes, FakeClock())
        for _ in range(4):
            await a.open_next()
            await a.close_question()
            await a.reveal_question()
        with pytest.raises(PhaseError, match="都已開放"):
            await a.open_next()
    run(go())


def test_concurrent_close_and_submit(fixture_bytes):
    """老師提早結束與送出並發：先開始的關閉生效後，送出不得被收（拿掉鎖時送出會在關閉之後被記錄）。"""
    async def one_round() -> int:
        clock = FakeClock()
        a = await timed_activity(fixture_bytes, clock)
        await a.open_next()
        clock.t += 1
        results = await asyncio.gather(a.close_question(), a.submit("第1組", 1, ["甲", "乙"]),
                                       return_exceptions=True)
        assert results[0] == 1
        return len(a.submissions[1])

    for _ in range(20):
        assert run(one_round()) == 0


# ---- API 與 view ----
@pytest.fixture
def timed(fixture_bytes, teacher_headers):
    from fastapi.testclient import TestClient

    from quiz_server.app import create_app
    clock = FakeClock()
    act = Activity(clock=clock, wall=lambda: 1_700_000_000.0, sleep=never_sleep)
    with TestClient(create_app(activity=act, teacher_key=TEACHER_KEY)) as c:
        c.post("/api/teacher/import", headers=teacher_headers,
               files={"file": ("group.xlsx", fixture_bytes("group.xlsx"), "application/octet-stream")})
        c.post("/api/teacher/mode", json={"mode": "timed"}, headers=teacher_headers)
        c.post("/api/teacher/question-settings", json={"question": 3, "time_limit": 30},
               headers=teacher_headers)
        yield c, clock


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def post(client, path: str, headers, body=None):
    return client.post(f"/api/teacher/{path}", json=body, headers=headers)


def advance_to_question_3(client, headers):
    """題 1、2 開放後直接關閉並揭曉（無人作答），再開題 3。"""
    for _ in range(2):
        post(client, "open-next", headers)
        post(client, "close-question", headers)
        post(client, "reveal-question", headers)
    assert post(client, "open-next", headers).json() == {"question": 3}


def test_api_round_flow_and_scores(timed, teacher_headers):
    c, clock = timed
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    assert post(c, "open-next", teacher_headers).status_code == 409  # 尚未開始
    post(c, "start", teacher_headers)
    advance_to_question_3(c, teacher_headers)
    view = c.get("/api/teacher/state", headers=teacher_headers).json()
    assert view["mode"]["sequential"] is True
    assert view["round"] == {"question": 3, "state": "open", "deadline_epoch_ms": (1_700_000_000 + 30) * 1000}
    clock.t += 2
    assert submit(c, t1, 3, ["位址"]).status_code == 200
    clock.t += 3
    assert submit(c, t2, 3, ["地址"]).status_code == 200
    assert submit(c, t2, 4, ["堆疊"]).status_code == 409
    assert post(c, "close-question", teacher_headers).json() == {"question": 3}
    assert post(c, "close-question", teacher_headers).status_code == 409
    post(c, "judge", teacher_headers, {"question": 3, "team": "第1組", "correct": True})
    post(c, "judge", teacher_headers, {"question": 3, "team": "第2組", "correct": False})
    assert post(c, "reveal-question", teacher_headers).json() == {"question": 3}
    view = c.get("/api/teacher/state", headers=teacher_headers).json()
    assert view["round"] is None
    assert view["leaderboard"][:2] == [{"team": "第1組", "rank": 1, "score": 967},
                                       {"team": "第2組", "rank": 2, "score": 0}]
    with c.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        student = ws.receive_json()["view"]
    assert student["revealed"][-1] == {"question": 3, "submitted": True, "correct": False, "score": 0}
    assert student["my_total"] == 0
    assert all(set(row) == {"team", "rank"} for row in student["leaderboard"])
    assert student["leaderboard"][0] == {"team": "第1組", "rank": 1}
    assert {r["rank"] for r in student["leaderboard"][1:]} == {2}  # 同分同名次
    assert "results" not in student and "team_scores" not in student


def test_time_limit_settings(timed, teacher_headers):
    c, _ = timed
    body = {"question": 3}
    assert post(c, "question-settings", teacher_headers, body).status_code == 422  # 一欄都沒有
    for bad in (4, 121):
        r = post(c, "question-settings", teacher_headers, {"question": 3, "time_limit": bad})
        assert r.status_code == 422
    r = post(c, "question-settings", teacher_headers, {"question": 3, "multiplier": 2})
    assert r.json() == {"question": 3, "multiplier": 2, "time_limit": 30}  # 只給倍率，時限不動
    r = post(c, "question-settings", teacher_headers, {"question": 3, "time_limit": 5})
    assert r.json() == {"question": 3, "multiplier": 2, "time_limit": 5}


def test_leaderboard_counts_revealed_only(timed, teacher_headers):
    c, clock = timed
    t1 = join(c, "第1組")
    post(c, "start", teacher_headers)
    advance_to_question_3(c, teacher_headers)
    clock.t += 1
    submit(c, t1, 3, ["位址"])
    post(c, "close-question", teacher_headers)
    post(c, "judge", teacher_headers, {"question": 3, "team": "第1組", "correct": True})
    with c.websocket_connect(f"/ws?role=student&token={t1}") as ws:
        before = ws.receive_json()["view"]
        post(c, "reveal-question", teacher_headers)
        after = ws.receive_json()["view"]
    assert before["my_total"] == 0 and all(r["rank"] == 1 for r in before["leaderboard"])
    assert after["my_total"] > 0 and after["leaderboard"][0] == {"team": "第1組", "rank": 1}


def test_student_leaderboard_has_no_scores(timed, teacher_headers):
    c, clock = timed
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    post(c, "start", teacher_headers)
    advance_to_question_3(c, teacher_headers)
    clock.t += 1
    submit(c, t1, 3, ["位址"])
    post(c, "close-question", teacher_headers)
    post(c, "judge", teacher_headers, {"question": 3, "team": "第1組", "correct": True})
    post(c, "reveal-question", teacher_headers)
    with c.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        view = ws.receive_json()["view"]
    assert all(set(row) == {"team", "rank"} for row in view["leaderboard"])
    assert "team_scores" not in view and "results" not in view
    assert all(r.get("question") is not None for r in view["revealed"])  # 只有本組的逐題結果


@pytest.mark.parametrize("state", ["open", "closed", "revealed"])
def test_timed_mode_isolated(timed, teacher_headers, state):
    c, clock = timed
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    post(c, "start", teacher_headers)
    advance_to_question_3(c, teacher_headers)
    clock.t += 1
    assert submit(c, t1, 3, [SECRET_A]).status_code == 200
    if state in ("closed", "revealed"):
        post(c, "close-question", teacher_headers)
        post(c, "judge", teacher_headers, {"question": 3, "team": "第1組", "correct": True})
    if state == "revealed":
        post(c, "reveal-question", teacher_headers)
    with c.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        raw = ws.receive_text()
    responses = [submit(c, t2, 3, ["乙"]).text, submit(c, t2, 4, ["乙"]).text]
    for text in [raw, *responses]:
        assert SECRET_A not in text
    view = json.loads(raw)["view"]
    assert "results" not in view and "team_scores" not in view


def test_timed_other_team_submit_sends_nothing(timed, teacher_headers):
    c, clock = timed
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    post(c, "start", teacher_headers)
    advance_to_question_3(c, teacher_headers)
    with c.websocket_connect(f"/ws?role=student&token={t2}") as ws:
        before = ws.receive_json()
        clock.t += 1
        submit(c, t1, 3, [SECRET_A])
        post(c, "close-question", teacher_headers)
        after = ws.receive_json()
    assert after["seq"] == before["seq"] + 1 and after["view"]["round"]["state"] == "closed"


def test_reset_clears_rounds_and_timer(timed, teacher_headers):
    """時間計分跑完→結束→重置：回合與計時器清空，可再從第 1 題開始（實作輪紅隊）。"""
    c, _ = timed
    post(c, "start", teacher_headers)
    for _ in range(4):
        post(c, "open-next", teacher_headers)
        post(c, "close-question", teacher_headers)
        post(c, "reveal-question", teacher_headers)
    assert post(c, "end", teacher_headers).json() == {"phase": "ended"}
    assert post(c, "reset", teacher_headers).status_code == 200
    act = c.app.state.activity
    assert act.rounds == {} and act._timer is None
    post(c, "start", teacher_headers)
    assert post(c, "open-next", teacher_headers).json() == {"question": 1}
    post(c, "close-question", teacher_headers)
