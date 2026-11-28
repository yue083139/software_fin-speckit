"""送出規則與並發順位（buzz-answering D1、D4、D5）。"""
import asyncio

import pytest

from quiz_server.activity import Activity, AlreadySubmittedError, AnswerError
from quiz_server.phases import PhaseError


def join(client, team: str) -> dict[str, str]:
    return {"X-Team-Token": client.post("/api/student/join", json={"team": team}).json()["token"]}


def submit(client, headers, question: int, answers: list[str]):
    body = {"question": question, "answers": answers}
    return client.post("/api/student/submit", json=body, headers=headers)


@pytest.fixture
def answering(loaded_client, teacher_headers):
    h1, h2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    assert loaded_client.post("/api/teacher/start", headers=teacher_headers).status_code == 200
    return loaded_client, h1, h2


def test_submit_before_start_is_409(loaded_client):
    h = join(loaded_client, "第1組")
    assert submit(loaded_client, h, 3, ["位址"]).status_code == 409


def test_first_submitter_wins(answering, teacher_headers):
    client, h1, h2 = answering
    assert submit(client, h2, 3, ["二"]).status_code == 200
    assert submit(client, h1, 3, ["一"]).status_code == 200
    ranking = client.get("/api/teacher/state", headers=teacher_headers).json()
    assert ranking["phase"] == "answering"
    act = client.app.state.activity
    ranked = act.rule.rank(act.submissions[3])
    assert [(r.team, r.rank) for r in ranked] == [("第2組", 1), ("第1組", 2)]


def test_duplicate_submit_is_409_and_keeps_first(answering):
    client, h1, _ = answering
    assert submit(client, h1, 3, ["第一次"]).status_code == 200
    r = submit(client, h1, 3, ["第二次"])
    assert r.status_code == 409
    assert client.app.state.activity.submissions[3][0].answers == ("第一次",)


def test_group_requires_all_slots(answering):
    client, h1, _ = answering
    assert submit(client, h1, 1, ["CPU"]).status_code == 422
    assert submit(client, h1, 1, ["CPU", "作業系統"]).status_code == 200


@pytest.mark.parametrize("answers", [["   "], ["a\x01b"], ["x" * 201]])
def test_invalid_answers_are_422(answering, answers):
    client, h1, _ = answering
    r = submit(client, h1, 3, answers)
    assert r.status_code == 422
    assert client.app.state.activity.submissions[3] == []


def test_answer_is_trimmed(answering):
    client, h1, _ = answering
    assert submit(client, h1, 3, ["  位址  "]).json() == {"question": 3, "answers": ["位址"]}


@pytest.mark.parametrize("headers", [{}, {"X-Team-Token": "forged"}])
def test_bad_token_is_403(answering, headers):
    client, _, _ = answering
    assert submit(client, headers, 3, ["x"]).status_code == 403


def test_unknown_question_is_404(answering):
    client, h1, _ = answering
    assert submit(client, h1, 99, ["x"]).status_code == 404


def test_submit_after_end_rejected(answering, teacher_headers):
    client, h1, _ = answering
    client.post("/api/teacher/end", headers=teacher_headers)
    assert submit(client, h1, 3, ["x"]).status_code == 409


def test_reset_clears_submissions(answering, teacher_headers):
    client, h1, _ = answering
    submit(client, h1, 3, ["x"])
    client.post("/api/teacher/end", headers=teacher_headers)
    client.post("/api/teacher/reset", headers=teacher_headers)
    assert client.app.state.activity.submissions[3] == []


def _started(fixture_bytes) -> Activity:
    a = Activity()
    asyncio.run(a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx"))
    asyncio.run(a.start())
    return a


def test_concurrent_same_question(fixture_bytes):
    teams = ["第1組", "第2組", "第3組", "第4組"]
    for _ in range(50):
        a = _started(fixture_bytes)

        async def go(act=a):
            return await asyncio.gather(*(act.submit(t, 3, [t]) for t in teams))

        subs = asyncio.run(go())
        seqs = sorted(s.seq for s in subs)
        assert seqs == [1, 2, 3, 4]
        ranked = a.rule.rank(a.submissions[3])
        assert sum(r.is_winner for r in ranked) == 1


def test_50_teams_concurrent_same_question_20_times(fixture_bytes):
    teams = [f"第{i}組" for i in range(1, 51)]
    for _ in range(20):
        a = Activity(team_count=50)
        asyncio.run(a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx"))
        asyncio.run(a.start())

        async def go(act=a):
            return await asyncio.gather(*(act.submit(team, 3, [team]) for team in teams))

        submissions = asyncio.run(go())
        assert sorted(item.seq for item in submissions) == list(range(1, 51))
        ranked = a.rule.rank(a.submissions[3])
        assert sum(item.is_winner for item in ranked) == 1


def test_concurrent_same_team_same_question(fixture_bytes):
    a = _started(fixture_bytes)

    async def go():
        return await asyncio.gather(*(a.submit("第1組", 3, [str(i)]) for i in range(10)),
                                    return_exceptions=True)

    results = asyncio.run(go())
    assert sum(not isinstance(r, Exception) for r in results) == 1
    assert all(isinstance(r, AlreadySubmittedError) for r in results if isinstance(r, Exception))
    assert len(a.submissions[3]) == 1


def test_activity_level_errors(fixture_bytes):
    a = Activity()
    asyncio.run(a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx"))
    with pytest.raises(PhaseError):
        asyncio.run(a.submit("第1組", 3, ["x"]))
    asyncio.run(a.start())
    with pytest.raises(AnswerError):
        asyncio.run(a.submit("第1組", 1, ["只有一個"]))
