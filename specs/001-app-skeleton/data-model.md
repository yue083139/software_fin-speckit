# Data Model: 001 app-skeleton

對照 `diagrams/001-app-skeleton-class.puml`。

## Activity（記憶體，單一實例）

| 欄位 | 型別 | 說明 |
|---|---|---|
| `phase` | `Phase` | 目前階段，預設 `preparing` |
| `teams` | `list[str]` | `第1組`…`第N組`，N ∈ [2, 12]，預設 4 |
| `version` | `int` | 每次狀態改變 +1；只在伺服器內部使用，不外露 |
| `_tokens` | `dict[str, str]` | 組別憑證 → 組別；同組至多一筆 |

## Phase 轉移表

| 從 | 可到 |
|---|---|
| `preparing` | `answering` |
| `answering` | `ended`、`judging`（預留） |
| `judging` | `ended` |
| `ended` | `preparing` |

## View（送出給單一連線）

- 老師：`{role, phase, teams, joined}`
- 學生（有效憑證）：`{role, phase, team, team_valid: true}`
- 學生（無效憑證）：`{role, phase, team: null, team_valid: false}`

WebSocket 訊息外框：`{type: "state", seq: <每連線遞增>, view}`。完整契約見 `/contracts/api.md`。
