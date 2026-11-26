# Data Model: 010 team-limit-50

對照 `diagrams/010-team-limit-50-class.puml`。本卡不新增持久化實體、欄位或狀態；只擴大既有 `Activity.teams` 的合法數量約束。

| 實體／值 | 現況 | 目標 | 不變約束 |
|---|---:|---:|---|
| `MIN_TEAMS` | 2 | 2 | 最少兩組 |
| `MAX_TEAMS` | 12 | 50 | 單一活動的組別總數上限 |
| `DEFAULT_TEAMS` | 4 | 4 | 新活動預設四組 |
| `MAX_DEVICES` | 6 | 6 | 組隊時每組最多六台；50 組組合上限 300 台 |
| `Activity.teams` | `第1組`…最多 `第12組` | `第1組`…最多 `第50組` | 名稱唯一、依數字升序、由伺服器產生 |
| `Activity._tokens` | token → 組別 | 不變 | 非組隊同組至多一筆；組隊同組至多六筆 |
| `Activity._codes` | 組別 → 邀請碼 | 不變 | 合法改組數時全部清除 |
| `Activity.drafts` | 組別 → 題號 → 草稿 | 不變 | 合法改組數時全部清除 |

## 驗證規則

- 組數必須是整數且 `2 <= count <= 50`；1、51 與格式錯誤拒絕，拒絕時活動狀態不變。
- 只有 `preparing` 可改組數；其他階段拒絕且狀態不變。
- 合法改組數時，不論擴大或縮小，所有 `_tokens`、`_codes`、`drafts` 都清除；現存前段組別也不保留舊身分。
- `team_names(50)` 必須依序產生 50 個唯一名稱，第 5 組與第 50 組以完整字串比對，不做前綴判斷。
- 每組裝置數仍由 token 筆數計算，不新增全活動裝置計數欄位；總數 300 是兩個既有上限的組合結果。

## 狀態轉換

```text
preparing + count ∈ [2, 50]
  → teams 取代為第1組…第N組
  → 撤銷全部 tokens、codes、drafts
  → 活動版本遞增並通知連線

preparing + count ∉ [2, 50] 或格式錯誤
  → 422；狀態不變

answering／judging／ended + 任一 count
  → 409；狀態不變
```

## View 影響

- 公開資訊：`teams` 最多 50 筆；不新增欄位。
- 老師 view：`teams`、`devices` 最多各 50 組；組隊時 `invite_codes` 最多 50 組；不含學生草稿。
- 有效學生 view：身分仍由 token 反查單一組別；搶答結束前只含本組答案／草稿。
- 無效學生 view：改組數後 token 失效，回最少資訊且 `team_valid=false`。
