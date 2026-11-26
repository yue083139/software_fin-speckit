# Tasks: 匯入題目敘述，開放作答後顯示給學生

**Input**: `specs/011-question-text/` 與 `diagrams/011-question-text-*.puml`

## Phase 0: 提案前置

- [x] T000 探針：四份夾具的表頭與題目欄逐列文字，原樣輸出 `probes/results/2026-11-26-question-text.txt`
- [x] T001 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T002 `docs/parity.md` §4 登記本卡、§5 記變更（與 OpenSpec 組同批）
- [x] T003 提案輪評審（紅隊＋架構雙通道，1 輪，與 OpenSpec 組同批）；藥方併入下一版；負責人裁定並批准契約（R3）

## Phase 1: User Story 1 - 匯入時讀取題目敘述 (P1) 🎯

### Tests

- [x] T010 [P] [US1] `server/tests/test_guided_notes_parse.py`：四份夾具逐子題 `prompt`；合成「無題目欄」「題組敘述縱向合併」負例
- [x] T011 [P] [US1] `test_guided_notes_export.py`、`test_google_sheets.py` 不改即綠（R4）

### Implementation

- [x] T012 [US1] `guided_notes.py` `QUESTION_ALIASES`、`_find_header` 找題目欄、`Slot.prompt`（類別圖）

## Phase 2: User Story 2 - 學生在搶答開始後看到題目 (P1)

### Tests

- [x] T020 [P] [US2] `server/tests/test_isolation.py`：`test_prompts_hidden_until_open`、`test_prompts_sequential_only_opened`、搶答中帶 `prompts` 的 payload 不含他組答案
- [x] T021 [P] [US2] `test_api_skeleton.py` 或同等：老師 view 任何階段帶 `prompts`、長度＝子題數
- [x] T022 [P] [US2] web `answer.test.tsx` 有敘述顯示、無敘述不留白；`results.test.tsx` 結果表顯示敘述

### Implementation

- [x] T023 [US2] `views.question_outline(a, teacher)` 依 R2 帶 `prompts`（時序圖）
- [x] T024 [US2] web `types.ts`、學生作答卡、老師題目清單與作答表、學生結果表

## Phase 3: Polish & 驗證

- [x] T030 `contracts/api.md`（負責人 2026-11-26 照傾向批准）、`eval/acceptance/matrix.yaml`（M-003 守門補、新增 M-021）
- [x] T031 文件：`docs/manual-verification.md` 場次 A 加「準備階段只見題號、開始後見敘述」
- [ ] T032 `make gate` 原樣輸出；逐圖核對寫入 `verification.md`
- [ ] T033 實作輪評審（雙通道 1 輪）
- [ ] T034 人工驗證（負責人，`docs/manual-verification.md` 場次 A）；`docs/parity.md` 狀態更新、`make gate-parity SIBLING=../software_fin-openspec` 綠
