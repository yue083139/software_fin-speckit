# Research: 016-teacher-key-error（與 OpenSpec design D1–D3 一一對應，R_n＝D_n）

知識時點：2026-11-26。

## R1 金鑰錯誤先 accept、不送訊息、再以 4401 關閉
- Decision：`ws()` 金鑰錯誤分支 `await socket.accept()` 後 `await socket.close(code=4401)`，之前無 `current_view()`、不入連線清單、無推播迴圈。
- Rationale：瀏覽器在交握前被拒時只得 1006；student-qr 對 4403 已同法實測（真 WebSocket 用戶端收到 4403）。
- 證偽：`test_teacher_ws_bad_key_accepts_then_closes_4401`；實作前 3 failed。

## R2 4403 優先於 4401
- Decision：本機檢查在金鑰檢查之前（沿用 014 R2）。
- 證偽：`test_public_host_takes_precedence_over_bad_key`。

## R3 老師頁整頁提示
- Decision：`Teacher.tsx` 的 `BadKeyNotice`（antd `Result status="error"`），文案「老師金鑰錯誤」＋「請用啟動伺服器時終端機印出的完整老師頁網址重新開啟，或回首頁重新輸入金鑰。」；`live.ts` 既有 4401 不重連。
- 證偽：`qr.test.tsx`、`live.test.tsx` 新增例。
