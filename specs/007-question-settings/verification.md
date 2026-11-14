# Verification: 007 question-settings

## 門禁（2026-11-12，本機 Windows）

見文末「門禁原樣輸出」（兩組同批跑）。程式與 OpenSpec 組逐位元組相同（`diff -rq` server/quiz_server、server/tests、web/src、contracts 無差異）。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `QuestionAttrs(multiplier=1)` | `server/quiz_server/scoring.py:20` | 一致 |
| class | `ScoringRule.rank(..., attrs: QuestionAttrs \| None)` | `scoring.py` 三處簽名 | 一致 |
| class | `ClassicBuzzRule`、`AccuracyRule` 乘倍率 | `scoring.py:58`、`:86` | 一致 |
| class | `SettingsError` | `server/quiz_server/activity.py:30` | 一致 |
| class | `Activity.attrs`、`set_question`、`load_questions` 重建、`reset` 保留 | `activity.py:164`、`:176`；`reset` 不動 `attrs` | 一致 |
| class | `views.score_label` | `server/quiz_server/views.py:21` | 一致 |
| sequence | `set_question`：檢查 preparing、題號、倍率 → 寫入 → version+1 | `activity.py:176` 起 | 一致 |
| sequence | 推播 `questions[].multiplier`、`score_label` | `views.py:18`、`:21` | 一致 |
| sequence | `results.build` → `rank(送出, judgments, attrs)` | `server/quiz_server/results.py` `_ranked`（以 `attrs_of(題號)` 取圖中的 `attrs[題號]`，題號不在表中時回預設值） | 一致 |
| component | `POST /api/teacher/question-settings` | `server/quiz_server/app.py:201` | 一致 |
| component | Teacher QuestionList 勾選框、Student 標記、欄名 `score_label` | `web/src/pages/ImportPanel.tsx`、`AnswerForm.tsx`、`Results.tsx` | 一致 |

偏離：無。

## 契約語意補充（負責人 2026-11-14 批准）

見 research R1：經典規則得主得「1 × 該題倍率」分；`team_scores` 欄名見 `score_label`。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/question-settings/verification.md`：勾第 3 題雙倍、學生看到標記、開始後不可改、第1組搶到第 3 題得 2 分、欄名「得分」、重置保留、重新匯入清除。

結果：＿＿＿（執行人／日期／看到什麼）

## 門禁原樣輸出

```
$ make gate
All checks passed!
All checks passed!
173 passed, 1 warning in 8.22s
51 passed in 5.45s
 Test Files  5 passed (5)
      Tests  21 passed (21)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 22 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 22 個圖檔語法通過
gate-parity: 0 處不一致
```
