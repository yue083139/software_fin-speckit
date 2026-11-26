"""作答隔離負例（buzz-answering D3、D6；docs/discipline-precedents.md「作答隔離」）。

斷言的是**傳輸內容**（WebSocket 原始文字、REST 回應原文、日誌），不是畫面。
"""
import json
import logging

import pytest

from quiz_server.phases import Phase
from quiz_server.views import student_view

SECRET_A = "甲組祕密答案"
SECRET_A2 = "甲組子題祕密"


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/submit", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


@pytest.fixture
def two_teams(loaded_client, teacher_headers):
    ta, tb = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    return loaded_client, ta, tb


def test_websocket_and_rest_do_not_leak(two_teams, teacher_headers):
    client, ta, tb = two_teams
    with client.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        first = wb.receive_text()
        responses = []
        assert submit(client, ta, 3, [SECRET_A]).status_code == 200
        assert submit(client, ta, 1, [SECRET_A, SECRET_A2]).status_code == 200
        # B 組自己的各種回應（成功、重複、格式錯、憑證錯）
        responses.append(submit(client, tb, 3, ["乙組答案"]).text)
        responses.append(submit(client, tb, 3, ["再送一次"]).text)
        responses.append(submit(client, tb, 1, ["少一格"]).text)
        responses.append(client.post("/api/student/submit", json={"question": "x", "answers": [SECRET_A]},
                                     headers={"X-Team-Token": tb}).text)
        responses.append(submit(client, "forged", 4, [SECRET_A]).text)
        # B 組自己送出會讓 B 的 view 改變 ⇒ 收到一則；之後老師結束
        own_update = wb.receive_text()
        client.post("/api/teacher/end", headers=teacher_headers)
        ended = wb.receive_text()
    for raw in [first, own_update, *responses]:
        assert SECRET_A not in raw and SECRET_A2 not in raw
    # 結束後才揭曉
    assert SECRET_A in ended


def test_other_team_submit_sends_nothing(two_teams, teacher_headers):
    client, ta, tb = two_teams
    with client.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        before = json.loads(wb.receive_text())
        for q in (3, 4):
            assert submit(client, ta, q, [SECRET_A]).status_code == 200
        client.post("/api/teacher/end", headers=teacher_headers)
        after = json.loads(wb.receive_text())
    # 中間若有任何推播，seq 就會跳號，且下一則不會是 ended
    assert after["seq"] == before["seq"] + 1
    assert after["view"]["phase"] == "ended"


@pytest.mark.parametrize("query", ["/ws?role=student&team=第1組", "/ws?role=student&token=forged&team=第1組"])
def test_spoofed_team_param(two_teams, query):
    client, ta, _ = two_teams
    submit(client, ta, 3, [SECRET_A])
    with client.websocket_connect(query) as ws:
        raw = ws.receive_text()
    assert SECRET_A not in raw
    assert json.loads(raw)["view"]["team_valid"] is False


@pytest.mark.parametrize("phase", [Phase.PREPARING, Phase.ANSWERING, Phase.JUDGING])
def test_non_ended_phases_isolated(two_teams, phase):
    client, ta, _ = two_teams
    submit(client, ta, 3, [SECRET_A])
    act = client.app.state.activity
    act.phase = phase  # 直接設定：judging 尚無轉移入口，驗的是 view 的裁切規則
    view = student_view(act, "第2組")
    assert SECRET_A not in json.dumps(view, ensure_ascii=False)
    assert "results" not in view


def test_logs_do_not_contain_answers(two_teams, caplog):
    client, ta, _ = two_teams
    with caplog.at_level(logging.DEBUG):
        submit(client, ta, 3, [SECRET_A])
        submit(client, ta, 3, [SECRET_A])
    assert SECRET_A not in caplog.text
    assert "第1組" in caplog.text


def test_judging_hides_judgments(two_teams, teacher_headers):
    """判定中：老師判定第1組，第2組收到 0 則推播，view 不含第1組答案與判定結果（game-mode-framework D5）。"""
    client, ta, tb = two_teams
    act = client.app.state.activity
    # two_teams 已開始搶答；回到準備改模式需重置，故直接在此測試內重建流程
    client.post("/api/teacher/end", headers=teacher_headers)
    client.post("/api/teacher/reset", headers=teacher_headers)
    client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    client.post("/api/teacher/start", headers=teacher_headers)
    submit(client, ta, 3, [SECRET_A])
    submit(client, tb, 3, ["乙組答案"])
    client.post("/api/teacher/end", headers=teacher_headers)
    assert act.phase is Phase.JUDGING
    with client.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        before = json.loads(wb.receive_text())
        client.post("/api/teacher/judge", json={"question": 3, "team": "第1組", "correct": True},
                    headers=teacher_headers)
        client.post("/api/teacher/judge", json={"question": 3, "team": "第2組", "correct": False},
                    headers=teacher_headers)
        client.post("/api/teacher/reveal", headers=teacher_headers)
        after = json.loads(wb.receive_text())
    raw = json.dumps(before, ensure_ascii=False)
    assert SECRET_A not in raw and "correct" not in raw and "results" not in before["view"]
    assert after["seq"] == before["seq"] + 1 and after["view"]["phase"] == "ended"
    assert SECRET_A in json.dumps(after, ensure_ascii=False)


