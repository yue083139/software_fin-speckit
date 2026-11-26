# 009 team-mode 介面契約

於 [`/contracts/api.md`](../../../contracts/api.md) **新增** `POST /api/teacher/team-play`（`{enabled}` ⇒ `{team_play}`；401／409 非 preparing／422）、`POST /api/student/draft`（`{question, answers}` ⇒ `{question}`；403／404／409／422，見 research R4）；`/api/public/info` 增 `team_play`；老師 view 增 `team_play`、`devices`、`invite_codes`；學生 view 增 `team_play`、`invite_code`（只在 preparing）、`drafts`（只在 answering）。

**語意補充（v1.1，負責人 2026-11-14 批准，見 research R7）**：身分表一組多台；`POST /api/student/join` 本體 `{team, code?}`、403 邀請碼不正確、組隊時 409 指已滿；`release` 組隊時撤銷全部裝置、清草稿並換新碼；`teams` 另清除邀請碼與草稿。組隊關閉時與 001 相同。
