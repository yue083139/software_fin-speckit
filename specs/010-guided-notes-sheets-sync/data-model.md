# Data Model: 010 guided-notes-sheets-sync

對照 `diagrams/010-guided-notes-sheets-sync-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `GoogleSession`（新） | `client_id`、`client_secret` | 環境變數；任一缺 ⇒ `configured = False` |
| `GoogleSession`（新） | `_pending: dict[state, (code_verifier, 到期時刻)]` | 一次性、10 分鐘；回呼取用即刪 |
| `GoogleSession`（新） | `_access_token`、`_refresh_token`、`_expires_at`、`email` | 只在記憶體；過期前 60 秒換新；登出清空 |
| `Grid`（新，介面） | `title`、`max_row`、`max_column`、`cell(row, col)`、`merges` | `OpenpyxlGrid`、`SheetsGrid` 兩個實作 |
| `Slot`（改語意） | `cell`、`label` | R5：子題可為標籤右側格，此時 `label=""`、`display` 取標籤格文字 |
| `Activity`（增） | `source_sheet_id: str \| None` | Google 試算表來源的 id；上傳 xlsx 為 `None`；重新匯入覆寫 |
| `Activity`（改） | `source_bytes: bytes \| None` | Google 來源時為格狀資料轉成的 xlsx（只含值與合併），供下載備援 |
| `GoogleAuthError`（新） | — | API 層轉 401 |
| `GoogleApiError`（新） | — | API 層轉 502，只帶 Google 錯誤 `status` |

學生 view、老師 view 不增欄位；Google 狀態只經 `GET /api/teacher/google`。
