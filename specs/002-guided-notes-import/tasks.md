# Tasks: 匯入 Guided Notes 並動態辨識題號、題組與作答格

**Input**: `specs/002-guided-notes-import/` 與 `diagrams/002-guided-notes-import-*.puml`
**Tests**: 測試先行（憲章原則 V）。

## Phase 1: Setup

- [x] T001 跑探針並存原樣輸出：`probes/results/2026-11-11-guided-notes-structure.txt`、`-openpyxl-writeback.txt`、`-sheets-export.txt`
- [x] T002 [P] `tests/fixtures/guided-notes/build_variant.py` 產生 `variant.xlsx`；夾具 README 更新

## Phase 2: Foundational

- [x] T003 `server/quiz_server/guided_notes.py` 資料類別 `Slot`、`Question`、`ParsedNotes`、`GuidedNotesError`（類別圖）

## Phase 3: User Story 1 - 老師上傳 xlsx 匯入題目 (P1) 🎯 MVP

### Tests

- [x] T004 [P] [US1] `server/tests/test_guided_notes_parse.py`：三份夾具、四種錯誤、別名整格比對、全形與英文別名
- [x] T005 [P] [US1] `server/tests/test_api_import.py`：上傳成功推播、壞檔 400、搶答中 409、需老師金鑰

### Implementation

- [x] T006 [US1] `guided_notes.parse_workbook`（R1–R3）
- [x] T007 [US1] `sources.check_upload`；`Activity.load_questions`、`require_preparing`；`/api/teacher/import`
- [x] T008 [US1] `web/src/pages/ImportPanel.tsx`、`Teacher.tsx` 接上傳

## Phase 4: User Story 2 - 老師貼 Google 試算表連結匯入 (P2)

- [x] T009 [P] [US2] `test_api_import.py`：連結改寫、拒收清單、Google 轉址、外部轉址被拒、私人試算表、5 MB、非準備階段 0 請求
- [x] T010 [US2] `sources.export_url`、`_allowed_hop`、`download_sheet`（時序圖 loop）；`/api/teacher/import-url`
- [x] T011 [US2] ImportPanel 連結輸入

## Phase 5: User Story 3 - 學生看到題號清單 (P3)

- [x] T012 [US3] `test_student_view_has_numbers_only`；`views.question_outline`；`Student.tsx` QuestionList；`pages.test.tsx`

## Phase N: Polish

- [x] T013 `contracts/api.md` 增補；`eval/acceptance/matrix.yaml` M-003
- [x] T014 SC-002 座標字面量 grep 原樣輸出、圖碼一致核對、`make gate-pr` 寫入 `verification.md`
- [ ] T015 人工驗證（待負責人）

## Dependencies & Execution Order

T003 → US1 → US2（共用解析）；US3 依賴 US1 的 view 欄位。
