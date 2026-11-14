# Data Model: 009 team-mode

對照 `diagrams/009-team-mode-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Activity`（增） | `team_play: bool = False` | 只在 preparing 改；改變時撤銷憑證與邀請碼；重置保留 |
| `Activity`（增） | `_codes: dict[組別, str]` | 6 碼邀請碼；第一台加入時產生；開始搶答與釋放時換新；改組數、切換組隊時刪除 |
| `Activity`（增） | `drafts: dict[組別, dict[題號, tuple[str, ...]]]` | 組內草稿，最後寫入者為準 |
| `Activity`（改） | `_tokens: dict[憑證, 組別]` | 組隊時同組可多筆（最多 `MAX_DEVICES = 6`） |
| `InviteCodeError`（新） | — | API 層轉 403 |

view 增欄位：老師 `team_play`、`devices`、`invite_codes`；學生 `team_play`、`invite_code`（只在 preparing）、`drafts`（只在 answering）；公開資訊 `team_play`。
