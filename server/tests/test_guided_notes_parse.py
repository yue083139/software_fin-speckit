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
    # guided-notes-sheets-sync D5：作答表頭 G4:H4 橫跨兩欄、子題 G 欄為標籤、H 欄空白 ⇒ H 欄為填空格
    assert _cells(notes)[0] == [("學習單", "H5"), ("學習單", "H6")]
    assert _cells(notes)[1] == [("學習單", "H8"), ("學習單", "H9")]
    assert _cells(notes)[2:] == [[("學習單", "G11")], [("學習單", "G13")]]
    assert [s.label for s in notes.questions[0].slots] == ["", ""]
    assert [s.display for s in notes.questions[0].slots] == ["（1）", "（2）"]
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


def test_d5_right_cell_must_be_inside_header_span():
    """作答表頭沒有橫向合併 ⇒ 標籤右側格不算填空格（不寫死欄位，只依表頭合併欄寬）。"""
    data = _book({"A1": "題號", "B1": "作答", "A2": 1, "B2": "（1）", "A3": None, "B3": "（2）"},
                 merges=("A2:A3",))
    notes = parse_workbook(data)
    assert [s.cell for s in notes.questions[0].slots] == ["B2", "B3"]


def test_d5_right_cell_with_content_is_not_blank():
    data = _book({"A1": "題號", "B1": "作答", "A2": 1, "B2": "（1）", "C2": "已填", "B3": "（2）"},
                 merges=("B1:C1", "A2:A3"))
    notes = parse_workbook(data)
    assert [s.cell for s in notes.questions[0].slots] == ["B2", "C3"]


# question-text D1：題目欄為可選欄，逐子題取所在列的敘述


def _prompts(notes):
    return [[s.prompt for s in q.slots] for q in notes.questions]


def test_prompts_single_template(fixture_bytes):
    notes = parse_workbook(fixture_bytes("single.xlsx"))
    prompts = _prompts(notes)
    assert [len(p) for p in prompts] == [1] * 6
    assert prompts[0][0].startswith("電腦系統中負責執行程式指令")
    assert all(p[0] for p in prompts)


def test_prompts_group_template_per_sub_row(fixture_bytes):
    notes = parse_workbook(fixture_bytes("group.xlsx"))
    prompts = _prompts(notes)
    assert prompts[0][0].startswith("根據文章第一段")
    assert prompts[0][1].startswith("而他安裝的 Windows")
    assert prompts[1][0].startswith("為了處理角色移動")
    assert prompts[1][1].startswith("而他用來實作")
    assert prompts[2][0].startswith("無論小明寫的高階語言")
    assert prompts[3][0].startswith("專案最後的連線失敗")


def test_prompts_variant_alias(fixture_bytes):
    notes = parse_workbook(fixture_bytes("variant.xlsx"))
    prompts = _prompts(notes)
    assert prompts[0] == ["先進先出的資料結構稱為什麼？"]
    assert all(all(p) for p in prompts)


def test_prompts_reference_template(fixture_bytes):
    notes = parse_workbook(fixture_bytes("reference.xlsx"))
    assert _prompts(notes)[1] == ["電腦內部使用哪一種進位系統？", "除了 1 之外，該系統還用哪個數字？"]


def test_no_question_column_still_imports():
    notes = parse_workbook(_book({"A1": "題號", "B1": "作答", "A2": 1, "A3": 2}))
    assert [q.number for q in notes.questions] == [1, 2]
    assert _prompts(notes) == [[""], [""]]


def test_group_prompt_merged_vertically_only_anchor():
    notes = parse_workbook(_book(
        {"A1": "題號", "B1": "題目", "C1": "作答", "A2": 1, "B2": "  共用敘述\n第二行  ", "C2": "（1）",
         "C3": "（2）", "A4": 2, "B4": 3.0},
        merges=("A2:A3", "B2:B3")))
    assert _prompts(notes) == [["共用敘述\n第二行", ""], ["3"]]


def test_prompts_do_not_change_writeback(fixture_bytes):
    from quiz_server.guided_notes import write_answers
    data = fixture_bytes("group.xlsx")
    notes = parse_workbook(data)
    out = openpyxl.load_workbook(io.BytesIO(write_answers(data, notes, {3: ("甲",)})))
    src = openpyxl.load_workbook(io.BytesIO(data))
    ws_o, ws_s = out.worksheets[0], src.worksheets[0]
    assert ws_o["C11"].value == ws_s["C11"].value  # 題目欄不被寫入
