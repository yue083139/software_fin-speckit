# Verification: 003 buzz-answering

## 門禁（2026-11-11，本機 Windows）

```
$ make gate-pr
All checks passed!
All checks passed!
106 passed, 1 warning in 12.37s
51 passed in 6.28s
 Test Files  2 passed (2)
      Tests  10 passed (10)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 10 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## 變異實錄（research R1）

```
$ （activity.py 的 async with self._lock 換成 contextlib.nullcontext()）uv run --project server pytest -q server/tests/test_submit.py -k concurrent
FAILED server\tests\test_submit.py::test_concurrent_same_question - assert [1...
FAILED server\tests\test_submit.py::test_concurrent_same_team_same_question
2 failed, 14 deselected in 0.56s
```

## 圖碼一致核對（憲章原則 VII）

> 本表行號以本功能實作提交 `43e0126` 當下的程式為準（後續功能會移動行號）；交付版（最終分支）的行號見 `specs/005-guided-notes-export/verification.md`「交付版圖碼核對」。

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `Submission`、`Ranked` | `server/quiz_server/scoring.py:11`、`:20` | 一致 |
| class | `ScoringRule.rank`（含 judgments、attrs）、`team_scores` | `scoring.py:29`、`:32`、`:35` | 一致 |
| class | `ClassicBuzzRule` | `scoring.py:38` | 一致 |
| class | `AlreadySubmittedError`、`AnswerError`、`clean_answers` | `server/quiz_server/activity.py:24`、`:28`、`:32` | 一致 |
| class | `Activity.question`／`submit`／`own_submissions`／`start`（須已匯入） | `activity.py:145`、`:152`、`:169`、`:178` | 一致 |
| sequence | submit 內：檢查 → 讀 next_seq → `_checkpoint` → 寫回 | `activity.py:152` 起 | 一致 |
| sequence | 第2組 view 不變則不推送 | `app.py` 送出迴圈 `if view == last_view`（001） | 一致 |
| sequence | ended 才以規則產生 results | `server/quiz_server/views.py:45`、`server/quiz_server/results.py:7` | 一致 |
| component | `POST /api/student/submit`、`RequestValidationError` 不回顯本體 | `server/quiz_server/app.py:112`、`:84` | 一致 |
| component | AnswerForm、studentSubmit | `web/src/pages/AnswerForm.tsx`、`web/src/api.ts` | 一致 |

偏離：無。

## 人工驗證（需求 P-05）

狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/archive/2026-11-12-buzz-answering/verification.md`：兩組搶同一題、題組只填一格無法送出、第2組畫面與開發者工具的 WebSocket 訊息看不到第1組答案、重複送出被拒、結束後才看到結果。

結果：＿＿＿（執行人／日期／看到什麼）
