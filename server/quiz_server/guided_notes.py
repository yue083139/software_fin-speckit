"""Guided Notes 解析與寫回。

解析：guided-notes-import D1–D4、guided-notes-sheets-sync D2、D5；寫回：guided-notes-export D1、D2。

定位只依表頭文字與合併範圍；本模組不含任何寫死的儲存格座標。
解析器只讀 `Grid` 介面：xlsx（openpyxl）與 Google Sheets 格狀資料各有一個實作，兩條路徑同一口徑。
"""
import io
import re
import unicodedata
from collections.abc import Sequence
from dataclasses import dataclass, replace
from typing import Protocol

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet

NUMBER_ALIASES = ("題號", "編號", "題次", "no", "no.", "#")
ANSWER_ALIASES = ("作答", "答案", "回答", "answer")
# 可選欄（game-mode-framework D4）：只產生判定建議；不含「答案」以免與作答欄別名衝突
REFERENCE_ALIASES = ("參考答案", "正確答案", "標準答案", "解答", "answerkey")
# 可選欄（question-text D1）：題目敘述只給學生看，不參與定位與寫回
QUESTION_ALIASES = ("題目", "題目敘述", "問題", "題幹", "question")
HEADER_SCAN_ROWS = 50
PLACEHOLDER = re.compile(r"[_＿]{3,}")
NUMBER_TEXT = re.compile(r"^(\d+)[.、]?$")


class GuidedNotesError(ValueError):
    """檔案不符合 Guided Notes 格式；API 層轉成 400，活動狀態不變。"""


@dataclass(frozen=True)
class Range:
    """合併範圍（1 起算，含兩端）。"""
    min_row: int
    min_col: int
    max_row: int
    max_col: int


class Grid(Protocol):
    """解析器需要的最小工作表介面（guided-notes-sheets-sync D2）。"""
    title: str
    max_row: int
    max_column: int
    merges: Sequence[Range]

    def cell(self, row: int, col: int) -> object: ...


class OpenpyxlGrid:
    def __init__(self, ws: Worksheet) -> None:
        self._ws = ws
        self.title = ws.title
        self.max_row = ws.max_row
        self.max_column = ws.max_column
        self.merges = [Range(r.min_row, r.min_col, r.max_row, r.max_col) for r in ws.merged_cells.ranges]

    def cell(self, row: int, col: int) -> object:
        return self._ws.cell(row, col).value


@dataclass(frozen=True)
class Slot:
    sheet: str
    cell: str
    label: str  # 作答格原有文字（如「（1）」或佔位符原文），寫回時保留；D5 右側填空格為 ""
    placeholder: bool
    display: str  # 給學生看的子題標籤
    reference: str | None = None  # 同列參考答案欄的值；只供老師與判定建議，永不送往學生
    prompt: str = ""  # 同列題目欄的敘述（question-text D1）；學生何時看得到由 views 決定


@dataclass(frozen=True)
class Question:
    number: int
    slots: tuple[Slot, ...]

    @property
    def is_group(self) -> bool:
        return len(self.slots) > 1


@dataclass(frozen=True)
class ParsedNotes:
    sheet: str
    questions: tuple[Question, ...]


def _norm(value: object) -> str:
    return "".join(unicodedata.normalize("NFKC", str(value)).split()).lower()


def _merged_index(grid: Grid) -> dict[tuple[int, int], Range]:
    index: dict[tuple[int, int], Range] = {}
    for rng in grid.merges:
        for row in range(rng.min_row, rng.max_row + 1):
            for col in range(rng.min_col, rng.max_col + 1):
                index[(row, col)] = rng
    return index


Header = tuple[int, int, int, int | None, int | None]  # 表頭列、題號欄、作答欄、參考答案欄、題目欄


def _find_header(grid: Grid, merged: dict) -> Header | None:
    for row in range(1, min(grid.max_row, HEADER_SCAN_ROWS) + 1):
        number_col = answer_col = reference_col = question_col = None
        for col in range(1, grid.max_column + 1):
            value = grid.cell(row, col)
            if value is None:
                continue
            text = _norm(value)
            if number_col is None and text in NUMBER_ALIASES:
                number_col = col
            elif answer_col is None and text in ANSWER_ALIASES:
                rng = merged.get((row, col))
                answer_col = rng.min_col if rng else col
            elif reference_col is None and text in REFERENCE_ALIASES:
                rng = merged.get((row, col))
                reference_col = rng.min_col if rng else col
            elif question_col is None and text in QUESTION_ALIASES:
                rng = merged.get((row, col))
                question_col = rng.min_col if rng else col
        if number_col is not None and answer_col is not None:
            return row, number_col, answer_col, reference_col, question_col
    return None


