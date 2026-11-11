# Tasks: 把搶答成功的答案寫回原 Guided Notes 的填空格

**Input**: `specs/005-guided-notes-export/` 與 `diagrams/005-guided-notes-export-*.puml`

## Phase 1: User Story 1 - 老師匯出寫好答案的 Guided Notes (P1) 🎯

### Tests

- [x] T001 [P] [US1] `server/tests/test_guided_notes_export.py`：三份夾具往返、題組標籤、佔位符、無人搶答題、公式形式答案存文字

### Implementation

- [x] T002 [US1] `guided_notes.fill`、`write_answers`（時序圖 loop）
- [x] T003 [US1] `results.winning_answers`
- [x] T004 [US1] `web/src/api.ts` `teacherDownload`、`Teacher.tsx` 匯出鈕與「放回 Google 試算表」說明

## Phase 2: User Story 2 - 只有老師、只在結束後可匯出 (P1)

- [x] T005 [P] [US2] `server/tests/test_api_export.py`：寫回得主、檔名標頭、只在 ended、需老師金鑰、可重複匯出
- [x] T006 [US2] `app.py` `GET /api/teacher/export`、`export_filename`
- [x] T007 [P] [US2] `web/src/pages/results.test.tsx` 匯出鈕只在 ended 可按

## Phase N: Polish

- [x] T008 真棧探針 `probes/e2e_flow_probe.py` 與原樣輸出
- [x] T009 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-006；README 活動操作步驟
- [x] T010 圖碼一致核對、`make gate-pr` 寫入 `verification.md`
- [ ] T011 人工驗證（待負責人）
