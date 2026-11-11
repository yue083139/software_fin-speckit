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
