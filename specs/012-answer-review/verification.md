# Verification: 012 answer-review（v1.1）

知識時點：2026-11-26；本機 Windows 11、worktree `wt-sk-answer-review`、分支 `012-answer-review`（rebase 於 `011-question-text` `244adb8`）。server、tests、contracts 與 OpenSpec 組 `feat/answer-review` `27661ad` 為同一份 diff（`make gate-parity SIBLING=../wt-os-answer-review` 見下）。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 圖上元素／訊息 | 程式落點 | 結果 |
|---|---|---|---|
| component | app.py `/api/teacher/review`・`review-reset` | `server/quiz_server/app.py:373`「`async def review(body: ReviewBody)`」、`:379`「`async def review_reset(body: ReviewResetBody)`」 | 一致 |
| component | app.py `export_lock` 序列化匯出與寫回；`_作答情況.xlsx` | `app.py:146`「`export_lock = asyncio.Lock()`」、`:117`「`return f"{stem}_作答情況.xlsx"`」 | 一致 |
| component | Activity `review`・`review_reset`・`review_candidate`・`sheet_written` | `server/quiz_server/activity.py:477`、`:492`、`:471`、`:129` | 一致 |
| component | results build（老師另含 review 欄位） | `server/quiz_server/results.py:38`「`entry["review"] = {`」 | 一致 |
| component | google_sheets `COPY_SUFFIX「_作答情況」`・`write_answers(restore)` | `server/quiz_server/google_sheets.py:18`、`:125` | 一致 |
| component | ClassicBuzzRule 候選＝第一個未被判錯者 | `server/quiz_server/scoring.py:69`「`is_winner = correct is not False and not winner_found`」 | 一致 |
| component | web Results（老師）讀 review 欄位、候選格「答對」「答錯」、已鎖定、重設本題、全部答錯 | `web/src/pages/Results.tsx` `ReviewCell`、`ReviewSummary`；`Teacher.tsx` `reviewing`（經典且 ended）；`web/src/pages/review.test.tsx` | 一致 |
| component | Results（學生）得主・分數・對錯標記 | `Results.tsx` `StudentResults` `verdict(r.correct)`；`review.test.tsx`「學生結果：檢查後 ✓／✗」 | 一致 |
| component | PhaseControls 匯出鈕（匯出中停用） | `Teacher.tsx` `exporting`；`review.test.tsx`「匯出進行中兩顆匯出鈕停用」 | 一致 |
| class | `Activity.mark_sheet_written(sheet_id, numbers)` | `activity.py:502` | 一致 |
| class | `ReviewBody {question, team, correct}`、`ReviewResetBody {question}` | `app.py` `class ReviewBody`、`class ReviewResetBody` | 一致 |
| sequence | 401 → 422 → 409 模式／階段 → 404 | `server/tests/test_review.py::test_error_order_401_then_422`、`test_only_classic_and_only_ended`、`test_no_submission_and_unknown_question` | 一致 |
| sequence | 已鎖定／無候選／候選不符三種 409 | `activity.py` `review`（依序 `本題已鎖定` → `本題沒有可檢查的答案` → `這一組不是目前要檢查的答案`） | 一致 |
| sequence | `_bump()` 成功恰推播一次、錯誤不推播 | `test_review.py::test_successful_review_pushes_once_and_failures_push_nothing` | 一致 |
| sequence | 重設未檢查題 409「本題尚未檢查」 | `activity.py` `review_reset`；`test_review.py::test_reset_returns_to_rank_one` | 一致 |
| sequence | 鎖內快照 → `write_answers(restore=sheet_written)` → `mark_sheet_written` | `app.py` `export_sheet`；`test_api_google.py::test_reexport_restores_previously_written_cells` | 一致 |

## 門禁實錄

`make gate` 後接 `make gate-parity SIBLING=../wt-os-answer-review`，原樣摘錄：

