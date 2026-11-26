# 012 answer-review 介面契約

**狀態：負責人 2026-11-26 批准（research R2、R4、R5、R6）**；已同批改 [`/contracts/api.md`](../../../contracts/api.md)。

錯誤判斷先後：**401 老師金鑰 → 422 本體格式 → 409 模式 → 409 階段 → 404 題號 → 409 已鎖定 → 409 無可檢查 → 409 候選不符**（重設：… → 404 → 409「本題尚未檢查」）。狀態改變的成功操作恰推播一次，錯誤不推播。

| 端點 | 本體 | 成功 | 錯誤 |
|---|---|---|---|
| `POST /api/teacher/review`（新） | `{question, team, correct}` | `{question, team, correct}`（不含答案）；推播 | 401；409「只有經典搶答可以檢查」「搶答結束後才能檢查」「本題已鎖定，請先重設本題」「本題沒有可檢查的答案」「這一組不是目前要檢查的答案，請重新整理」；404 題號不存在；422 |
| `POST /api/teacher/review-reset`（新） | `{question}` | `{question}`；推播 | 401；422；409 模式、階段；404；409「本題尚未檢查」 |

**語意補充**：

- 經典模式 `results[].ranking[].correct`／`board[].ranking[].correct`：未檢查 `null`，檢查後 `true`／`false`；`winner` 為候選（可能為 `null`＝全部答錯）；分數依候選（R1、R4）。
- `POST /api/teacher/import-url`：副本名稱「<原標題>_作答情況」（R6）。
- `GET /api/teacher/export`：`filename*=UTF-8''<原檔名>_作答情況.xlsx`（R6）。
- `POST /api/teacher/export-sheet`：寫入範圍＝目前有得主的作答格＋上次寫過、這次已無得主的作答格（以原內容還原）；與 `GET /api/teacher/export` 以同一把伺服器鎖序列化（R5）。
- 老師 view（新增欄位）：經典模式 `board[]` 每題 `review: {candidate: 組名|null, rejected: [組名…依順位], locked: bool}`；其他模式不帶，學生 `results` 永不帶（R4）。

**不變**：`/api/teacher/judge`、`/api/teacher/accept-suggestions`、`/api/teacher/reveal` 及判定模式語意；學生 view 欄位。
