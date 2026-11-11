"""探針：印出 Guided Notes xlsx 的表頭、合併範圍與非空儲存格，供匯入／匯出卡寫稿前確認版面。

用法：python probes/guided_notes_structure_probe.py <xlsx>...
只讀不寫；不含任何定位邏輯，定位口徑由匯入卡的規格決定。
"""
import sys

import openpyxl


def dump(path: str) -> None:
    wb = openpyxl.load_workbook(path)
    print(f"##### {path}")
    for ws in wb.worksheets:
        merged = sorted(str(r) for r in ws.merged_cells.ranges)
        print(f"== 工作表 {ws.title}  範圍 {ws.dimensions}")
        print(f"   合併範圍（{len(merged)}）：{', '.join(merged)}")
        for row in ws.iter_rows():
            for c in row:
                if c.value is not None:
                    print(f"   {c.coordinate}: {c.value!r}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    for p in sys.argv[1:]:
        dump(p)
