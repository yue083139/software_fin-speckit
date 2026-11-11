# Tasks: 老師即時作答狀況與結果、學生結束後檢視結果

**Input**: `specs/004-results-view/` 與 `diagrams/004-results-view-*.puml`

## Phase 1: Foundational

- [x] T001 `results.team_scores`（經規則）

## Phase 2: User Story 1 - 老師即時看作答狀況 (P1) 🎯

- [x] T002 [P] [US1] `test_results_view.py::test_teacher_board_live`、`test_teacher_board_empty_before_import`
- [x] T003 [US1] `views.teacher_view` 加 `board`、`team_scores`
- [x] T004 [US1] `web/src/pages/Results.tsx` `Board`、`Teacher.tsx` 接入

## Phase 3: User Story 2 - 學生結束後看結果 (P1)

- [x] T005 [P] [US2] `test_student_results_only_when_ended`
- [x] T006 [US2] `views.student_view` ended 加 `team_scores`
- [x] T007 [US2] `StudentResults`、`Student.tsx` 接入；`results.test.tsx`

## Phase 4: User Story 3 - 一致性 (P2)

- [x] T008 [US3] `test_teacher_and_student_agree`

## Phase N: Polish

- [x] T009 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-007、M-008
- [x] T010 圖碼一致核對、`make gate-pr` 寫入 `verification.md`
- [ ] T011 人工驗證（待負責人）
