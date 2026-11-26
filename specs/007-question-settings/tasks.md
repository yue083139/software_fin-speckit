# Tasks: 題目設定——雙倍分數題

**Input**: `specs/007-question-settings/` 與 `diagrams/007-question-settings-*.puml`

## Phase 1: User Story 1 - 老師把題目設為雙倍分數 (P1) 🎯

### Tests

- [x] T001 [P] [US1] `server/tests/test_question_settings.py`：錯誤碼、匯入清除、重置保留、學生看得到倍率
- [x] T002 [P] [US1] `web/src/pages/settings.test.tsx`：勾選呼叫 API、非準備階段停用、學生標記

### Implementation

- [x] T003 [US1] `scoring.py` `QuestionAttrs`；`Activity.attrs`、`set_question`（時序圖前段）
- [x] T004 [US1] `app.py` `POST /api/teacher/question-settings`；`views.py` `multiplier`
- [x] T005 [US1] web：老師勾選框、學生「雙倍分數」標記

## Phase 2: User Story 2 - 雙倍題得分加倍 (P1)

- [x] T006 [P] [US2] `server/tests/test_scoring.py::test_multiplier_doubles`；改寫 `test_reserved_inputs_do_not_change_classic`；`test_score_label`
- [x] T007 [US2] 兩種規則乘倍率；`results.py` 傳入 attrs；`score_label`
- [x] T008 [US2] web：結果畫面每題標倍率、欄名用 `score_label`

## Phase N: Polish

- [x] T009 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-013
- [x] T010 圖碼一致核對、`make gate` 寫入 `verification.md`
- [ ] T011 人工驗證（待負責人）
