"""產生含參考答案欄的 Guided Notes 夾具 reference.xlsx（卡 game-mode-framework tasks 1.1）。

版面：工作表「學習單」，表頭在第 3 列：B 題號、C:E 題目（合併）、F 作答、G 參考答案。
第 1 題單題（參考答案「CPU」）；第 2 題為 2 個子題的題組（參考答案「二進位」「0」）；
第 3 題沒有參考答案（G 欄空白）；第 4 題作答格為底線佔位符（參考答案「Linux」）。
題目皆為合成內容。

用法：python tests/fixtures/guided-notes/build_reference.py（輸出到同目錄 reference.xlsx）
期望解析結果：4 題，子題數 [1, 2, 1, 1]；參考答案 [["CPU"], ["二進位", "0"], [None], ["Linux"]]。
"""
from pathlib import Path

import openpyxl
from openpyxl.styles import Font

OUT = Path(__file__).with_name("reference.xlsx")


def main() -> None:
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "學習單"
    ws.merge_cells("B1:G1")
    ws["B1"] = "計算機概論 小測驗（含參考答案）"
    ws["B1"].font = Font(bold=True, size=14)
    ws["B3"], ws["C3"], ws["F3"], ws["G3"] = "題號", "題目", "作答", "參考答案"
    ws.merge_cells("C3:E3")
    for c in ("B3", "C3", "F3", "G3"):
        ws[c].font = Font(bold=True)

    def text(row: int, value: str) -> None:
        ws.merge_cells(start_row=row, start_column=3, end_row=row, end_column=5)
        ws.cell(row, 3, value)

    ws["B4"] = 1
    text(4, "電腦負責執行指令的核心元件英文縮寫是？")
    ws["G4"] = "CPU"
    ws["B5"] = 2
    ws.merge_cells("B5:B6")
    text(5, "電腦內部使用哪一種進位系統？")
    ws["F5"], ws["G5"] = "（1）", "二進位"
    text(6, "除了 1 之外，該系統還用哪個數字？")
    ws["F6"], ws["G6"] = "（2）", "0"
    ws["B7"] = 3
    text(7, "請舉一個你常用的應用程式。")
    ws["B8"] = 4
    text(8, "一個開放原始碼的作業系統核心名稱是？")
    ws["F8"], ws["G8"] = "______", "Linux"
    wb.save(OUT)
    print(f"已產生 {OUT}")


if __name__ == "__main__":
    main()
