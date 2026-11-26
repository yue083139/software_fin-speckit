# Data Model: 007 question-settings

對照 `diagrams/007-question-settings-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `QuestionAttrs`（新） | `multiplier: int = 1` | 1 或 2；008 增 `time_limit` |
| `Activity`（增） | `attrs: dict[題號, QuestionAttrs]` | 匯入重建、重置保留 |

view 增欄位：`questions[].multiplier`（老師與學生）、`results[].multiplier`／`board[].multiplier`；`score_label` 規則改為「經典且全部 1 倍 ⇒ 得題數」。
