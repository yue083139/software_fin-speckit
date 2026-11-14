# Verification: 009 team-mode（v1.1）

## 圖碼一致核對（憲章原則 VII）

| 圖 | 圖上元素／訊息 | 程式落點 | 結果 |
|---|---|---|---|
| component | TeamSettings 組隊勾選・台數・邀請碼 | `web/src/pages/Teacher.tsx`「組隊（一組多台裝置）」 | 一致 |
| component | Home 邀請碼輸入欄 | `web/src/pages/Home.tsx` `TeamPicker` | 一致 |
| component | AnswerForm 草稿 400 ms・「套用」 | `web/src/pages/AnswerForm.tsx` `DRAFT_DELAY_MS`、「套用」 | 一致 |
| component | api.ts `joinTeam(team, code)`・`studentDraft` | `web/src/api.ts` | 一致 |
| component | app.py 三端點 | `server/quiz_server/app.py` `/api/teacher/team-play`、`/api/student/join`（`JoinBody.code`）、`/api/student/draft` | 一致 |
| class | `Activity.team_play`、`_codes`、`drafts`、`set_team_play`、`join(team, code)`、`release`、`start`、`devices`、`invite_code`、`set_draft` | `server/quiz_server/activity.py` | 一致 |
| class | `InviteCodeError` 403、`TeamTakenError` 409、`AnswerError` 422 | `activity.py`；`app.py` `_bad_code` | 一致 |
| class | `student_view` 的 `invite_code` 只在 preparing、`drafts` 只在 answering | `server/quiz_server/views.py` | 一致 |
| sequence | 第一台加入產生碼 → 無碼 403 → 帶碼加入 | `activity.join` 分支順序 | 一致 |
| sequence | start 換新所有邀請碼 | `activity.start`「開始搶答即換新邀請碼」 | 一致 |
| sequence | 草稿只推本組、第2組不推送 | `views.student_view`＋ws「只在本連線 view 改變時才送」；`test_other_team_draft_sends_nothing` | 一致 |
| sequence | B 送出 → 清草稿 → A 收推播；A 再送 409 | `activity.submit`；`test_member_sees_team_submission` | 一致 |
| sequence | release 換新碼、舊碼 403 | `activity.release`；`test_release_revokes_all_devices_and_code` | 一致 |

偏離：無。

## 契約語意補充（待負責人批准）

見 research R7。組隊關閉時與 001 相同（001 的加入測試未改仍綠）。

## 門禁原樣輸出（2026-11-14，本機 Windows）

```
$ make gate SIBLING=../software_fin-openspec
All checks passed!
All checks passed!
227 passed, 1 warning in 36.76s
51 passed in 6.67s
 Test Files  7 passed (7)
      Tests  33 passed (33)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 28 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 28 個圖檔語法通過
gate-parity: 0 處不一致
```

變異實錄：程式與測試和 OpenSpec 組逐字相同，八則變異見 `openspec/changes/team-mode/verification.md`（OpenSpec repo）。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 場次 E 執行，結果回填本段）。

結果：＿＿＿（執行人／日期／看到什麼）
