# 010 guided-notes-sheets-sync 介面契約

**狀態：待負責人批准（research R7）**；批准前不改 [`/contracts/api.md`](../../../contracts/api.md)。

**新增**：
- `GET /api/teacher/google`（老師）⇒ `{configured, signed_in, email}`；401。
- `POST /api/teacher/google/login`（老師）⇒ `{url}`（Google 授權網址）；400 伺服器未設定 OAuth 用戶端；401。
- `GET /api/google/callback?code&state`（不需老師金鑰；只接受伺服器發出、未過期、未用過的 `state`）⇒ HTML「登入完成，可關閉此分頁」；400 state 不符或 Google 回 error。
- `POST /api/teacher/google/logout`（老師）⇒ `{signed_in: false}`；401。
- `POST /api/teacher/export-sheet`（老師）⇒ `{url}`（副本連結）；401 未登入 Google 或無老師金鑰；409 非 ended、尚未匯入、或題目不是從 Google 試算表匯入；502 Google 錯誤。

**語意改變**：
- `POST /api/teacher/import-url`：需已登入 Google，以 Sheets API 讀取（不再下載 xlsx）；401 未登入；400 連結不符（不發請求）；409 非 preparing（不發請求）；502 Google 錯誤。

**不變**：`POST /api/teacher/import`（上傳 xlsx）、`GET /api/teacher/export`（下載 xlsx；Google 來源時只含值與合併）。
