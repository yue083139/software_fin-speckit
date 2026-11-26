# Tasks: 經典搶答結束後依順位「答對／答錯」檢查，匯出改寫選定答案

**Input**: `specs/012-answer-review/` 與 `diagrams/012-answer-review-*.puml`

## Phase 0: 提案前置

- [x] T000 現行行為以原始碼引述為證（research 背景段）；`git grep -n 搶答結果 -- :/` 全列，R6 逐點改或登記有意不改
- [x] T001 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [ ] T002 `docs/parity.md` §4 `answer-review` 已由 `question-text` 批登記（取代 `mode-buzz-fallback`）；合流時把兩列「-搶答結果」改為「_作答情況」
- [x] T003 提案輪評審（紅隊 0B/2M/3m、架構 0B/1M/3m，皆 0 阻斷，與 OpenSpec 組同批）；藥方併入 v1.1；負責人 2026-11-26 裁未決事項並批准契約

## Phase 1: User Story 1 - 依順位檢查 (P1) 🎯

### Tests

- [x] T010 [P] [US1] `server/tests/test_scoring.py`：新增判錯遞補、判對鎖定、全部判錯；**改寫** `test_judgments_do_not_change_classic` → `test_classic_without_judgments_unchanged`、`test_classic_correct_is_none` → `test_classic_correct_reflects_review`（原斷言即本卡推翻的口徑）
- [x] T011 [P] [US1] `server/tests/test_review.py`：錯誤碼與先後；連點負例；重設；推播
- [ ] T012 [P] [US1] （移到 `web-workbench` 整合）`web/src/pages/results.test.tsx`：只有候選列有「答對」「答錯」；鎖定顯示「已鎖定」「重設本題」；全部答錯顯示「全部答錯，無得主」

### Implementation

- [x] T013 [US1] `scoring.py` `ClassicBuzzRule.rank` 讀判定（R1）
- [x] T014 [US1] `activity.py` `review`、`review_reset`、`review_candidate`（R2、R3）
- [x] T015 [US1] `app.py` 兩端點（R2）
- [ ] T016 [US1] （移到 `web-workbench` 整合）web：`api.ts`、`types.ts`、`Results.tsx`、`Teacher.tsx` 接線

## Phase 2: User Story 2 - 學生結果同步 (P1)

- [x] T020 [P] [US2] `server/tests/test_results_view.py`：檢查後老師 `board` 與學生 `results` 一致；`test_isolation.py` 既有非 ended 負例不改即綠

## Phase 3: User Story 3 - 匯出與檔名 (P1)

- [x] T030 [P] [US3] `server/tests/test_google_sheets.py` copy 名稱「_作答情況」；`test_api_google.py::test_reexport_restores_previously_written_cells`（v1.1 寫回範圍）
- [x] T031 [P] [US3] `server/tests/test_api_export.py`：xlsx 為檢查後得主；全部判錯同原檔；檔名 `group_作答情況.xlsx`
- [x] T032 [US3] `google_sheets.py` `COPY_SUFFIX`、`write_answers(restore=)`；`activity.py` `sheet_written`；`app.py` `export_filename`、匯出鎖（R5、R6）
- [ ] T033 [US3] （移到 `web-workbench` 整合）`web/src/pages/ImportPanel.tsx` 副本名稱文案

## Phase 4: Polish

- [x] T040 `contracts/api.md`（負責人批准後）
- [x] T041 `eval/acceptance/matrix.yaml`：M-005、M-006、M-008 更新；新增 M-022
- [x] T042 文件：`README.md`、`docs/requirements.md` §4（負責人對 R-10／R-05 的解讀）、`docs/manual-verification.md` 場次 A 第 15a～15c、16、18 步
- [x] T043 `make gate` 原樣輸出、圖碼一致核對寫入 `verification.md`
- [ ] T044 實作輪評審（雙通道 1 輪）
- [ ] T045 人工驗證（負責人，場次 A）；`docs/parity.md` 狀態更新、`make gate-parity SIBLING=../software_fin-openspec` 綠
