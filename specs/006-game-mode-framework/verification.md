# Verification: 006 game-mode-framework

## 門禁（2026-11-12，本機 Windows）

```
$ make gate
All checks passed!
All checks passed!
162 passed, 1 warning in 7.77s
51 passed in 5.43s
 Test Files  4 passed (4)
      Tests  17 passed (17)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 19 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 19 個圖檔語法通過
gate-parity: 0 處不一致
```

## 變異實錄（research R3）

程式與 OpenSpec 組逐位元組相同（`diff -rq` server/quiz_server、server/tests、web/src、contracts 無差異），變異在 OpenSpec 組跑一次，原樣輸出：

```
== 拿掉 reveal 的未判定檢查
FAILED tests/test_judging.py::test_reveal_blocked_until_all_judged - assert (...
2 failed, 15 deselected, 1 warning in 1.18s
== 拿掉 end 的 _require(ANSWERING)
1 passed, 16 deselected, 1 warning in 0.90s
== v1.0 並發測試：reveal 改用每次新建的鎖
1 passed, 16 deselected in 0.79s
== accept_suggestions 用每次新建的鎖
FAILED tests/test_judging.py::test_concurrent_judge_and_accept_suggestions - ...
1 failed, 16 deselected in 0.37s
== judge 用每次新建的鎖
FAILED tests/test_judging.py::test_concurrent_judge_and_accept_suggestions - ...
1 failed, 16 deselected in 0.43s
```

第 2、3 則未紅，處理見 research R3（v1.2）：`end()` 的前置條件不是唯一防線（轉移表已擋 `judging → judging`）；v1.0 並發測試假綠，已換成「老師判定與採用全部建議」的真競態。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `Mode`、`MODES`、`DEFAULT_MODE`、`ModeError` | `server/quiz_server/modes.py:11`、`:18`、`:24`、`:27` | 一致 |
| class | `Ranked.correct` | `server/quiz_server/scoring.py:27` | 一致 |
| class | `AccuracyRule`（正確 1 分、最早正確為得主） | `scoring.py:67` | 一致 |
| class | `Slot.reference` | `server/quiz_server/guided_notes.py:35` | 一致 |
| class | `judging.normalize`、`suggest` | `server/quiz_server/judging.py:8`、`:12` | 一致 |
| class | `Activity.rule`（唯讀）、`set_mode` | `server/quiz_server/activity.py:72`、`:140` | 一致 |
| class | `Activity.end`（只接受 answering）、`suggestion`、`pending_judgments`、`judge`、`accept_suggestions`、`reveal` | `activity.py:205`、`:220`、`:223`、`:227`、`:235`、`:254` | 一致 |
| sequence | `end()`：`_require(ANSWERING)` 後依 `mode.judged` 轉 `JUDGING` | `activity.py:208`–`:209` | 一致 |
| sequence | `accept_suggestions` loop：`suggest` 有結果才寫入 | `activity.py:235` 起 | 一致 |
| sequence | 判定後第2組不推送 | `app.py` 送出迴圈 `if view == last_view`（001）；`test_isolation.py::test_judging_hides_judgments` | 一致 |
| sequence | `reveal` alt：有未判定 ⇒ `PhaseError`（409） | `activity.py:254` 起 | 一致 |
| sequence | ended 才以 `AccuracyRule` 產生含 `correct` 的 results | `server/quiz_server/results.py:15`；`views.py` `student_view` | 一致 |
| component | `app.py` `/mode`、`/judge`、`/accept-suggestions`、`/reveal` | `server/quiz_server/app.py:196`、`:201`、`:207`、`:211` | 一致 |
| component | Teacher `ModeSelector`、判定鈕、Board `JudgeCell`、StudentPanel 模式說明 | `web/src/pages/Teacher.tsx`、`Results.tsx`、`Student.tsx` | 一致 |
| component | views 註記：參考答案與建議只在 `teacher=True` | `results.py:15` `build(teacher=)`、`views.py:36` | 一致 |

偏離：無。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/archive/2026-11-14-game-mode-framework/verification.md`：匯入 `reference.xlsx`、選「只計對錯」、兩組作答、結束進入判定中（學生看不到他組答案與參考答案）、採用全部建議、手動判剩餘一筆、揭曉、學生看到對錯與「最早答對」、匯出寫回最早答對者。

結果：＿＿＿（執行人／日期／看到什麼）
