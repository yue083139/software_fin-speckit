# Research: 008 mode-timed-scoring

知識時點：2026-11-12。對標：Kahoot!「How points work」：答對得分隨作答時間遞減、0.5 秒內滿分、答錯 0 分；主持人逐題推進，每題結束顯示排行榜（`docs/research/competitors.md`）。裁剪：沒有標準答案 ⇒ 每題多一步老師判定；學生端排行榜只公開名次，不公開他組分數與答案。

## R1 回合與截止

- **Decision**：`Round(number, opened_at, deadline_epoch_ms, limit, closed, revealed)`；`open_next` 依題號順序、`current is None` 才可開；送出檢查「題號＝current、未關閉、`clock() − opened_at ≤ limit`」；`close_due()` 由計時器任務呼叫、可重入；`Activity(clock=time.monotonic, wall=time.time)` 可注入。
- **Rationale**：截止寫在送出路徑，計時器排程誤差不影響公平；送出路徑在讓出點之前讀一次 `now = clock()`，截止比對與 `elapsed_ms` 共用（v1.1）；計時器任務迴圈「睡剩餘時間 → `close_due()`」直到該回合已關閉或不是 `current`（v1.1 紅隊實測 Windows asyncio 計時解析度 15.6 毫秒，60 次有 1 次提早約 3 毫秒醒來，單次睡眠會漏關）；`deadline_epoch_ms` 是靜態值，view 不會每秒變動、不破壞「view 改變才推送」。
- **證偽欄｜可證偽**：`test_timed_mode.py`（假時鐘：`limit` 時成功、`limit + 0.001` 時 409——v1.2：兩情況各用新活動，否則計時器會先在送出的讓出點關閉回合，測不到送出路徑本身的比對；`close_due` 前後；`test_timer_retries_after_early_wake`；`test_concurrent_close_and_submit` 20 輪：v1.2 改為「先開始的提早結束生效後，送出必被拒」——原斷言「被接受者 elapsed ≤ 時限」在假時鐘下恆真、測不到鎖）；變異實錄：拿掉截止比對必紅。

## R2 計分

- **Decision**：`timed_points(elapsed_ms, limit, multiplier)`：`ms = clamp(elapsed_ms, 0, T × 1000)`；ms ≤ 500 ⇒ 1000；否則 `(2001 × T − ms) // (2 × T)`（與 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5)` 代數相等；`Fraction` 精確值窮舉 T＝5–120、ms＝501–T×1000 不一致 0 例；浮點寫法 5129 例少 1 分）；乘倍率。`TimedRule` 正確者計分、得主＝最早正確者。
- **Rationale**：探針原樣輸出：

```
$ uv run --project server python -c "...round(0.5), round(2.5), round(999.5)..."
round(0.5)= 0 round(2.5)= 2 round(999.5)= 1000
T=30,t=2: 966.6666666666666 -> 967
```

- **證偽欄｜可證偽**：`test_scoring.py::test_timed_points`（TRD §4 三案例、點五案例 (1285, 5) ⇒ 872、倍率）。

## R3 時限

- **Decision**：`QuestionAttrs.time_limit = 20`，範圍 5–120；設定 API 本體 `{question, multiplier?, time_limit?}` 至少一欄。
- **Rationale**：預設 20 秒、上限 120 秒屬取捨（課堂填空題不需更長）。
- **證偽欄｜可證偽**：`test_question_settings.py` 時限錯誤碼與「只給一欄不動另一欄」。

## R4 隔離與排行榜

- **Decision**：`round`（公開回合狀態）；`mode` 增 `sequential`（前端不比對模式鍵）；學生 `revealed`（只有本組、只列已揭曉題）、`my_total`（本組累積）、`leaderboard: [{team, rank}]`（依已揭曉題累積分數的名次，同分同名次、下一名跳號，**不含分數**）；老師 `leaderboard: [{team, rank, score}]`；他組答案、分數、順位、作答秒數只在 `ended`。
- **Rationale**：TRD T-06「永遠不含他組答案內容直到該題揭曉」之上再收緊為「直到活動結束」，符合 R-09 與憲章原則 II 原文。分數是作答秒數的單調函數，公開他組分數時兩次相減即可反推秒數（時限 20 秒解析度約 0.04 秒），故依裁定原文「公開累積排名」只送名次（v1.1，兩通道）。
- **證偽欄｜可證偽**：`test_isolation.py::test_timed_mode_isolated`（開放中、已關閉、已揭曉）、`test_timed_other_team_submit_sends_nothing`、`test_leaderboard_counts_revealed_only`、`test_student_leaderboard_has_no_scores`。

## R5 真棧探針

- **Decision**：`probes/timed_flow_probe.py`：真 uvicorn、真 WebSocket 用戶端，時限 5 秒，確認伺服器自動關閉的推播。
- **Rationale**：計時器在 TestClient 與真 uvicorn 的事件迴圈行為可能不同（第一期真棧探針曾抓到兩個單元測試漏掉的問題）。
- **證偽欄｜可證偽**：探針斷言失敗即非零退出，原樣輸出入 `probes/results/`。