def _reference(grid: Grid, merged: dict, row: int, col: int | None) -> str | None:
    if col is None:
        return None
    rng = merged.get((row, col))
    if rng is not None and rng.min_row != row:
        return None  # 縱向合併的非錨點列：參考答案只屬於錨點列的子題
    value = grid.cell(row, rng.min_col if rng else col)
    text = "" if value is None else str(value).strip()
    return text or None


def _prompt(grid: Grid, merged: dict, row: int, col: int | None) -> str:
    """D1：該列題目欄的敘述；縱向合併的非錨點列為空，避免同一段敘述在題組每個子題重複。"""
    if col is None:
        return ""
    rng = merged.get((row, col))
    if rng is not None and rng.min_row != row:
        return ""
    value = grid.cell(row, rng.min_col if rng else col)
    if value is None or isinstance(value, bool):
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def _as_number(value: object) -> int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value if value > 0 else None
    if isinstance(value, float):
        return int(value) if value.is_integer() and value > 0 else None
    if isinstance(value, str):
        m = NUMBER_TEXT.match(_norm(value))
        return int(m.group(1)) if m and int(m.group(1)) > 0 else None
    return None


def _display(label: str, placeholder: bool, index: int, group: bool) -> str:
    text = PLACEHOLDER.sub("", label).strip() if placeholder else label.strip()
    if text:
        return text
    return f"({index})" if group else ""


def parse_workbook(data: bytes) -> ParsedNotes:
    try:
        wb = openpyxl.load_workbook(io.BytesIO(data))
    except Exception as exc:  # openpyxl 對壞檔會拋多種例外，一律視為格式錯誤
        raise GuidedNotesError("不是有效的 xlsx 檔") from exc
    return parse_grids([OpenpyxlGrid(ws) for ws in wb.worksheets])


def parse_grids(grids: Sequence[Grid]) -> ParsedNotes:
    """取第一個找得到表頭列的工作表解析。"""
    for grid in grids:
        merged = _merged_index(grid)
        header = _find_header(grid, merged)
        if header is not None:
            return _parse_sheet(grid, merged, header)
    raise GuidedNotesError(
        "找不到同時含題號與作答欄的表頭列（題號欄可用名稱："
        + "、".join(NUMBER_ALIASES) + "；作答欄可用名稱：" + "、".join(ANSWER_ALIASES) + "）"
    )


def _blank_fill_cell(grid: Grid, merged: dict, header_answer: Range | None,
                     anchor: tuple[int, int], label: str) -> tuple[int, int] | None:
    """D5：標籤格右側、仍在作答表頭合併欄寬內、空白且不屬合併範圍的格即填空格。"""
    if header_answer is None or not label.strip() or PLACEHOLDER.search(label):
        return None
    if merged.get(anchor) is not None:
        return None
    right = (anchor[0], anchor[1] + 1)
    if right[1] > header_answer.max_col or merged.get(right) is not None:
        return None
    value = grid.cell(*right)
    if value is not None and str(value).strip():
        return None
    return right


def _parse_sheet(grid: Grid, merged: dict, header: Header) -> ParsedNotes:
    header_row, number_col, answer_col, reference_col, question_col = header
    header_answer = merged.get((header_row, answer_col))
    # (座標, 寫回保留的標籤, 是否佔位符, 參考答案, 顯示用標籤, 題目敘述)
    raw: list[tuple[int, list[tuple[str, str, bool, str | None, str, str]]]] = []
    for row in range(header_row + 1, grid.max_row + 1):
        rng = merged.get((row, number_col))
        if rng is not None and (rng.min_row, rng.min_col) != (row, number_col):
            continue  # 合併範圍的非左上角格：屬於上一題或分隔列
        number = _as_number(grid.cell(row, number_col))
        if number is None:
            continue
        rows = range(rng.min_row, rng.max_row + 1) if rng else range(row, row + 1)
        slots: list[tuple[str, str, bool, str | None, str, str]] = []
        seen: set[tuple[int, int]] = set()
        for r in rows:
            arng = merged.get((r, answer_col))
            anchor = (arng.min_row, arng.min_col) if arng else (r, answer_col)
            if anchor in seen:
                continue
            if arng is not None and arng.min_col <= number_col <= arng.max_col:
                continue  # 橫跨題號欄的合併列不是作答格
            seen.add(anchor)
            value = grid.cell(*anchor)
            label = "" if value is None else str(value)
            ref = _reference(grid, merged, r, reference_col)
            prompt = _prompt(grid, merged, r, question_col)
            target = _blank_fill_cell(grid, merged, header_answer, anchor, label)
            if target is not None:
                coord = f"{get_column_letter(target[1])}{target[0]}"
                slots.append((coord, "", False, ref, label, prompt))
            else:
                coord = f"{get_column_letter(anchor[1])}{anchor[0]}"
                slots.append((coord, label, bool(PLACEHOLDER.search(label)), ref, label, prompt))
        if not slots:
            raise GuidedNotesError(f"第 {number} 題找不到作答格")
        raw.append((number, slots))
    if not raw:
        raise GuidedNotesError("找不到題號（表頭下方的題號欄沒有正整數）")
    numbers = [n for n, _ in raw]
    dupes = sorted({n for n in numbers if numbers.count(n) > 1})
    if dupes:
        raise GuidedNotesError("題號重複：" + "、".join(map(str, dupes)))
    questions = tuple(
        Question(number, tuple(
            Slot(grid.title, coord, label, ph, _display(shown, ph, i, len(slots) > 1), ref, prompt)
            for i, (coord, label, ph, ref, shown, prompt) in enumerate(slots, 1)
        ))
        for number, slots in raw
    )
    return ParsedNotes(grid.title, questions)


