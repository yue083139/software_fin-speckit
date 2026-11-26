# 005 guided-notes-export 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `GET /api/teacher/export`：回傳 xlsx（得主答案寫入作答格、一律為文字），`Content-Disposition` 含 `filename*=UTF-8''<原檔名>-搶答結果.xlsx`；401、409（非 ended 或尚未匯入）。
