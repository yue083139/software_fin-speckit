"""組隊：開關、邀請碼加入、代表作答、組內草稿（team-mode D1–D5）。"""
import asyncio

import pytest

from quiz_server import results
from quiz_server.activity import MAX_DEVICES, Activity, AlreadySubmittedError, InviteCodeError, TeamTakenError
from quiz_server.phases import PhaseError


def run(coro):
    return asyncio.run(coro)


def join(client, team: str, code: str | None = None):
    body = {"team": team} if code is None else {"team": team, "code": code}
    return client.post("/api/student/join", json=body)


def draft(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/draft", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def team_on(client, headers):
    r = client.post("/api/teacher/team-play", json={"enabled": True}, headers=headers)
    assert r.status_code == 200, r.text
    return r


def state(client, headers):
    return client.get("/api/teacher/state", headers=headers).json()


# ---- D1 開關 ----
def test_toggle_only_when_preparing(loaded_client, teacher_headers):
    c = loaded_client
    assert c.post("/api/teacher/team-play", json={"enabled": True}).status_code == 401
    assert c.post("/api/teacher/team-play", json={"enabled": "x"}, headers=teacher_headers).status_code == 422
    team_on(c, teacher_headers)
    assert state(c, teacher_headers)["team_play"] is True
    assert c.get("/api/public/info").json()["team_play"] is True
    c.post("/api/teacher/start", headers=teacher_headers)
    r = c.post("/api/teacher/team-play", json={"enabled": False}, headers=teacher_headers)
    assert r.status_code == 409
    assert state(c, teacher_headers)["team_play"] is True


def test_toggle_revokes_only_on_change(loaded_client, teacher_headers):
    c = loaded_client
    t1 = join(c, "第1組").json()["token"]
    team_on(c, teacher_headers)
    act = c.app.state.activity
    assert act.team_of(t1) is None  # 值改變 ⇒ 撤銷
    t2 = join(c, "第1組").json()["token"]
    code = state(c, teacher_headers)["invite_codes"]["第1組"]
    team_on(c, teacher_headers)  # 值不變 ⇒ 不撤銷
    assert act.team_of(t2) == "第1組"
    assert state(c, teacher_headers)["invite_codes"]["第1組"] == code
    c.post("/api/teacher/team-play", json={"enabled": False}, headers=teacher_headers)
    assert act.team_of(t2) is None
    assert state(c, teacher_headers)["invite_codes"] == {}


def test_reset_keeps_team_play(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    c.post("/api/teacher/start", headers=teacher_headers)
    c.post("/api/teacher/end", headers=teacher_headers)
    c.post("/api/teacher/reset", headers=teacher_headers)
    assert state(c, teacher_headers)["team_play"] is True


def test_configure_teams_clears_codes(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    join(c, "第1組")
    c.post("/api/teacher/teams", json={"count": 3}, headers=teacher_headers)
    s = state(c, teacher_headers)
    assert s["invite_codes"] == {} and s["devices"] == {t: 0 for t in s["teams"]}


@pytest.mark.parametrize("key", ["classic", "accuracy", "timed"])
def test_team_play_does_not_change_scoring(fixture_bytes, key):
    async def play(team_play: bool):
        a = Activity(wall=lambda: 1_700_000_000.0)
        await a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx")
        await a.set_mode(key)
        if team_play:
            await a.set_team_play(True)
        await a.start()
        if key == "timed":
            await a.open_next()
            await a.submit("第2組", 1, ["甲", "乙"])
            await a.submit("第1組", 1, ["丙", "丁"])
            await a.close_question()
            await a.judge(1, "第2組", True)
            await a.judge(1, "第1組", False)
            await a.reveal_question()
        else:
            await a.submit("第2組", 3, ["甲"])
            await a.submit("第1組", 3, ["乙"])
            await a.submit("第1組", 4, ["丙"])
            await a.end()
            if a.mode.judged:
                for n, t, ok in ((3, "第2組", False), (3, "第1組", True), (4, "第1組", True)):
                    await a.judge(n, t, ok)
                await a.reveal()
        rows = results.build(a)
        if a._timer is not None:
            a._timer.cancel()
        # 時間計分的分數取決於真實時鐘的作答毫秒，只比順位與判定；其餘模式連分數一起比
        timed = key == "timed"
        return ([[(r["team"], r["rank"], None if timed else r["score"], r.get("correct"))
                  for r in q["ranking"]] for q in rows],
                None if timed else results.team_scores(a))

    assert run(play(False)) == run(play(True))


# ---- D2 邀請碼 ----
def test_join_requires_code(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    a = join(c, "第1組")
    assert a.status_code == 200
    code = state(c, teacher_headers)["invite_codes"]["第1組"]
    assert len(code) == 6
    for bad in (None, "", "ZZZZZZ", code[:5]):
        r = join(c, "第1組", bad)
        assert r.status_code == 403 and r.json()["detail"] == "邀請碼不正確"
        assert "token" not in r.text
    assert state(c, teacher_headers)["devices"]["第1組"] == 1
    assert join(c, "第1組", f"  {code.lower()} ").status_code == 200
    assert state(c, teacher_headers)["devices"]["第1組"] == 2
    # 別組的邀請碼不能拿來加入本組
    join(c, "第2組")
    other = state(c, teacher_headers)["invite_codes"]["第2組"]
    if other != code:
        assert join(c, "第1組", other).status_code == 403


def test_single_device_without_team_play_unchanged(loaded_client):
    assert join(loaded_client, "第1組").status_code == 200
    r = join(loaded_client, "第1組", "ANYCODE")
    assert r.status_code == 409


def test_device_limit(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    join(c, "第1組")
    code = state(c, teacher_headers)["invite_codes"]["第1組"]
    for _ in range(MAX_DEVICES - 1):
        assert join(c, "第1組", code).status_code == 200
    r = join(c, "第1組", code)
    assert r.status_code == 409 and "最多 6 台" in r.json()["detail"]
    # 沒有正確邀請碼的人不該知道已滿：先比對邀請碼
    assert join(c, "第1組", "WRONG1").status_code == 403


@pytest.mark.parametrize("existing,expected", [(MAX_DEVICES, 0), (MAX_DEVICES - 1, 1)])
def test_concurrent_join_at_limit(existing, expected):
    async def go():
        a = Activity()
        await a.set_team_play(True)
        await a.join("第1組")
        code = a.invite_code("第1組")
        for _ in range(existing - 1):
            await a.join("第1組", code)
        res = await asyncio.gather(*(a.join("第1組", code) for _ in range(5)), return_exceptions=True)
        return a, res

    a, res = run(go())
    assert sum(isinstance(r, str) for r in res) == expected
    assert all(isinstance(r, (str, TeamTakenError)) for r in res)
    assert a.devices("第1組") == MAX_DEVICES


def test_concurrent_first_join_one_code():
    async def go():
        a = Activity()
        await a.set_team_play(True)
        res = await asyncio.gather(*(a.join("第1組") for _ in range(5)), return_exceptions=True)
        return a, res

    a, res = run(go())
    # 並發的第一台：恰一台成為第一台，其餘因沒有邀請碼被拒
    assert sum(isinstance(r, str) for r in res) == 1
    assert sum(isinstance(r, InviteCodeError) for r in res) == 4


def test_release_revokes_all_devices_and_code(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    tokens = [join(c, "第1組").json()["token"]]
    old = state(c, teacher_headers)["invite_codes"]["第1組"]
    tokens += [join(c, "第1組", old).json()["token"] for _ in range(2)]
    assert c.post("/api/teacher/release", json={"team": "第1組"}, headers=teacher_headers).status_code == 200
    act = c.app.state.activity
    assert all(act.team_of(t) is None for t in tokens)
    s = state(c, teacher_headers)
    assert s["devices"]["第1組"] == 0 and "第1組" not in s["joined"]
    new = s["invite_codes"]["第1組"]  # 釋放即換新碼，只在老師畫面
    assert new != old  # 換新（撞碼機率約 10⁻⁹）
    # 被踢的人不能搶先以「第一台」重新佔住：不帶碼、帶舊碼都 403
    assert join(c, "第1組").status_code == 403
    assert join(c, "第1組", old).status_code == 403
    assert join(c, "第1組", new).status_code == 200
    assert state(c, teacher_headers)["invite_codes"]["第1組"] == new


def test_fullwidth_code_accepted(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    join(c, "第1組")
    code = state(c, teacher_headers)["invite_codes"]["第1組"]
    wide = "".join(chr(ord(ch) + 0xFEE0) for ch in code)  # 半形轉全形
    assert join(c, "第1組", wide).status_code == 200
    r = join(c, "第1組", "邀請碼錯")
    assert r.status_code == 403


# ---- D3 代表作答 ----
def test_concurrent_submit_same_team(fixture_bytes):
    async def go():
        a = Activity()
        await a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx")
        await a.set_team_play(True)
        await a.join("第1組")
        code = a.invite_code("第1組")
        tokens = [await a.join("第1組", code) for _ in range(2)]
        assert {a.team_of(t) for t in tokens} == {"第1組"}
        await a.start()
        outcomes = []
        for q in (3, 4):
            res = await asyncio.gather(*(a.submit("第1組", q, [f"答{i}"]) for i in range(20)),
                                       return_exceptions=True)
            outcomes.append(res)
        return a, outcomes

    a, outcomes = run(go())
    for res in outcomes:
        assert sum(not isinstance(r, Exception) for r in res) == 1
        assert all(isinstance(r, AlreadySubmittedError) for r in res if isinstance(r, Exception))
    seqs = [s.seq for subs in a.submissions.values() for s in subs]
    assert len(seqs) == len(set(seqs)) == 2


def test_member_sees_team_submission(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    ta = join(c, "第1組").json()["token"]
    tb = join(c, "第1組", state(c, teacher_headers)["invite_codes"]["第1組"]).json()["token"]
    c.post("/api/teacher/start", headers=teacher_headers)
    with c.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        wb.receive_json()
        assert submit(c, ta, 3, ["甲"]).status_code == 200
        view = wb.receive_json()["view"]
    assert view["my_submissions"] == [{"question": 3, "answers": ["甲"]}]
    r = submit(c, tb, 3, ["乙"])
    assert r.status_code == 409 and r.json()["detail"] == "本組已送出這一題，不可修改"


# ---- D4 草稿 ----
def test_draft_rules(loaded_client, teacher_headers):
    c = loaded_client
    t0 = join(c, "第3組").json()["token"]
    c.post("/api/teacher/start", headers=teacher_headers)
    r = draft(c, t0, 3, ["x"])
    assert r.status_code == 409 and r.json()["detail"] == "只有組隊模式可以共用草稿"
    c.post("/api/teacher/end", headers=teacher_headers)
    c.post("/api/teacher/reset", headers=teacher_headers)
    team_on(c, teacher_headers)
    ta = join(c, "第1組").json()["token"]
    tb = join(c, "第1組", state(c, teacher_headers)["invite_codes"]["第1組"]).json()["token"]
    assert draft(c, ta, 3, ["x"]).status_code == 409  # 準備中
    assert draft(c, "forged", 3, ["x"]).status_code == 403
    c.post("/api/teacher/start", headers=teacher_headers)
    assert draft(c, ta, 99, ["x"]).status_code == 404
    for bad in (["a"], ["a" * 201, "b"], ["a\x07", "b"]):
        r = draft(c, ta, 1, bad)
        assert r.status_code == 422 and "a" * 50 not in r.text and "\x07" not in r.text
    r = draft(c, ta, 1, ["草稿一", ""])
    assert r.status_code == 200 and r.json() == {"question": 1}
    act = c.app.state.activity
    from quiz_server.views import student_view
    assert student_view(act, "第1組")["drafts"] == [{"question": 1, "answers": ["草稿一", ""]}]
    assert draft(c, tb, 1, ["草稿二", "乙"]).status_code == 200  # 最後寫入者為準
    assert student_view(act, "第1組")["drafts"] == [{"question": 1, "answers": ["草稿二", "乙"]}]
    assert submit(c, tb, 1, ["定稿", "乙"]).status_code == 200
    assert student_view(act, "第1組")["drafts"] == []  # 送出清除
    r = draft(c, ta, 1, ["再改", "x"])
    assert r.status_code == 409 and r.json()["detail"] == "本組已送出這一題，不可修改"


def test_draft_cleared_on_release_and_reset(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    ta = join(c, "第1組").json()["token"]
    c.post("/api/teacher/start", headers=teacher_headers)
    draft(c, ta, 3, ["草稿"])
    act = c.app.state.activity
    assert act.drafts.get("第1組")
    c.post("/api/teacher/release", json={"team": "第1組"}, headers=teacher_headers)
    assert not act.drafts.get("第1組")
    ta = join(c, "第1組", state(c, teacher_headers)["invite_codes"]["第1組"]).json()["token"]
    draft(c, ta, 3, ["草稿"])
    c.post("/api/teacher/end", headers=teacher_headers)
    c.post("/api/teacher/reset", headers=teacher_headers)
    assert act.drafts == {}


def test_draft_timed_only_open_question(fixture_bytes):
    async def go():
        a = Activity(wall=lambda: 1_700_000_000.0)
        await a.load_questions(fixture_bytes("group.xlsx"), "group.xlsx")
        await a.set_mode("timed")
        await a.set_team_play(True)
        await a.join("第1組")
        await a.start()
        with pytest.raises(PhaseError, match="這一題目前沒有開放作答"):
            await a.set_draft("第1組", 1, ["a", "b"])
        await a.open_next()
        await a.set_draft("第1組", 1, ["a", "b"])
        with pytest.raises(PhaseError, match="這一題目前沒有開放作答"):
            await a.set_draft("第1組", 2, ["a", "b"])
        await a.close_question()
        with pytest.raises(PhaseError, match="這一題目前沒有開放作答"):
            await a.set_draft("第1組", 1, ["a", "b"])
        a._timer and a._timer.cancel()

    run(go())


def test_teacher_view_has_no_drafts(loaded_client, teacher_headers):
    c = loaded_client
    team_on(c, teacher_headers)
    ta = join(c, "第1組").json()["token"]
    c.post("/api/teacher/start", headers=teacher_headers)
    draft(c, ta, 3, ["老師不該看到的草稿"])
    assert "老師不該看到的草稿" not in c.get("/api/teacher/state", headers=teacher_headers).text


# ---- v1.1：邀請碼只在準備階段給學生，開始搶答即換新 ----
def test_code_rotates_on_start_and_hidden_from_students(loaded_client, teacher_headers):
    from quiz_server.views import student_view
    c = loaded_client
    team_on(c, teacher_headers)
    join(c, "第1組")
    act = c.app.state.activity
    old = state(c, teacher_headers)["invite_codes"]["第1組"]
    assert student_view(act, "第1組")["invite_code"] == old
    c.post("/api/teacher/start", headers=teacher_headers)
    new = state(c, teacher_headers)["invite_codes"]["第1組"]
    view = student_view(act, "第1組")
    assert "invite_code" not in view and new not in str(view) and old not in str(view)
    assert new != old  # 換新（32⁶ 種，撞碼機率約 10⁻⁹）
    assert join(c, "第1組", old).status_code == 403  # 準備階段被瞄到的碼失效
    assert join(c, "第1組", new).status_code == 200  # 搶答中向老師索取的新碼可用
