# Data Model: 008 mode-timed-scoring

對照 `diagrams/008-mode-timed-scoring-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Mode`（增） | `sequential: bool` | `MODES["timed"]`：judged=False、sequential=True、`TimedRule` |
| `QuestionAttrs`（增） | `time_limit: int = 20` | 5–120 秒 |
| `Round`（新） | `number`、`opened_at`、`deadline_epoch_ms`、`limit`、`closed`、`revealed` | `current`＝唯一未揭曉的回合 |
| `Activity`（增） | `rounds`、`_clock`、`_wall`、計時器任務 | 匯入、重置取消計時器並清空 |

## 回合狀態

| 狀態 | 進入 | 學生可送出 | 老師可判定 |
|---|---|---|---|
| open | `open_next` | 只限該題、未逾時 | 否 |
| closed | 時限到（`close_due`）或 `close_question` | 否 | 是 |
| revealed | `reveal_question`（無未判定） | 否 | 否 |

## view 增欄位

- 老師與學生：`round: {question, state: "open"|"closed", deadline_epoch_ms} | null`；`questions[].time_limit`。
- 學生（逐題模式、非 ended）：`revealed: [{question, submitted, correct, score}]`（只有本組）、`leaderboard: [{team, score}]`（已揭曉題）。
- 老師：`leaderboard`（同格式）。
