# Data Model: 019-live-feed

無伺服器資料模型變更。前端新增衍生型別（只在畫面計算，不送伺服器）：

| 型別 | 欄位 | 說明 |
|---|---|---|
| `FeedEvent` | `key: string` | `<題號>-<組別>`，同 key 的通知只顯示一則 |
| | `text: string` | 「<組> 搶下第 N 題！」或「<組> 送出第 N 題」；不含答案 |

來源：老師 view 既有的 `board[].ranking[]`（`team`、`rank`）、`phase`、`mode.key`。
