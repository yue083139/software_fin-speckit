"""Guided Notes 解析（guided-notes-import D1–D4）與寫回（guided-notes-export D1、D2）。

定位只依表頭文字與合併範圍；本模組不含任何寫死的儲存格座標。
"""
import io
import re
import unicodedata
from dataclasses import dataclass

import openpyxl
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.cell_range import CellRange
from openpyxl.worksheet.worksheet import Worksheet

NUMBER_ALIASES = ("題號", "編號", "題次", "no", "no.", "#")
ANSWER_ALIASES = ("作答", "答案", "回答", "answer")
HEADER_SCAN_ROWS = 50
PLACEHOLDER = re.compile(r"[_＿]{3,}")
NUMBER_TEXT = re.compile(r"^(\d+)[.、]?$")


class GuidedNotesError(ValueError):
    """檔案不符合 Guided Notes 格式；API 層轉成 400，活動狀態不變。"""


@dataclass(frozen=True)
class Slot:
    sheet: str
    cell: str
    label: str  # 作答格原有文字（如「（1）」或佔位符原文），寫回時保留
    placeholder: bool
    display: str  # 給學生看的子題標籤


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


def _merged_index(ws: Worksheet) -> dict[tuple[int, int], CellRange]:
    index: dict[tuple[int, int], CellRange] = {}
    for rng in ws.merged_cells.ranges:
        for row in range(rng.min_row, rng.max_row + 1):
            for col in range(rng.min_col, rng.max_col + 1):
                index[(row, col)] = rng
    return index


def _find_header(ws: Worksheet, merged: dict) -> tuple[int, int, int] | None:
    for row in range(1, min(ws.max_row, HEADER_SCAN_ROWS) + 1):
        number_col = answer_col = None
        for col in range(1, ws.max_column + 1):
            value = ws.cell(row, col).value
            if value is None:
                continue
            text = _norm(value)
            if number_col is None and text in NUMBER_ALIASES:
                number_col = col
            elif answer_col is None and text in ANSWER_ALIASES:
                rng = merged.get((row, col))
                answer_col = rng.min_col if rng else col
        if number_col is not None and answer_col is not None:
            return row, number_col, answer_col
    return None


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
    for ws in wb.worksheets:
        merged = _merged_index(ws)
        header = _find_header(ws, merged)
        if header is not None:
            return _parse_sheet(ws, merged, header)
    raise GuidedNotesError(
        "找不到同時含題號與作答欄的表頭列（題號欄可用名稱："
        + "、".join(NUMBER_ALIASES) + "；作答欄可用名稱：" + "、".join(ANSWER_ALIASES) + "）"
    )


def _parse_sheet(ws: Worksheet, merged: dict, header: tuple[int, int, int]) -> ParsedNotes:
    header_row, number_col, answer_col = header
    raw: list[tuple[int, list[tuple[str, str, bool]]]] = []
    for row in range(header_row + 1, ws.max_row + 1):
        rng = merged.get((row, number_col))
        if rng is not None and (rng.min_row, rng.min_col) != (row, number_col):
            continue  # 合併範圍的非左上角格：屬於上一題或分隔列
        number = _as_number(ws.cell(row, number_col).value)
        if number is None:
            continue
        rows = range(rng.min_row, rng.max_row + 1) if rng else range(row, row + 1)
        slots: list[tuple[str, str, bool]] = []
        seen: set[tuple[int, int]] = set()
        for r in rows:
            arng = merged.get((r, answer_col))
            anchor = (arng.min_row, arng.min_col) if arng else (r, answer_col)
            if anchor in seen:
                continue
            if arng is not None and arng.min_col <= number_col <= arng.max_col:
                continue  # 橫跨題號欄的合併列不是作答格
            seen.add(anchor)
            value = ws.cell(*anchor).value
            label = "" if value is None else str(value)
            coord = f"{get_column_letter(anchor[1])}{anchor[0]}"
            slots.append((coord, label, bool(PLACEHOLDER.search(label))))
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
            Slot(ws.title, coord, label, ph, _display(label, ph, i, len(slots) > 1))
            for i, (coord, label, ph) in enumerate(slots, 1)
        ))
        for number, slots in raw
    )
    return ParsedNotes(ws.title, questions)


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