```
All checks passed!
All checks passed!
294 passed, 1 warning in 21.13s
58 passed in 6.32s
 Test Files  8 passed (8)
      Tests  41 passed (41)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 37 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 37 個圖檔語法通過
docs/requirements.md: 兩組內容不一致
contracts/api.md: 兩組內容不一致
gate-parity: 2 處不一致
make: *** [gate-parity] Error 1
gate-exit=2
gate-parity: 0 處不一致
```

`make gate` 內含的 gate-parity 預設比對 `../software_fin-openspec`（當時停在 `feat/question-text`，尚無本卡改動），故 `docs/requirements.md`、`contracts/api.md` 2 處不一致屬預期；與同批的 OpenSpec worktree 比對 0 處不一致。其餘門禁全綠（server 294 passed、web 41 passed）。前一次 `make gate` 在機器負載高時 web 有 1 例逾時，單獨重跑與本次皆 41 passed。

前端整合後（rebase 於 `origin/dev`，含 `web-workbench`）：`make gate`、前端再跑一次、`make gate-parity SIBLING=../wt-os-answer-review`：

```
All checks passed!
All checks passed!
297 passed, 1 warning in 16.63s
58 passed in 6.87s
 Test Files  9 passed (9)
      Tests  48 passed (48)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 40 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 40 個圖檔語法通過
docs/requirements.md: 兩組內容不一致
docs/parity.md: 兩組內容不一致
contracts/api.md: 兩組內容不一致
gate-parity: 3 處不一致
make: *** [gate-parity] Error 1
gate-exit=2
 Test Files  9 passed (9)
      Tests  48 passed (48)
gate-parity: 0 處不一致
```

`make gate` 內的 gate-parity 預設比對 `../software_fin-openspec`（另一分支）3 處不一致屬預期；與同批 OpenSpec worktree 比對 0 處不一致。

## 變異實錄

與 OpenSpec 組同一份程式碼，變異實錄見 `software_fin-openspec` `openspec/changes/answer-review/verification.md`：拿掉候選比對 ⇒ `test_double_click_does_not_skip_a_team` 等 2 例紅；`restore=frozenset()` ⇒ `test_reexport_restores_previously_written_cells` 紅；刪 `load_questions` 內清空 ⇒ `test_reimport_clears_written` 紅；拿掉 `mark_sheet_written` 副本 id 條件 ⇒ `test_written_not_recorded_when_copy_changed_during_write` 紅；重置加清空 ⇒ `test_reset_keeps_written_and_restores_in_next_round` 紅。

## 評審紀錄

- 提案輪（v1.0 → v1.1）：紅隊 0B/2M/3m、架構 0B/1M/3m，皆 0 阻斷；藥方見 research 抬頭 v1.1 段（需求 §4 解讀、game-modes／results-view MODIFIED、寫回範圍改「有得主＋上次寫過」、匯出鎖、推播口徑、錯誤碼 401→422）。
- 實作輪：紅隊 **CLEARED**（0B/0M/2m）、架構 **CLEARED**（0B/0M/0m）。紅隊實測：並發 5 個對同一候選的「答錯」⇒ 狀態碼 `[200, 409, 409, 409, 409]`（候選只移一組）；A-6 重置後新一場寫回 ⇒ H5／H6 還原、G13 寫入新得主。紅隊次要兩條（重新匯入清空、寫回期間換副本不記錄）已落永久測試與變異實錄（上表）；架構外包檢查兩條：M-022 守門欄改列具體測試名、`spec.md` FR-005 與 US3 情境 5、6 補「重置保留、重新匯入清空」並由測試守。

## followup（不阻塞，主人 @yue083139）

- 匯出鎖（`app.py` `export_lock`）沒有並發測試：兩個寫回請求真正交錯需要可控的 Google 替身延遲；目前只以程式結構（鎖內取快照、鎖內 `mark_sheet_written`）保證。
- 老師端「答對／答錯／重設本題」按鈕、匯出中停用、`ImportPanel.tsx` 副本名稱文案：`web-workbench`（antd）合入後整合。

## 人工驗證（需求 P-05）

狀態：**待執行**（負責人，`docs/manual-verification.md` 場次 A 第 15a～15c、16～18 步；老師端按鈕待 `web-workbench` 整合後才有）。
