# Data Model: 006 game-mode-framework

對照 `diagrams/006-game-mode-framework-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Mode`（新） | `key`、`label`、`judged`、`rule` | `MODES`：`classic`（經典搶答，judged=False）、`accuracy`（只計對錯，judged=True） |
| `Ranked`（增） | `correct: bool \| None` | 經典為 `None`；只計對錯為老師判定，未判定 `None` |
| `Slot`（增） | `reference: str \| None` | 參考答案，只供老師與建議 |
| `Activity`（增） | `mode`、`judgments: dict[題號, dict[組別, bool]]` | 匯入、重置清空 `judgments`；重置保留 `mode` |

## 狀態轉移

| 目前 | 動作 | 經典 | 只計對錯 |
|---|---|---|---|
| `answering` | 結束搶答 | `ended` | `judging` |
| `judging` | 結束搶答 | — | 409 |
| `judging` | 揭曉（無未判定） | — | `ended` |
| `judging` | 揭曉（有未判定） | — | 409 |

## view 增欄位

- 老師：`mode: {key, label, judged}`、`modes: [{key, label}]`、`pending_judgments`、`score_label`；`board[].reference: [str|null]`、`board[].ranking[].correct`、`board[].ranking[].suggestion`。
- 學生：`mode: {key, label}`、`score_label`；`ended` 的 `results[].ranking[].correct`。不含 `reference`、`suggestion`。
