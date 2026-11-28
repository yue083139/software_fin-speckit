"""寫回原 Guided Notes（guided-notes-export D1、D2）：三份夾具往返比對。"""
import io

import openpyxl
import pytest

from quiz_server.guided_notes import parse_workbook, write_answers


def _load(data: bytes):
    return openpyxl.load_workbook(io.BytesIO(data))


def _snapshot(wb):
    values = {(ws.title, c.coordinate): c.value
              for ws in wb.worksheets for row in ws.iter_rows() for c in row if c.value is not None}
    merged = {ws.title: sorted(str(r) for r in ws.merged_cells.ranges) for ws in wb.worksheets}
    return values, merged


@pytest.mark.parametrize("name", ["single.xlsx", "group.xlsx", "variant.xlsx"])
def test_round_trip_preserves_other_cells(fixture_bytes, name):
    original = fixture_bytes(name)
    notes = parse_workbook(original)
    answers = {q.number: tuple(f"答{q.number}-{i}" for i in range(1, len(q.slots) + 1))
               for q in notes.questions}
    out = write_answers(original, notes, answers)
    before_values, before_merged = _snapshot(_load(original))
    after_wb = _load(out)
    after_values, after_merged = _snapshot(after_wb)
    slot_cells = {(s.sheet, s.cell) for q in notes.questions for s in q.slots}
    assert after_merged == before_merged
    for key, value in before_values.items():
        if key not in slot_cells:
            assert after_values.get(key) == value, key
    for q in notes.questions:
        for i, s in enumerate(q.slots, 1):
            assert f"答{q.number}-{i}" in after_wb[s.sheet][s.cell].value
    # 匯出檔再匯入，題目結構不變
    assert [len(q.slots) for q in parse_workbook(out).questions] == [len(q.slots) for q in notes.questions]


def test_group_keeps_labels(fixture_bytes):
    """guided-notes-sheets-sync D5：題組子題答案寫入標籤右側填空格，標籤格不動。"""
    original = fixture_bytes("group.xlsx")
    notes = parse_workbook(original)
    out = write_answers(original, notes, {1: ("CPU", "作業系統")})
    ws = _load(out)["學習單"]
    cells = [s.cell for s in notes.questions[0].slots]
    assert cells == ["H5", "H6"]
    assert [ws[c].value for c in cells] == ["CPU", "作業系統"]
    assert [ws["G5"].value, ws["G6"].value] == ["（1）", "（2）"]


def test_label_with_merged_answer_cell_keeps_append(fixture_bytes):
    """作答格本身為合併範圍（variant 子題）⇒ D5 不適用，維持接在標籤後。"""
    original = fixture_bytes("variant.xlsx")
    notes = parse_workbook(original)
    out = write_answers(original, notes, {2: ("前序", "中序", "後序")})
    q = notes.questions[1]
    ws = _load(out)[q.slots[0].sheet]
    assert [ws[s.cell].value for s in q.slots] == ["(a)前序", "(b)中序", "(c)後序"]


def test_placeholder_replaced(fixture_bytes):
    original = fixture_bytes("variant.xlsx")
    notes = parse_workbook(original)
    out = write_answers(original, notes, {1: ("佇列",)})
    slot = notes.questions[0].slots[0]
    value = _load(out)[slot.sheet][slot.cell].value
    assert value == "佇列" and "___" not in value


def test_unanswered_question_unchanged(fixture_bytes):
    original = fixture_bytes("single.xlsx")
    notes = parse_workbook(original)
    out = write_answers(original, notes, {3: ("位址",)})
    ws = _load(out)["學習單"]
    q3, q4 = notes.questions[2].slots[0], notes.questions[3].slots[0]
    assert ws[q3.cell].value == "位址"
    assert ws[q4.cell].value is None


def test_formula_like_answer_stays_text(fixture_bytes):
    original = fixture_bytes("single.xlsx")
    notes = parse_workbook(original)
    out = write_answers(original, notes, {1: ("=1+1",)})
    cell = _load(out)["學習單"][notes.questions[0].slots[0].cell]
    assert cell.value == "=1+1"
    assert cell.data_type == "s"
