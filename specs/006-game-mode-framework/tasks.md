# Tasks: 遊戲模式框架、判定階段與「只計對錯」模式

**Input**: `specs/006-game-mode-framework/` 與 `diagrams/006-game-mode-framework-*.puml`

## Phase 1: Setup

- [ ] T001 `tests/fixtures/guided-notes/build_reference.py` 與 `reference.xlsx`；加入 `ops/gate_parity.py` 共用檔、夾具 README

## Phase 2: User Story 1 - 老師在開始前選擇模式 (P1) 🎯

### Tests

- [ ] T002 [P] [US1] `server/tests/test_modes.py`：登記表、錯誤碼、重置保留（類別圖 Mode）

### Implementation

- [ ] T003 [US1] `server/quiz_server/modes.py`；`Activity.mode`、`rule` 屬性、`set_mode`
- [ ] T004 [US1] `app.py` `POST /api/teacher/mode`；`views.py` `mode`、`modes`、`score_label`
- [ ] T005 [US1] web：模式單選（`Teacher.tsx`）、學生模式說明（`Student.tsx`）

## Phase 3: User Story 2 - 老師判定每筆送出再揭曉 (P1)

### Tests

- [ ] T006 [P] [US2] `server/tests/test_scoring.py` `AccuracyRule` 表格式
- [ ] T007 [P] [US2] `server/tests/test_judging.py`：流程、錯誤碼、未判定 409、判定中結束 409、改判、並發（時序圖 alt）；變異實錄兩則
- [ ] T008 [P] [US2] `server/tests/test_isolation.py::test_judging_hides_judgments`；`test_results_view.py` 一致性兩模式；`test_guided_notes_export.py` 寫回最早答對者

### Implementation

- [ ] T009 [US2] `scoring.py` `Ranked.correct`、`AccuracyRule`
- [ ] T010 [US2] `Activity.end`（只接受 answering）、`judge`、`pending_judgments`、`reveal`
- [ ] T011 [US2] `results.build(teacher=)`；`app.py` `/judge`、`/reveal`
- [ ] T012 [US2] web：判定鈕、未判定數、揭曉鈕、結果對錯；`web/src/pages/judging.test.tsx`

## Phase 4: User Story 3 - 參考答案預填判定建議 (P2)

### Tests

- [ ] T013 [P] [US3] `server/tests/test_guided_notes_parse.py` 參考答案欄；`test_judging.py::test_suggest`、採用建議不覆蓋
- [ ] T014 [P] [US3] `server/tests/test_isolation.py::test_reference_never_sent_to_students`

### Implementation

- [ ] T015 [US3] `guided_notes.py` `REFERENCE_ALIASES`、`Slot.reference`；`judging.py`
- [ ] T016 [US3] `Activity.accept_suggestions`、`suggestion`；`app.py` `/accept-suggestions`；web「採用全部建議」與建議顯示

## Phase N: Polish

- [ ] T017 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-009～M-012、M-004 守門擴充
- [ ] T018 圖碼一致核對、`make gate` 寫入 `verification.md`
- [ ] T019 人工驗證（待負責人）
