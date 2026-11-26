# Data Model: 012 answer-review

對照 `diagrams/012-answer-review-class.puml`。

| 實體 | 欄位／方法 | 說明 |
|---|---|---|
| `Activity`（共用） | `judgments: dict[題號, dict[組別, bool]]` | 經典模式只在 `ended` 由 `review` 寫入；`_clear_answers`（重新匯入、重置）清空（R1、R3） |
| `Activity`（增） | `review(number, team, correct)` | 鎖內：模式 classic → 階段 ended → 題號 → 未鎖定 → 有候選 → `team`＝候選；寫入後 `_bump()`（R2） |
| `Activity`（增） | `review_reset(number)` | 鎖內：模式 → 階段 → 題號；清空該題判定、`_bump()`（R2） |
| `Activity`（增，唯讀） | `review_candidate(number) -> Ranked \| None` | 依規則取該題 `is_winner` 那列；供 `review` 比對候選 |
| `ClassicBuzzRule`（改） | `rank(submissions, judgments, attrs)` | 候選＝依 `seq` 第一個判定不為 `False` 者，得 1×倍率；`correct` 帶判定值；全部 `False` 無得主（R1） |
| `google_sheets`（改） | `COPY_SUFFIX = "_作答情況"`；`write_answers` 寫全部作答格 | 無得主者寫 `slot.label`（R5、R6） |
| `app`（改） | `export_filename` ⇒ `<stem>_作答情況.xlsx` | R6 |

老師與學生 view 不增欄位：鎖定＝候選 `correct === true`；全部答錯＝`winner === null` 且 `ranking` 每列 `correct === false`（R4）。