XLSX_BAD_TITLE = re.compile(r"[\\/:*?\[\]]")
XLSX_TITLE_MAX = 31


def _xlsx_title(title: str, used: set[str]) -> str:
    """Google 允許、xlsx 不允許的分頁名稱字元換成「_」並截到 31 字；重名加序號（實作輪評審）。"""
    base = XLSX_BAD_TITLE.sub("_", title).strip("'")[:XLSX_TITLE_MAX] or "工作表"
    name, n = base, 2
    while name.lower() in used:
        suffix = f"_{n}"
        name, n = base[: XLSX_TITLE_MAX - len(suffix)] + suffix, n + 1
    used.add(name.lower())
    return name


def grids_to_xlsx(grids: Sequence[Grid]) -> tuple[bytes, dict[str, str]]:
    """格狀資料轉成只含值與合併的 xlsx（Google 來源的下載備援，guided-notes-sheets-sync D4）。

    回傳 (xlsx, {Google 分頁名: xlsx 分頁名})；寫回 Google 仍用原名，只有下載備援用對照後的名稱。
    """
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    used: set[str] = set()
    names: dict[str, str] = {}
    for grid in grids:
        names[grid.title] = _xlsx_title(grid.title, used)
        ws = wb.create_sheet(names[grid.title])
        for row in range(1, grid.max_row + 1):
            for col in range(1, grid.max_column + 1):
                value = grid.cell(row, col)
                if value is not None:
                    cell = ws.cell(row, col, value)
                    if isinstance(value, str):
                        cell.data_type = "s"  # 「=」開頭的文字不得變公式
        for m in grid.merges:
            ws.merge_cells(start_row=m.min_row, start_column=m.min_col,
                           end_row=m.max_row, end_column=m.max_col)
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue(), names


def rename_sheets(notes: ParsedNotes, names: dict[str, str]) -> ParsedNotes:
    """把作答格的分頁名換成 xlsx 備援檔裡的名稱（座標不變）。"""
    return ParsedNotes(names.get(notes.sheet, notes.sheet), tuple(
        Question(q.number, tuple(replace(s, sheet=names.get(s.sheet, s.sheet)) for s in q.slots))
        for q in notes.questions))


def fill(slot: Slot, answer: str) -> str:
    """佔位符 ⇒ 取代第一段底線；否則接在既有標籤之後（guided-notes-export D2）。"""
    if slot.placeholder:
        return PLACEHOLDER.sub(lambda _: answer, slot.label, count=1)
    return f"{slot.label}{answer}"


def write_answers(original: bytes, notes: ParsedNotes, answers: dict[int, tuple[str, ...]]) -> bytes:
    """把每題得主答案寫回匯入時記下的作答格；其他儲存格與合併範圍不動（guided-notes-export D1）。

    `answers`：題號 → 各子題答案（無得主的題目不在其中，保持原樣）。
    """
    wb = openpyxl.load_workbook(io.BytesIO(original))
    for q in notes.questions:
        values = answers.get(q.number)
        if values is None:
            continue
        for slot, answer in zip(q.slots, values, strict=True):
            cell = wb[slot.sheet][slot.cell]
            cell.value = fill(slot, answer)
            # openpyxl 會把 = 開頭的字串存成公式；學生答案一律存為文字（v1.1 評審實證）
            cell.data_type = "s"
    out = io.BytesIO()
    wb.save(out)
    return out.getvalue()
