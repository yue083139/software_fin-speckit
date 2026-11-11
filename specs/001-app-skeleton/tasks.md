# Tasks: 前後端骨架、身分進場與活動階段同步

**Input**: `specs/001-app-skeleton/`（spec、plan、research、data-model）與 `diagrams/001-app-skeleton-*.puml`
**Tests**: 憲章原則 V 要求測試先行，每個使用者故事先寫測試。

## Format: `[ID] [P?] [Story] Description`

## Phase 1: Setup

- [x] T001 建立 `server/pyproject.toml`（FastAPI、uvicorn、websockets、openpyxl、python-multipart、httpx；dev：pytest、pytest-timeout、ruff）
- [x] T002 [P] 建立 `web/`（package.json、vite.config.ts 代理 `/api`、`/ws`、tsconfig、eslint）
- [x] T003 [P] Makefile 增加 `dev`、`web-install`，`test`／`lint` 納入 server 與 web；CI 安裝依賴
- [x] T004 [P] `server/CLAUDE.md`、`web/CLAUDE.md` 元件規範；`make sync-agents`

## Phase 2: Foundational

- [x] T005 `server/tests/conftest.py`（測試用老師金鑰、TestClient fixture）
- [x] T006 `server/quiz_server/phases.py`（類別圖 Phase、TRANSITIONS、PhaseError）
- [x] T007 `contracts/api.md` 首建（身分、列舉、端點、訊息外框）

## Phase 3: User Story 1 - 老師與學生以不同身分進場 (P1) 🎯 MVP

### Tests

- [x] T008 [P] [US1] `server/tests/test_api_skeleton.py`：老師金鑰 401／4401、加入一次 409、釋放後可再加入且舊憑證失效、無效憑證最少資訊
- [x] T009 [P] [US1] `server/tests/test_phases.py::test_concurrent_join_same_team_once`

### Implementation

- [x] T010 [US1] `activity.py` `join`、`release`、`team_of`、`joined_teams`（類別圖 Activity）
- [x] T011 [US1] `views.py` `teacher_view`、`student_view`、`view_for`
- [x] T012 [US1] `app.py` `/api/student/join`、`/api/teacher/release`、老師金鑰相依、WebSocket 驗證（時序圖前半）
- [x] T013 [US1] `web/src/pages/Home.tsx`（選組加入、憑證存 sessionStorage）、`api.ts`

## Phase 4: User Story 2 - 活動階段同步給所有使用者 (P1)

### Tests

- [x] T014 [P] [US2] `test_phases.py` 轉移表窮舉、並發 start、`judging` 預留但經典不經過
- [x] T015 [P] [US2] `test_api_skeleton.py` 三連線同步、每連線 seq 遞增、非法轉移 409

### Implementation

- [x] T016 [US2] `activity.py` `start`、`end`、`reset`、`_checkpoint`、`_bump`
- [x] T017 [US2] `app.py` WebSocket 每連線送出迴圈（view 相同就不送；時序圖 par 段）
- [x] T018 [US2] `web/src/live.ts`（斷線重連、4401 不重連）、`Student.tsx`、`Teacher.tsx` PhaseControls

## Phase 5: User Story 3 - 老師設定組數與管理組別 (P2)

- [x] T019 [US3] `test_api_skeleton.py` 設定組數廣播並撤銷憑證、搶答中 409、超出範圍 422
- [x] T020 [US3] `activity.configure_teams`、`/api/teacher/teams`、`Teacher.tsx` TeamSettings（釋放按鈕）
- [x] T021 [P] [US3] `web/src/pages/pages.test.tsx`

## Phase N: Polish & Cross-Cutting

- [x] T022 `__main__.py`：印老師頁網址、uvicorn `log_level="warning"`
- [x] T023 變異實錄（鎖換成 `nullcontext`）結果寫入 `verification.md`
- [x] T024 圖碼一致核對表寫入 `verification.md`（憲章原則 VII 實作階段）
- [x] T025 `make gate-pr` 原樣輸出寫入 `verification.md`
- [ ] T026 人工驗證（待負責人，步驟見 `verification.md`）

## Dependencies & Execution Order

- Phase 1 → Phase 2 → US1 → US2 → US3；US2 的 WebSocket 推播依賴 US1 的憑證反查。
- [P] 任務為不同檔案、可並行。
