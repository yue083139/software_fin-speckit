# Data Model: 002 guided-notes-import

對照 `diagrams/002-guided-notes-import-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Slot` | `sheet`、`cell`、`label`、`placeholder`、`display` | 一個作答格；`cell` 來自解析（非程式常數） |
| `Question` | `number`、`slots` | `len(slots) ≥ 2` 即題組（X-01） |
| `ParsedNotes` | `sheet`、`questions` | 解析結果 |
| `Activity`（新增） | `notes`、`source_bytes`、`source_name` | 匯入當下的原檔與檔名，供 005 寫回 |

View 新增欄位：老師 `source`、`questions`；學生 `questions`。`questions[] = {number, labels}`，`labels` 長度＝子題數，單題為 `[""]`。
