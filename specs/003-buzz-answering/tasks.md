# Tasks: 開放／結束搶答、以組送出、伺服器判定最快組、作答隔離

**Input**: `specs/003-buzz-answering/` 與 `diagrams/003-buzz-answering-*.puml`
**Tests**: 測試先行（憲章原則 V）。

## Phase 1: Setup

- [x] T001 server dev 依賴加 `pytest-timeout`，`timeout = 30`（WebSocket 等不到訊息時判紅而非掛起）

## Phase 2: Foundational

- [x] T002 `server/quiz_server/scoring.py`：`Submission`、`Ranked`、`ScoringRule`、`ClassicBuzzRule`（類別圖）
- [x] T003 [P] `server/tests/test_scoring.py`
- [x] T004 `conftest.py`：`ready_activity` 先匯入題目、`loaded_client`；001 測試改用（開始條件修改）

## Phase 3: User Story 1 - 各組搶答送出，最快者得題 (P1) 🎯 MVP

- [x] T005 [P] [US1] `server/tests/test_submit.py`：未開始 409、先送者得題、重複 409、壞憑證 403、題號 404、結束後 409、重置清空、並發 50 輪、同組並發
- [x] T006 [US1] `Activity.submit`（時序圖 activate 段）、`own_submissions`、`question`、`start` 前置條件、`reset` 清空
- [x] T007 [US1] `app.py` `/api/student/submit`、`AlreadySubmittedError` → 409
- [x] T008 [US1] `web/src/pages/AnswerForm.tsx`、`Student.tsx`、`api.ts` `studentSubmit`

## Phase 4: User Story 2 - 題組一次送出全部子題 (P1)

- [x] T009 [US2] `test_group_requires_all_slots`、`test_invalid_answers_are_422`；`clean_answers`
- [x] T010 [P] [US2] `web/src/pages/answer.test.tsx`（題組填滿才可送出、送出後鎖定）

## Phase 5: User Story 3 - 搶答結束前看不到他組作答狀況 (P1)

- [x] T011 [P] [US3] `server/tests/test_isolation.py`：三通道、0 則推播、冒用參數、非 ended 各階段、日誌
- [x] T012 [US3] `views.student_view` 隔離、`results.build`（ended 才揭曉）、`RequestValidationError` 處理器

## Phase N: Polish

- [x] T013 `contracts/api.md` 增補；`eval/acceptance/matrix.yaml` M-004、M-005
- [x] T014 變異實錄、圖碼一致核對、`make gate-pr` 寫入 `verification.md`
- [ ] T015 人工驗證（待負責人）

## Dependencies & Execution Order

T002 → US1 → US2（共用 submit）；US3 依賴 US1 的送出紀錄。