REFERENCES = ["CPU", "二進位", "Linux"]


def test_reference_never_sent_to_students(client, teacher_headers, fixture_bytes):
    """參考答案與建議在 preparing／answering／judging／ended 都不送往學生（game-mode-framework D5）。"""
    upload = {"file": ("reference.xlsx", fixture_bytes("reference.xlsx"), "application/octet-stream")}
    client.post("/api/teacher/import", headers=teacher_headers, files=upload)
    client.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    ta, tb = join(client, "第1組"), join(client, "第2組")
    seen: list[str] = []
    with client.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        seen.append(wb.receive_text())                                   # preparing
        client.post("/api/teacher/start", headers=teacher_headers)
        seen.append(wb.receive_text())                                   # answering
        seen.append(submit(client, ta, 1, ["cpu"]).text)
        seen.append(submit(client, tb, 1, ["gpu"]).text)
        seen.append(wb.receive_text())                                   # 本組送出後
        seen.append(submit(client, tb, 1, ["再送"]).text)               # 錯誤回應
        client.post("/api/teacher/end", headers=teacher_headers)
        seen.append(wb.receive_text())                                   # judging
        client.post("/api/teacher/accept-suggestions", headers=teacher_headers)
        client.post("/api/teacher/reveal", headers=teacher_headers)
        seen.append(wb.receive_text())                                   # ended
    seen.append(client.get("/api/public/info").text)
    assert json.loads(seen[-2])["view"]["phase"] == "ended"
    for raw in seen:
        assert "suggestion" not in raw and "reference" not in raw
        for ref in REFERENCES:
            # 學生答案「gpu」「cpu」可在 ended 出現；參考答案原文「CPU」等不得出現
            assert ref not in raw, (ref, raw[:200])
    teacher = client.get("/api/teacher/state", headers=teacher_headers).text
    assert "CPU" in teacher and "二進位" in teacher


# ---- 組隊（team-mode D5）：草稿與邀請碼只給本組 ----
SECRET_DRAFT = "甲組草稿祕密"


@pytest.fixture
def team_play(loaded_client, teacher_headers):
    c = loaded_client
    r = c.post("/api/teacher/team-play", json={"enabled": True}, headers=teacher_headers)
    assert r.status_code == 200
    ta, tb = join(c, "第1組"), join(c, "第2組")
    c.post("/api/teacher/start", headers=teacher_headers)
    # 開始搶答會換新邀請碼；取搶答中有效的那一個
    code_a = c.get("/api/teacher/state", headers=teacher_headers).json()["invite_codes"]["第1組"]
    return c, ta, tb, code_a


def draft(client, token: str, question: int, answers: list[str]):
    return client.post("/api/student/draft", json={"question": question, "answers": answers},
                       headers={"X-Team-Token": token})


def test_team_draft_isolated(team_play, teacher_headers):
    c, ta, tb, code_a = team_play
    seen = []
    with c.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        seen.append(wb.receive_text())
        assert draft(c, ta, 3, [SECRET_DRAFT]).status_code == 200
        # B 組自己的各種回應：成功、格式錯、已送出、憑證錯
        seen.append(draft(c, tb, 3, ["乙組草稿"]).text)
        seen.append(draft(c, tb, 1, [SECRET_DRAFT]).text)
        seen.append(draft(c, "forged", 3, [SECRET_DRAFT]).text)
        seen.append(wb.receive_text())  # B 自己的草稿改變 B 的 view
        seen.append(submit(c, tb, 3, ["乙組答案"]).text)
        seen.append(wb.receive_text())
        seen.append(c.get("/api/public/info").text)
        seen.append(c.post("/api/student/join", json={"team": "第1組"}).text)  # 無碼加入 A 組被拒
    for raw in seen:
        assert SECRET_DRAFT not in raw and code_a not in raw
    # 老師看得到邀請碼，看不到草稿
    teacher = c.get("/api/teacher/state", headers=teacher_headers).text
    assert code_a in teacher and SECRET_DRAFT not in teacher


