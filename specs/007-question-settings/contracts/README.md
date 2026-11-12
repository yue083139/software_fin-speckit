# 007 question-settings 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /api/teacher/question-settings`（`{question, multiplier}` ⇒ `{question, multiplier}`；401／404 題號不存在／409 非 preparing／422 倍率不是 1 或 2）；`questions[]`、`results[]`、`board[]` 增 `multiplier`。**語意補充**：經典規則得主得 1 × 該題倍率分；`team_scores` 欄名見 `score_label`（見 research R1）。
