# Tasks: Guided Notes 直接串接雲端 Google Sheets 讀寫

**Input**: `specs/010-guided-notes-sheets-sync/` 與 `diagrams/010-guided-notes-sheets-sync-*.puml`

## Phase 0: 提案前置

- [x] T000 負責人建 OAuth 用戶端（網頁應用程式、重新導向 `http://127.0.0.1:8000/api/google/callback`、「測試中」與測試使用者），`.env` 不入庫
- [x] T001 探針 `probes/google_sheets_probe.py` 原樣輸出 `probes/results/2026-11-17-google-sheets.txt`（四步皆 OK）
- [x] T002 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T003 提案輪評審（紅隊＋架構雙通道，1 輪，與 OpenSpec 組同批，皆 CLEARED 0 阻斷）；藥方併入 v1.2；負責人 2026-11-17 裁定並批准契約（R7）
- [x] T004 探針補 `openid email`、refresh 換新、撤銷（表單本體）三步；負責人重跑，輸出存 `probes/results/`，回填 R1 證偽欄

## Phase 1: User Story 1 - Google 登入 (P1) 🎯

### Tests

- [x] T010 [P] [US1] `server/tests/test_api_google.py`：登入網址含 PKCE、`prompt=consent`、cookie；回呼換權杖；state 偽造／過期／重放／cookie 不符 400、不回顯參數；無 refresh token 過期後 401；未設定 400；登出撤銷權杖在本體；錯誤碼先後；`httpx.MockTransport` 替身
- [x] T011 [P] [US1] `server/tests/test_isolation.py`：老師以假權杖完成登入、匯入、寫回、換新、登出（含撤銷失敗）後，學生 WebSocket／REST 與 caplog 不含權杖、授權碼、client secret

### Implementation

- [x] T012 [US1] `google_auth.py` `GoogleSession`（類別圖、時序圖「登入」段）
- [x] T013 [US1] `app.py` 四支 Google 端點；`__main__.py` 讀 `.env`
- [x] T014 [US1] web `GooglePanel.tsx`、`api.ts`；`google.test.tsx`

## Phase 2: User Story 2 - 從雲端試算表匯入 (P1)

- [x] T020 [P] [US2] `server/tests/test_google_sheets.py`：四份夾具轉 Sheets 格狀資料替身，解析與 xlsx 逐題相同；`effectiveValue` 題號負例；匯入請求序「標題 → copy → 讀副本」、解析失敗刪副本
- [x] T021 [P] [US2] `test_api_import.py`：刪公開下載測試；未登入 401、壞連結 400、搶答中 409，三者 0 次對外請求
- [x] T022 [US2] `guided_notes.py` `Grid`、`OpenpyxlGrid`、`parse_grids`
- [x] T023 [US2] `google_sheets.py` `import_copy`（標題 → copy → `read_grid`）、`SheetsGrid`；`sources.py` 刪下載；`activity.py` `source_sheet_id`
- [x] T024 [US2] web `ImportPanel.tsx` 改「從 Google 試算表匯入」（未登入停用）＋上傳 xlsx 備援

## Phase 3: User Story 3 - 寫回副本 (P1)

- [x] T030 [P] [US3] `test_google_sheets.py`：寫回只一次對副本的 batchUpdate、只含作答格、`RAW`、分頁名 `'` 跳脫；原檔 id 匯入後 0 次請求
- [x] T031 [P] [US3] `test_api_google.py`：export-sheet 401／409／502
- [x] T032 [US3] `google_sheets.write_answers`；`app.py` `POST /api/teacher/export-sheet`
- [x] T033 [US3] web 「匯出到 Google 試算表」、顯示副本連結；「下載 xlsx（備援）」

## Phase 4: User Story 4 - 題組子題填空格 (P2)

- [x] T040 [P] [US4] `test_guided_notes_parse.py`、`test_guided_notes_export.py`：group 子題 H 欄、G 欄標籤不變；single、variant 不變
- [x] T041 [US4] `guided_notes._parse_sheet` R5 規則

## Phase 5: Polish & 驗證

- [x] T050 `contracts/api.md`（負責人批准後）、`eval/acceptance/matrix.yaml`
- [x] T051 `ops/gate_secrets.py` 三種形狀＋變異實錄
- [x] T052 文件：`docs/requirements.md` §4、`docs/product-trd.md`、`README.md`、`.env.example`、`docs/manual-verification.md` 場次 A2、A5
- [x] T053 `make gate` 原樣輸出；逐圖核對寫入 `verification.md`
- [x] T054 真棧：`make dev` 實際登入、匯入、寫回一次，輸出存 `probes/results/`
- [ ] T055 人工驗證交組員；`docs/parity.md` 狀態更新、`make gate-parity SIBLING=../software_fin-openspec` 綠
