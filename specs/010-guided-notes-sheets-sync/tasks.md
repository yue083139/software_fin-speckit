# Tasks: Guided Notes 直接串接雲端 Google Sheets 讀寫

**Input**: `specs/010-guided-notes-sheets-sync/` 與 `diagrams/010-guided-notes-sheets-sync-*.puml`

## Phase 0: 提案前置

- [x] T000 負責人建 OAuth 用戶端（網頁應用程式、重新導向 `http://127.0.0.1:8000/api/google/callback`、「測試中」與測試使用者），`.env` 不入庫
- [x] T001 探針 `probes/google_sheets_probe.py` 原樣輸出 `probes/results/2026-11-17-google-sheets.txt`（四步皆 OK）
- [x] T002 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [ ] T003 提案輪評審（紅隊＋架構雙通道，1 輪，與 OpenSpec 組同批）；負責人裁定未決事項並批准契約（R7）

## Phase 1: User Story 1 - Google 登入 (P1) 🎯

### Tests

- [ ] T010 [P] [US1] `server/tests/test_api_google.py`：登入網址含 PKCE 與 state；回呼換權杖；state 偽造／過期／重放 400；未設定 400；登出撤銷；`httpx.MockTransport` 替身
- [ ] T011 [P] [US1] `server/tests/test_isolation.py`：老師登入後學生 WebSocket／REST 與 caplog 不含權杖字串

### Implementation

- [ ] T012 [US1] `google_auth.py` `GoogleSession`（類別圖、時序圖「登入」段）
- [ ] T013 [US1] `app.py` 四支 Google 端點；`__main__.py` 讀 `.env`
- [ ] T014 [US1] web `GooglePanel.tsx`、`api.ts`；`google.test.tsx`

## Phase 2: User Story 2 - 從雲端試算表匯入 (P1)

- [ ] T020 [P] [US2] `server/tests/test_google_sheets.py`：三份夾具轉 Sheets 格狀資料替身，解析與 xlsx 逐題相同
- [ ] T021 [P] [US2] `test_api_import.py`：刪公開下載測試；未登入 401、壞連結 400、搶答中 409，三者 0 次對外請求
- [ ] T022 [US2] `guided_notes.py` `Grid`、`OpenpyxlGrid`、`parse_grids`
- [ ] T023 [US2] `google_sheets.py` `read_grid`、`SheetsGrid`；`sources.py` 刪下載；`activity.py` `source_sheet_id`
- [ ] T024 [US2] web `ImportPanel.tsx` 改「從 Google 試算表匯入」（未登入停用）＋上傳 xlsx 備援

## Phase 3: User Story 3 - 寫回副本 (P1)

- [ ] T030 [P] [US3] `test_google_sheets.py`：寫回請求一次 copy、一次 batchUpdate、只含作答格、`RAW`、分頁名跳脫；原檔 0 次寫入
- [ ] T031 [P] [US3] `test_api_google.py`：export-sheet 401／409／502
- [ ] T032 [US3] `google_sheets.copy_and_write`；`app.py` `POST /api/teacher/export-sheet`
- [ ] T033 [US3] web 「匯出到 Google 試算表」、顯示副本連結；「下載 xlsx（備援）」

## Phase 4: User Story 4 - 題組子題填空格 (P2)

- [ ] T040 [P] [US4] `test_guided_notes_parse.py`、`test_guided_notes_export.py`：group 子題 H 欄、G 欄標籤不變；single、variant 不變
- [ ] T041 [US4] `guided_notes._parse_sheet` R5 規則

## Phase 5: Polish & 驗證

- [ ] T050 `contracts/api.md`（負責人批准後）、`eval/acceptance/matrix.yaml`
- [ ] T051 `ops/gate_secrets.py` 三種形狀＋變異實錄
- [ ] T052 文件：`docs/requirements.md` §4、`docs/product-trd.md`、`README.md`、`.env.example`、`docs/manual-verification.md` 場次 A2、A5
- [ ] T053 `make gate` 原樣輸出；逐圖核對寫入 `verification.md`
- [ ] T054 真棧：`make dev` 實際登入、匯入、寫回一次，輸出存 `probes/results/`
- [ ] T055 人工驗證交組員；`docs/parity.md` 狀態更新、`make gate-parity SIBLING=../software_fin-openspec` 綠
