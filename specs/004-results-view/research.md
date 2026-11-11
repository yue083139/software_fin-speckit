# Research: 004 results-view

知識時點：2026-11-11。對標：Kahoot! 每題結束顯示答案分布與排名；本系統以整場結束為揭曉點（R-08）。

## R1 共用結果函式

- **Decision**：`results.build(a)` 與 `results.team_scores(a)` 都經 `a.rule`；老師 `board` 與學生 `results` 呼叫同一函式。
- **證偽欄｜可證偽**：`test_teacher_and_student_agree`（JSON 逐字相同）。

## R2 學生結果欄位的存在性

- **Decision**：非 ended 階段學生 view 不含 `results`、`team_scores` 鍵（不是空陣列）。
- **Rationale**：前端以鍵存在與否判斷是否揭曉，空陣列易被誤判為「沒有結果」；也讓隔離測試可直接斷言鍵不存在。
- **證偽欄｜可證偽**：`test_student_results_only_when_ended`。

## R3 介面

- **Decision**：老師表最後一欄顯示「已送出組數」；學生結果頁首顯示本組得題數與各組得題數；答案以「（1）A ／ （2）B」格式呈現。
- **證偽欄｜屬取捨**：一張表即可在 Demo 影片同時展示多組狀況。
