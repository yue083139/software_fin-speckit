# 010 guided-notes-sheets-sync 介面契約

**狀態：負責人 2026-11-17 批准（research R7）**；實作時同批改 [`/contracts/api.md`](../../../contracts/api.md)。

錯誤判斷先後一律：**老師金鑰 401 → 階段／來源 409 → 參數 400 → Google 登入 401 → Google 端 502**；Google 登入檢查前不發任何對外請求。

| 端點 | 成功 | 錯誤（依上述先後） |
|---|---|---|
| `GET /api/teacher/google` | `{configured, signed_in, email}` | 401 |
| `POST /api/teacher/google/login` | `{url}`，設 cookie `qz_gstate` | 401；400「伺服器未設定 Google OAuth 用戶端」 |
| `GET /api/google/callback?code&state`（不需老師金鑰） | HTML「登入完成，可關閉此分頁」 | 400 HTML「登入失敗，請回老師頁重新登入」（state 不符／過期／重放／cookie 不符／帶 error；不回顯參數） |
| `POST /api/teacher/google/logout` | `{signed_in: false}` | 401 |
| `POST /api/teacher/import-url` `{url}`（語意改變：需登入、匯入時複製後讀副本） | `{source, count, sheet_url}` | 401；409 非 preparing；400 連結不符／分頁不存在／解析錯誤；401「請先以 Google 帳號登入」「Google 登入已過期，請重新登入」；502 |
| `POST /api/teacher/export-sheet` | `{url}` | 401；409「搶答結束後才能匯出」「尚未匯入題目」「題目不是從 Google 試算表匯入，請改用下載 xlsx」；401 Google 未登入／過期；502 |

**不變**：`POST /api/teacher/import`（上傳 xlsx）、`GET /api/teacher/export`（下載 xlsx；Google 來源時只含值與合併）。老師與學生 view 不增欄位。
