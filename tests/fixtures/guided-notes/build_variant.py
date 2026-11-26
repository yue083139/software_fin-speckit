"""產生版面變形的 Guided Notes 夾具 variant.xlsx（卡 guided-notes-import tasks 1.1）。

與官方範本刻意不同：第一個工作表沒有表頭（須跨工作表找）、表頭在第 8 列且從 C 欄開始、
欄名為「編號／題目敘述／答案」、題號有字串「3.」與浮點數 4.0、第 2 題為 3 個子題的題組、
第 1 題作答格含底線佔位符、第 5 題作答格未合併、表頭下有不屬於任何題目的備註列。

用法：python tests/fixtures/guided-notes/build_variant.py（輸出到同目錄 variant.xlsx）
期望解析結果：5 題，子題數 [1, 3, 1, 2, 1]。
"""
from pathlib import Path

import openpyxl
from openpyxl.styles import Border, Font, Side

OUT = Path(__file__).with_name("variant.xlsx")
THIN = Side(style="thin")
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)


def main() -> None:
    wb = openpyxl.Workbook()
    intro = wb.active
    intro.title = "說明"
    intro["A1"] = "本檔為測試用自製 Guided Notes，題目皆為合成內容。"
    ws = wb.create_sheet("第二份學習單")
    ws.merge_cells("C2:I2")
    ws["C2"] = "資料結構小測驗（變形版面）"
    ws["C2"].font = Font(bold=True, size=14)
    ws["C5"] = "班級：＿＿＿＿　組別：＿＿＿＿"
    ws["C8"], ws["D8"], ws["H8"] = "編號", "題目敘述", "答案"
    ws.merge_cells("D8:G8")
    ws.merge_cells("H8:I8")
    for c in ("C8", "D8", "H8"):
        ws[c].font = Font(bold=True)

    def question(row: int, number, text: str, answer=None, merge_answer: bool = True) -> None:
        ws.cell(row, 3, number).border = BOX
        ws.merge_cells(start_row=row, start_column=4, end_row=row, end_column=7)
        ws.cell(row, 4, text)
        if merge_answer:
            ws.merge_cells(start_row=row, start_column=8, end_row=row, end_column=9)
        if answer is not None:
            ws.cell(row, 8, answer)

    question(9, 1, "先進先出的資料結構稱為什麼？", "______")
    ws.merge_cells("C10:I10")
    question(11, 2, "二元樹走訪：先拜訪根節點的方式稱為？", "(a)")
    ws.merge_cells("D12:G12")
    ws["D12"] = "先拜訪左子樹、再根、再右子樹稱為？"
    ws.merge_cells("H12:I12")
    ws["H12"] = "(b)"
    ws.merge_cells("D13:G13")
    ws["D13"] = "最後才拜訪根節點稱為？"
    ws.merge_cells("H13:I13")
    ws["H13"] = "(c)"
    ws.merge_cells("C11:C13")
    ws.merge_cells("C14:I14")
    question(15, "3.", "以鍵值直接計算儲存位置的結構稱為？")
    ws.merge_cells("C16:I16")
    question(17, 4.0, "圖的走訪：使用佇列的方式稱為？", "（1）")
    ws.merge_cells("D18:G18")
    ws["D18"] = "使用堆疊或遞迴的方式稱為？"
    ws.merge_cells("H18:I18")
    ws["H18"] = "（2）"
    ws.merge_cells("C17:C18")
    ws.merge_cells("C19:I19")
    question(20, 5, "時間複雜度 O(log n) 的搜尋法稱為？", merge_answer=False)
    ws["C22"] = "備註：本頁共 5 題，請以組為單位作答。"
    wb.save(OUT)
    print(f"已產生 {OUT}")


if __name__ == "__main__":
    main()
