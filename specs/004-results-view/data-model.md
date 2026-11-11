# Data Model: 004 results-view

| 欄位 | 位置 | 說明 |
|---|---|---|
| `board` | 老師 view（任何階段） | `QuestionResult[]` |
| `team_scores` | 老師 view（任何階段）、學生 view（ended） | `{組名: 分數}` |
| `results` | 學生 view（ended） | 與 `board` 相同 |

`QuestionResult = {number, labels, ranking: [{team, answers, rank, is_winner, score}], winner: {team, answers} | null}`。