def test_other_team_draft_sends_nothing(team_play, teacher_headers):
    c, ta, tb, _ = team_play
    with c.websocket_connect(f"/ws?role=student&token={tb}") as wb:
        before = json.loads(wb.receive_text())
        for i in range(3):
            assert draft(c, ta, 3, [f"{SECRET_DRAFT}{i}"]).status_code == 200
        c.post("/api/teacher/end", headers=teacher_headers)
        after = json.loads(wb.receive_text())
    assert after["seq"] == before["seq"] + 1
    assert after["view"]["phase"] == "ended"


@pytest.mark.parametrize("phase", [Phase.PREPARING, Phase.JUDGING, Phase.ENDED])
def test_drafts_only_in_answering(team_play, phase):
    c, ta, _, _ = team_play
    draft(c, ta, 3, [SECRET_DRAFT])
    act = c.app.state.activity
    act.phase = phase  # 直接設定，驗 view 的裁切規則
    view = student_view(act, "第1組")
    assert "drafts" not in view
    assert SECRET_DRAFT not in json.dumps(view, ensure_ascii=False)


def test_invalid_token_gets_no_team_fields(team_play):
    c, _, _, code_a = team_play
    with c.websocket_connect("/ws?role=student&token=forged") as ws:
        raw = ws.receive_text()
    view = json.loads(raw)["view"]
    assert set(view) == {"role", "phase", "team", "team_valid"}
    assert code_a not in raw


def test_invite_code_not_sent_to_students_while_answering(team_play, teacher_headers):
    c, ta, _, _ = team_play
    code_now = c.get("/api/teacher/state", headers=teacher_headers).json()["invite_codes"]["第1組"]
    with c.websocket_connect(f"/ws?role=student&token={ta}") as wa:
        raw = wa.receive_text()
    assert code_now not in raw and "invite_code" not in json.loads(raw)["view"]


def test_google_tokens_never_reach_students_or_logs(activity, fixture_bytes, caplog):
    """guided-notes-sheets-sync D6：登入到登出（撤銷失敗）全程，學生端與日誌不含任何憑證。"""
    from urllib.parse import parse_qs as _pq

    from conftest import TEACHER_KEY
    from fastapi.testclient import TestClient
    from google_fake import ACCESS, ACCESS2, CLIENT_ID, CLIENT_SECRET, CODE, REFRESH, FakeGoogle, sign_in

    from quiz_server.app import create_app
    from quiz_server.google_auth import GoogleSession

    clock = [1000.0]
    fake = FakeGoogle(fixture_bytes("group.xlsx"))
    fake.fail["revoke"] = 1
    session = GoogleSession(CLIENT_ID, CLIENT_SECRET, transport=fake.transport(), clock=lambda: clock[0])
    h = {"X-Teacher-Key": TEACHER_KEY}
    url = "https://docs.google.com/spreadsheets/d/" + "1" + "A" * 43 + "/edit"
    secrets_ = [ACCESS, ACCESS2, REFRESH, CLIENT_SECRET, CODE]
    caplog.set_level(logging.DEBUG)
    with TestClient(create_app(activity=activity, teacher_key=TEACHER_KEY, google=session)) as c:
        sign_in(c, h)
        assert c.post("/api/teacher/import-url", json={"url": url}, headers=h).status_code == 200
        ta = join(c, "第1組")
        tb = join(c, "第2組")
        with c.websocket_connect(f"/ws?role=student&token={tb}") as wb:
            raw = [wb.receive_text()]
            c.post("/api/teacher/start", headers=h)
            raw.append(wb.receive_text())
            own_a = submit(c, ta, 3, [SECRET_A]).text  # A 組自己的回應，不屬 B 組通道
            raw.append(submit(c, tb, 4, ["乙"]).text)
            raw.append(c.get("/api/public/info").text)
            clock[0] += 3600  # 觸發換新
            c.post("/api/teacher/end", headers=h)
            raw.append(wb.receive_text())
        assert c.post("/api/teacher/export-sheet", headers=h).status_code == 200
        c.post("/api/teacher/google/logout", headers=h)
        teacher_view = c.get("/api/teacher/state", headers=h).text
    blob = "\n".join(raw + [own_a])
    logs = "\n".join(r.getMessage() for r in caplog.records)
    assert SECRET_A not in "\n".join(raw[:4])  # 搶答中學生 B 的通道看不到 A 組答案
    for s in secrets_:
        assert s not in blob, s
        assert s not in logs, s
        assert s not in teacher_view, s
    assert _pq(fake.calls[-1].content.decode()).get("token") == [REFRESH]  # 撤銷失敗也有送出
