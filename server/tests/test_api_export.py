"""匯出端點（guided-notes-export D3、D4）。"""
import io
from urllib.parse import quote

import openpyxl

from quiz_server.guided_notes import parse_workbook


def join(client, team: str) -> str:
    return client.post("/api/student/join", json={"team": team}).json()["token"]


def submit(client, token: str, question: int, answers: list[str]):
    body = {"question": question, "answers": answers}
    return client.post("/api/student/submit", json=body, headers={"X-Team-Token": token})


def test_export_writes_winners(loaded_client, teacher_headers, fixture_bytes):
    t1, t2 = join(loaded_client, "第1組"), join(loaded_client, "第2組")
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    submit(loaded_client, t2, 3, ["一"])
    submit(loaded_client, t1, 3, ["零"])
    submit(loaded_client, t1, 1, ["CPU", "作業系統"])
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    r = loaded_client.get("/api/teacher/export", headers=teacher_headers)
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("application/vnd.openxmlformats-officedocument")
    notes = parse_workbook(fixture_bytes("group.xlsx"))
    ws = openpyxl.load_workbook(io.BytesIO(r.content))["學習單"]
    q1, q3 = notes.questions[0], notes.questions[2]
    assert [ws[s.cell].value for s in q1.slots] == ["（1）CPU", "（2）作業系統"]
    assert ws[q3.slots[0].cell].value == "一"  # 第2組先送出
    assert ws[notes.questions[3].slots[0].cell].value is None


def test_filename_header(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    r = loaded_client.get("/api/teacher/export", headers=teacher_headers)
    assert f"filename*=UTF-8''{quote('group-搶答結果.xlsx')}" in r.headers["content-disposition"]


def test_export_only_when_ended(loaded_client, teacher_headers):
    assert loaded_client.get("/api/teacher/export", headers=teacher_headers).status_code == 409
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    assert loaded_client.get("/api/teacher/export", headers=teacher_headers).status_code == 409


def test_export_requires_teacher(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    assert loaded_client.get("/api/teacher/export").status_code == 401


def test_export_can_repeat(loaded_client, teacher_headers):
    loaded_client.post("/api/teacher/start", headers=teacher_headers)
    loaded_client.post("/api/teacher/end", headers=teacher_headers)
    a = loaded_client.get("/api/teacher/export", headers=teacher_headers)
    b = loaded_client.get("/api/teacher/export", headers=teacher_headers)
    assert a.status_code == b.status_code == 200


def test_accuracy_exports_earliest_correct(loaded_client, teacher_headers):
    """只計對錯：寫回最早送出的**正確**答案；全錯的題目不寫（game-mode-framework D2）。"""
    c = loaded_client
    c.post("/api/teacher/mode", json={"mode": "accuracy"}, headers=teacher_headers)
    t1, t2 = join(c, "第1組"), join(c, "第2組")
    c.post("/api/teacher/start", headers=teacher_headers)
    submit(c, t1, 3, ["地址"])
    submit(c, t2, 3, ["位址"])
    submit(c, t1, 4, ["錯的"])
    c.post("/api/teacher/end", headers=teacher_headers)
    for q, team, ok in ((3, "第1組", False), (3, "第2組", True), (4, "第1組", False)):
        c.post("/api/teacher/judge", json={"question": q, "team": team, "correct": ok},
               headers=teacher_headers)
    assert c.get("/api/teacher/export", headers=teacher_headers).status_code == 409  # 判定中不可匯出
    c.post("/api/teacher/reveal", headers=teacher_headers)
    r = c.get("/api/teacher/export", headers=teacher_headers)
    ws = openpyxl.load_workbook(io.BytesIO(r.content))["學習單"]
    original = openpyxl.load_workbook(io.BytesIO(fixture_bytes_group()))["學習單"]
    assert ws["G11"].value.endswith("位址")
    assert ws["G13"].value == original["G13"].value


def fixture_bytes_group() -> bytes:
    from conftest import FIXTURES
    return (FIXTURES / "group.xlsx").read_bytes()
