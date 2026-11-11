# Research: 005 guided-notes-export

知識時點：2026-11-11。

## R1 寫回演算法

- **Decision**：openpyxl 重新載入保存的原檔位元組，只改作答格，另存新位元組；原檔不變可重複匯出。
- **證偽欄｜可證偽**：`probes/results/2026-11-11-openpyxl-writeback.txt`（合併範圍不變 True、其他非空格變動數 0、框線保留）；`test_round_trip_preserves_other_cells`（三份夾具）；`test_export_can_repeat`。

## R2 填寫格式與文字型別

- **Decision**：佔位符取代第一段底線；否則「標籤＋答案」；`cell.data_type = "s"`。
- **Rationale**：openpyxl 會把 `=` 開頭字串存成公式（OpenSpec 組提案輪紅隊以 openpyxl 3.1.5 實證 `data_type` 為 `f`；實作輪紅隊再以 `=cmd|'/c calc'!A0` 驗證匯出為 `inlineStr`）。
- **證偽欄｜可證偽**：`test_group_keeps_labels`、`test_placeholder_replaced`、`test_formula_like_answer_stays_text`。屬取捨：同一格多段底線只取代第一段（followup）。

## R3 真棧驗證

- **Decision**：以真 uvicorn 與真 WebSocket 用戶端跑完整流程。
- **Rationale**：TestClient 不經 uvicorn；真棧發現 uvicorn 缺 WebSocket 實作與 INFO 日誌外洩憑證兩個問題（已在 001 修正並回寫 research R3、R5）。
- **證偽欄｜可證偽**：`probes/results/2026-11-11-e2e-flow.txt`。
