# 012 answer-review 介面契約

**狀態：待負責人批准（research R2、R4、R6）**；批准後實作時同批改 [`/contracts/api.md`](../../../contracts/api.md)。

錯誤判斷先後：**422 本體格式 → 401 老師金鑰 → 409 模式 → 409 階段 → 404 題號 → 409 已鎖定 → 409 無可檢查 → 409 候選不符**。

| 端點 | 本體 | 成功 | 錯誤 |
|---|---|---|---|
| `POST /api/teacher/review`（新） | `{question, team, correct}` | `{question, team, correct}`（不含答案）；推播 | 401；409「只有經典搶答可以檢查」「搶答結束後才能檢查」「本題已鎖定，請先重設本題」「本題沒有可檢查的答案」「這一組不是目前要檢查的答案，請重新整理」；404 題號不存在；422 |
| `POST /api/teacher/review-reset`（新） | `{question}` | `{question}`；推播 | 401；409 模式、階段；404；422 |

**語意補充**：

- 經典模式 `results[].ranking[].correct`／`board[].ranking[].correct`：未檢查 `null`，檢查後 `true`／`false`；`winner` 為候選（可能為 `null`＝全部答錯）；分數依候選（R1、R4）。
- `POST /api/teacher/import-url`：副本名稱「<原標題>_作答情況」（R6）。
- `GET /api/teacher/export`：`filename*=UTF-8''<原檔名>_作答情況.xlsx`（R6）。
- `POST /api/teacher/export-sheet`：每次寫入全部作答格，無得主者寫回原內容（R5）。

**不變**：`/api/teacher/judge`、`/api/teacher/accept-suggestions`、`/api/teacher/reveal` 及判定模式語意；老師與學生 view 欄位。
