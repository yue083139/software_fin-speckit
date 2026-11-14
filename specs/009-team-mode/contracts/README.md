# 009 team-mode 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /api/teacher/team-play`（`{enabled}` ⇒ `{team_play}`；401／409 非 preparing／422）、`POST /api/student/draft`（`{question, answers}` ⇒ `{question}`；403／404／409／422，見 research R4）；`POST /api/student/join` 本體 `{team, code?}`，增 403 邀請碼不正確、409 此組裝置已滿；`/api/public/info` 增 `team_play`；老師 view 增 `team_play`、`devices`、`invite_codes`；學生 view 增 `team_play`、`invite_code`、`drafts`。全部只增不改。
