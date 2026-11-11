# Data Model: 003 buzz-answering

對照 `diagrams/003-buzz-answering-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Submission` | `team`、`question`、`answers`、`seq`、`elapsed_ms` | 送出紀錄；`seq` 為順位唯一依據 |
| `Ranked` | `team`、`answers`、`seq`、`rank`、`is_winner`、`score` | 規則輸出 |
| `Activity`（新增） | `rule`、`submissions`、`_seq`、`_started_at` | 匯入、重置時清空 |

學生 view 新增：`my_submissions: [{question, answers}]`（所有階段，只有本組）；`ended` 時 `results: [{number, labels, ranking, winner}]`。
