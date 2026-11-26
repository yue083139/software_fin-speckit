# 002 guided-notes-import 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增：`POST /api/teacher/import`（multipart，欄位 `file`）、`POST /api/teacher/import-url`（`{url}`），以及老師與學生 view 的 `questions`、老師 view 的 `source`。錯誤：400 檔案／連結／格式不符、401、409 非準備階段。
