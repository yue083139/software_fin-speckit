"""Guided Notes 解析（guided-notes-import D1–D4）：三份版面不同的夾具＋四種錯誤。"""
import io

import openpyxl
import pytest

from quiz_server.guided_notes import GuidedNotesError, parse_workbook


def _cells(notes):
    return [[(s.sheet, s.cell) for s in q.slots] for q in notes.questions]


def test_single_template(fixture_bytes):
    notes = parse_workbook(fixture_bytes("single.xlsx"))
    assert [q.number for q in notes.questions] == [1, 2, 3, 4, 5, 6]
    assert [len(q.slots) for q in notes.questions] == [1] * 6
    # 作答格位置來自解析：題號列的作答欄（合併範圍左上角）
    assert _cells(notes) == [[("學習單", f"G{r}")] for r in (5, 7, 9, 11, 13, 15)]


def test_group_template(fixture_bytes):
    notes = parse_workbook(fixture_bytes("group.xlsx"))
    assert [q.number for q in notes.questions] == [1, 2, 3, 4]
    assert [len(q.slots) for q in notes.questions] == [2, 2, 1, 1]
    assert _cells(notes)[0] == [("學習單", "G5"), ("學習單", "G6")]
    assert [s.label for s in notes.questions[0].slots] == ["（1）", "（2）"]
    assert notes.questions[0].is_group and not notes.questions[2].is_group


def test_variant_layout(fixture_bytes):
    notes = parse_workbook(fixture_bytes("variant.xlsx"))
    assert notes.sheet == "第二份學習單"
    assert [q.number for q in notes.questions] == [1, 2, 3, 4, 5]
    assert [len(q.slots) for q in notes.questions] == [1, 3, 1, 2, 1]
    assert _cells(notes) == [
        [("第二份學習單", "H9")],
        [("第二份學習單", "H11"), ("第二份學習單", "H12"), ("第二份學習單", "H13")],
        [("第二份學習單", "H15")],
        [("第二份學習單", "H17"), ("第二份學習單", "H18")],
        [("第二份學習單", "H20")],
    ]
    first = notes.questions[0].slots[0]
    assert first.placeholder is True
    assert [s.display for s in notes.questions[1].slots] == ["(a)", "(b)", "(c)"]


def _book(rows: dict[str, object], merges: tuple[str, ...] = ()) -> bytes:
    wb = openpyxl.Workbook()
    ws = wb.active
    for coord, value in rows.items():
        ws[coord] = value
    for m in merges:
        ws.merge_cells(m)
    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


def test_header_aliases_must_match_whole_cell():
    data = _book({"A1": "題號說明", "B1": "作答區域", "A2": 1})
    with pytest.raises(GuidedNotesError, match="找不到同時含題號與作答欄的表頭列"):
        parse_workbook(data)


def test_no_numbers():
    with pytest.raises(GuidedNotesError, match="找不到題號"):
        parse_workbook(_book({"A1": "題號", "B1": "作答", "A2": "備註"}))


def test_duplicate_numbers():
    with pytest.raises(GuidedNotesError, match="題號重複：2"):
        parse_workbook(_book({"A1": "題號", "B1": "作答", "A2": 1, "A3": 2, "A4": 2}))


def test_question_without_answer_cell():
    # 第 1 題的作答欄被一個跨越題號欄的合併範圍吃掉 ⇒ 沒有作答格
    data = _book({"A1": "題號", "B1": "作答", "A2": 1, "A3": 2}, merges=("A2:B2",))
    with pytest.raises(GuidedNotesError, match="第 1 題找不到作答格"):
        parse_workbook(data)


def test_not_xlsx():
    with pytest.raises(GuidedNotesError, match="不是有效的 xlsx"):
        parse_workbook(b"not a workbook")


def test_fullwidth_and_english_aliases():
    notes = parse_workbook(_book({"B3": "Ｎｏ.", "D3": "Answer", "B4": "１", "B5": 2}))
    assert [q.number for q in notes.questions] == [1, 2]
    assert _cells(notes) == [[("Sheet", "D4")], [("Sheet", "D5")]]


def test_reference_column(fixture_bytes):
    """可選參考答案欄（game-mode-framework D4）：表頭「題號／題目／作答／參考答案」。"""
    notes = parse_workbook(fixture_bytes("reference.xlsx"))
    assert [len(q.slots) for q in notes.questions] == [1, 2, 1, 1]
    assert [[s.reference for s in q.slots] for q in notes.questions] == [
        ["CPU"], ["二進位", "0"], [None], ["Linux"]]
    assert _cells(notes) == [[("學習單", "F4")], [("學習單", "F5"), ("學習單", "F6")],
                             [("學習單", "F7")], [("學習單", "F8")]]


@pytest.mark.parametrize("name", ["single.xlsx", "group.xlsx", "variant.xlsx"])
def test_templates_have_no_reference(fixture_bytes, name):
    notes = parse_workbook(fixture_bytes(name))
    assert all(s.reference is None for q in notes.questions for s in q.slots)
