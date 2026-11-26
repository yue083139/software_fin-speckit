# Data Model: 005 guided-notes-export

無新增實體。使用 002 的 `Slot`（`sheet`、`cell`、`label`、`placeholder`）與 `Activity.source_bytes`、`Activity.notes`，以及 003 的 `ScoringRule` 得主。

`winning_answers(a) -> {題號: (子題1答案, 子題2答案, …)}`；無得主的題目不在其中。
