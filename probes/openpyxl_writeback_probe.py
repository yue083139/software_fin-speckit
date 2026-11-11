"""探針：openpyxl 寫入合併儲存格左上角後存檔再讀回，合併範圍、框線與其他格是否保留。

用法：python probes/openpyxl_writeback_probe.py <xlsx>
"""
import io
import sys

import openpyxl


def main(path: str) -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    raw = open(path, "rb").read()
    wb = openpyxl.load_workbook(io.BytesIO(raw))
    ws = wb.worksheets[0]
    before_merged = sorted(str(r) for r in ws.merged_cells.ranges)
    snap = {c.coordinate: c.value for row in ws.iter_rows() for c in row if c.value is not None}
    target = None
    for r in ws.merged_cells.ranges:
        cell = ws.cell(r.min_row, r.min_col)
        if r.min_col > 2 and cell.value in (None, "（1）"):
            target = cell
            break
    print("寫入目標", target.coordinate, "原值", repr(target.value), "框線", target.border.bottom.style)
    target.value = (target.value or "") + "探針答案"
    out = io.BytesIO()
    wb.save(out)
    wb2 = openpyxl.load_workbook(io.BytesIO(out.getvalue()))
    ws2 = wb2.worksheets[0]
    after_merged = sorted(str(r) for r in ws2.merged_cells.ranges)
    t2 = ws2[target.coordinate]
    print("讀回值", repr(t2.value), "框線", t2.border.bottom.style)
    print("合併範圍不變", before_merged == after_merged, len(after_merged))
    changed = [k for k, v in snap.items() if k != target.coordinate and ws2[k].value != v]
    print("其他非空格變動數", len(changed))
    print("工作表名稱", ws2.title, "欄寬G", ws2.column_dimensions["G"].width)


if __name__ == "__main__":
    main(sys.argv[1])
