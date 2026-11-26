# 003 buzz-answering 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /api/student/submit`（`X-Team-Token`；`{question, answers}`；403／404／409／422），`POST /api/teacher/start` 增加「尚未匯入題目」409，學生 view 新增 `my_submissions` 與 `ended` 時的 `results`，錯誤回應不回顯請求本體。
