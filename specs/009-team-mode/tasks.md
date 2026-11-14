# Tasks: 組隊模式——一組多台裝置、代表作答

**Input**: `specs/009-team-mode/` 與 `diagrams/009-team-mode-*.puml`

## Phase 1: User Story 1 - 組隊開關與邀請碼加入 (P1) 🎯

### Tests

- [ ] T001 [P] [US1] `server/tests/test_team_mode.py`：開關 409、切換撤銷、邀請碼 403、上限 409、並發加入、釋放整組、組隊不改計分
- [ ] T002 [P] [US1] `web/src/pages/team.test.tsx`：老師組隊勾選、台數與邀請碼、首頁帶邀請碼加入

### Implementation

- [ ] T003 [US1] `activity.py` `team_play`、`set_team_play`、`join(team, code)`、`_codes`、`MAX_DEVICES`、`InviteCodeError`（時序圖前段）
- [ ] T004 [US1] `app.py` `POST /api/teacher/team-play`、join 本體 `code` 與 403；`views.py` 老師 `devices`、`invite_codes`，學生 `invite_code`，公開資訊 `team_play`
- [ ] T005 [US1] web：老師組隊勾選與台數／邀請碼、首頁邀請碼欄、學生頁邀請碼

## Phase 2: User Story 2 - 代表作答 (P1)

- [ ] T006 [P] [US2] `test_team_mode.py::test_concurrent_submit_same_team`、`test_member_sees_team_submission`
- [ ] T007 [US2] 送出成功後清除該組該題草稿

## Phase 3: User Story 3 - 組內草稿 (P2)

- [ ] T008 [P] [US3] `test_team_mode.py::test_draft_rules`；`test_isolation.py` 組隊負例三則
- [ ] T009 [US3] `activity.py` `drafts`、`set_draft`；`app.py` `POST /api/student/draft`；`views.py` 學生 `drafts`
- [ ] T010 [US3] web：作答卡送草稿（400 毫秒）、顯示組內草稿與「套用」

## Phase N: Polish

- [ ] T011 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-017～M-019
- [ ] T012 圖碼一致核對、`make gate` 寫入 `verification.md`
- [ ] T013 人工驗證（`docs/manual-verification.md` 場次 E）
