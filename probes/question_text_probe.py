"""question-text 探針：列出每份 Guided Notes 的表頭、題目欄逐列全文與合併範圍（question-text D1）。

用法：uv run --project server python -X utf8 probes/question_text_probe.py tests/fixtures/guided-notes/*.xlsx
"""
import sys
from pathlib import Path

import openpyxl
from openpyxl.utils import get_column_letter

QUESTION = ("題目", "題目敘述", "問題", "題幹", "question")


def main(paths: list[str]) -> None:
    print("指令：uv run --project server python -X utf8 probes/question_text_probe.py " + " ".join(paths))
    for p in paths:
        wb = openpyxl.load_workbook(p)
        for ws in wb.worksheets:
            for row in ws.iter_rows(min_row=1, max_row=min(ws.max_row, 50)):
                hit = [c for c in row if c.value is not None and str(c.value).strip().lower() in QUESTION]
                if hit:
                    break
            else:
                continue
            header = {c.coordinate: str(c.value) for c in row if c.value is not None}
            col = hit[0].column
            letter = get_column_letter(col)
            merges = sorted(str(r) for r in ws.merged_cells.ranges if r.min_col <= col <= r.max_col)
            print(f"== {Path(p).name} [{ws.title}] 表頭 {header}")
            print(f"   題目欄 {letter} 的合併範圍：{merges}")
            for r in range(row[0].row + 1, ws.max_row + 1):
                v = ws.cell(r, col).value
                if v is not None:
                    print(f"   {letter}{r}: {v}")


if __name__ == "__main__":
    main(sys.argv[1:])
