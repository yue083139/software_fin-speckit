# Data Model: 018-results-podium

無伺服器資料模型變更。前端新增衍生型別（只在畫面計算，不送伺服器）：

| 型別 | 欄位 | 說明 |
|---|---|---|
| `PodiumPlace` | `rank: 1 \| 2 \| 3` | 名次（同分同名次、下一名跳號） |
| | `score: number` | 該名次的分數（> 0） |
| | `teams: string[]` | 並列該名次的組別，依伺服器組別順序 |

來源：結束後 view 的 `team_scores: Record<string, number>`（既有欄位）。
