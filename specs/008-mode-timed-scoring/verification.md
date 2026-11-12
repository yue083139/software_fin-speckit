# Verification: 008 mode-timed-scoring

## 變異實錄（research R1、R2、R4）

程式與 OpenSpec 組逐位元組相同（`diff -rq` server/quiz_server、server/tests、web/src、contracts、probes 無差異），變異在 OpenSpec 組跑一次，原樣輸出：

```
== 拿掉送出路徑的截止比對
FAILED tests/test_timed_mode.py::test_deadline_on_submit_path - Failed: DID N...
1 failed, 1 passed, 14 deselected in 0.51s
== 計時器只睡一次（while 改 if）
FAILED tests/test_timed_mode.py::test_timer_retries_after_early_wake - assert...
1 failed, 15 deselected in 0.44s
== close_question 用每次新建的鎖
FAILED tests/test_timed_mode.py::test_concurrent_close_and_submit - assert 1 ...
1 failed, 15 deselected in 0.44s
== 學生名次帶分數
FAILED tests/test_timed_mode.py::test_api_round_flow_and_scores - assert False
FAILED tests/test_timed_mode.py::test_leaderboard_counts_revealed_only - Asse...
FAILED tests/test_timed_mode.py::test_student_leaderboard_has_no_scores - ass...
3 failed, 13 deselected, 1 warning in 1.27s
```

## 真棧探針（research R5）

`probes/results/2026-11-12-timed-flow.txt`：真 uvicorn 下伺服器在開題後 5.02 秒自動關閉並推播（時限 5 秒）；他組送出後 0.5 秒內 0 則推播；第2組 payload 不含第1組答案、名次不含分數。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `Mode.sequential`、`timed` | `server/quiz_server/modes.py:23` | 一致 |
| class | `QuestionAttrs.time_limit` | `server/quiz_server/scoring.py` `QuestionAttrs` | 一致 |
| class | `Round` 六欄位 | `server/quiz_server/activity.py:41` | 一致 |
| class | `TimedRule`、`timed_points` | `scoring.py:113`、`:101` | 一致 |
| class | `Activity.rounds`、`current`、`_clock`／`_wall`／`_sleep`、`open_next`、`close_question`、`close_due`、`reveal_question`、`submit`、`end` | `activity.py:363`、`:367`、`:403`、`:393`、`:416`；送出 `:240`、`:247`；`end` `:284` | 一致 |
| class | `views_module.round_view`、`mode_info` | `server/quiz_server/views.py:22`、`mode_info` | 一致 |
| class | `results_module.revealed_scores`、`leaderboard(with_scores)`、`own_revealed` | `server/quiz_server/results.py:60`、`:65`、`:80` | **偏離已先改圖**：v1.1 圖把 `leaderboard` 畫在 views，實作放在 results（views 呼叫它）；依原則 VII 先改圖並重轉 PNG |
| sequence | `open_next`：檢查 → `Round(opened_at = clock())` → `create_task` 計時器 | `activity.py:367` 起 | 一致 |
| sequence | `submit`：題號＝current、未關閉、`clock() - opened_at <= limit`；`elapsed_ms` 同一讀值 | `activity.py:240`–`:247` | 一致 |
| sequence | 計時器 `close_due()` → closed → 推播 | `activity.py:385` `_run_timer`（迴圈）、`:393` | 一致 |
| sequence | 太晚送出 409 | `activity.py` 送出前置條件；探針「關閉後送出 409 這一題目前沒有開放作答」 | **偏離已先改圖**（實作輪架構通道）：v1.2 圖寫「本題作答時間已到」，但圖中情境是計時器已關閉之後才送，程式回「這一題目前沒有開放作答」；「時間已到」只在計時器尚未關閉時出現。已改圖並重轉 PNG |
| sequence | `reveal_question` → views → results `own_revealed`、`leaderboard(with_scores=False)` → `TimedRule` | `views.py:88`；`results.py` | 一致（圖已同批改） |
| component | `app.py` `open-next`、`close-question`、`reveal-question`、`question-settings(time_limit)` | `server/quiz_server/app.py:207`、`:213`、`:217`；`QuestionSettingsBody` | 一致 |
| component | 計時器任務迴圈直到關閉 | `activity.py:385` | 一致 |
| component | Teacher RoundControls、時限欄、StudentPanel 倒數與名次 | `web/src/pages/Teacher.tsx`、`ImportPanel.tsx`、`Student.tsx` `TimedPanel`、`Round.tsx` | 一致 |

## 人工驗證（需求 P-05）

狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/mode-timed-scoring/verification.md`：選時間計分、設時限、逐題開放、倒數到 0 自動關閉、晚送被拒、判定後揭曉、學生看到本組結果與沒有分數欄的名次表、未揭曉時不能開下一題或結束。

結果：＿＿＿（執行人／日期／看到什麼）

## 門禁原樣輸出（2026-11-12，本機 Windows）

```
$ make gate
All checks passed!
All checks passed!
197 passed, 1 warning in 9.62s
51 passed in 5.37s
 Test Files  6 passed (6)
      Tests  26 passed (26)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 25 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 25 個圖檔語法通過
gate-parity: 0 處不一致
```

## 實作輪評審補測（2026-11-12）

紅隊實作輪 `CLEARED`，另指出三處「程式對、測試守不住」（變異後仍綠）。已補測試，變異改為必紅：

```
== R1 作答毫秒改回自開始搶答（刪 opened_at = rnd.opened_at）
FAILED tests/test_timed_mode.py::test_open_in_order_and_only_current_accepted
1 failed, 16 passed, 1 warning in 2.35s
== R2 重置不清回合（刪 self.rounds = {}）
FAILED tests/test_timed_mode.py::test_reset_clears_rounds_and_timer - Asserti...
1 failed, 16 passed, 1 warning in 2.32s
== R3 採用建議不檢查回合已關閉（刪 _require_judgeable）
FAILED tests/test_timed_mode.py::test_judge_and_reveal_preconditions - Failed...
1 failed, 16 passed, 1 warning in 2.36s
```

架構通道實作輪 1 重要（契約 `judge`／`accept-suggestions` 未補時間計分語意）、2 次要（名次「空陣列」字句、008 時序圖晚送訊息）已修，見 `contracts/api.md`、design D5／D6、SpecKit 008 圖與核對表。
