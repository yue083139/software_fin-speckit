# Research: 007 question-settings

知識時點：2026-11-12。對標：Kahoot! Double points 為逐題開關、分數 ×2、題目開始前提示（`docs/research/competitors.md`）。

## R1 規則輸入

- **Decision**：`QuestionAttrs(multiplier=1)`；`ScoringRule.rank(submissions, judgments=None, attrs: QuestionAttrs | None = None)`；`ClassicBuzzRule` 得主、`AccuracyRule` 正確者 `score = 1 × multiplier`；`results` 的 `build`、`team_scores`、`winning_answers` 一律傳入該題 `attrs`。
- **Rationale**：分數只由規則產生（003 R3），排行榜、結果、匯出不另算。
- **證偽欄｜可證偽**：`test_scoring.py::test_multiplier_doubles`。

## R2 設定流程

- **Decision**：`set_question(number, multiplier)` 鎖內、`preparing`（409）、題號（404）、`multiplier in (1, 2)`（`SettingsError` 422）；`load_questions` 重建、`reset` 保留。
- **證偽欄｜可證偽**：`test_question_settings.py`。

## R3 view

- **Decision**：老師與學生 `questions[].multiplier`；`results`／`board` 每題 `multiplier`；`score_label`＝經典且全部 1 倍 ⇒「得題數」，否則「得分」。
- **證偽欄｜可證偽**：`test_question_settings.py::test_score_label`、`test_student_sees_multiplier`。
