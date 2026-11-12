# 008 mode-timed-scoring 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /api/teacher/open-next`（`{question}`；401／409 非 answering、非逐題模式、目前題未揭曉、已無題目）、`POST /api/teacher/close-question`（`{question}`；401／409 沒有進行中的題目）、`POST /api/teacher/reveal-question`（`{question}`；401／409 未關閉或尚有未判定）；`POST /api/teacher/question-settings` 本體改為 `{question, multiplier?, time_limit?}`（至少一欄；時限 5–120）；`POST /api/student/submit` 的 409 增「這一題目前沒有開放作答」「本題作答時間已到」；`mode` 增 `timed`。view 增欄位見 [data-model.md](../data-model.md)。
