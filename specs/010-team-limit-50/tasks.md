---

description: "010-team-limit-50 的相依排序實作任務"
---

# Tasks: 組別上限提高至 50 組

**Input**: `specs/010-team-limit-50/` 內的 spec、plan、research、data-model、contracts 與 quickstart

**Tests**: 本卡為 S 檔，依門禁先於實作原則採 TDD；各故事先寫驗收並確認紅燈，再修改產品程式。

**Organization**: 任務依使用者故事分組；每個故事完成後均可用其獨立驗收單獨確認。

## Format: `[ID] [P?] [Story] Description`

- **[P]**：可與同階段其他標有 `[P]` 的任務平行處理，且不修改同一檔案
- **[Story]**：對應 `spec.md` 的 US1、US2、US3

## Phase 1: Setup（提案與契約前置）

**Purpose**: 先完成 S 檔提案批准與兩組一致性前置，未通過前不得修改凍結契約或產品程式。

- [x] T001 將 `team-limit-50` 卡與共用需求口徑同步到姊妹 repo，並更新 `docs/parity.md` 的同步狀態與證據
- [x] T002 依 S 檔流程完成提案輪紅隊與架構評審，將兩通道結論、藥方回驗及輪次記錄於 `specs/010-team-limit-50/verification.md`
- [x] T003 取得負責人對「`POST /api/teacher/teams` 合法範圍由 2–12 改為 2–50」的明確批准，將批准原文與日期補入 `specs/010-team-limit-50/contracts/api-change.md`
- [x] T004 依 `specs/010-team-limit-50/quickstart.md` 保存實作前 2–12 組既有回歸基線到 `specs/010-team-limit-50/verification.md`

**Checkpoint**: 必須依序完成 parity 同步、提案雙通道評審與負責人批准，才可進入紅燈驗收與實作。

---

## Phase 2: Foundational（共享約束）

**Purpose**: 先建立所有故事共用的單一上限來源與凍結契約口徑。

- [x] T005 將已批准的組數契約由 2–12 更新為 2–50，且保持端點、回應形狀、每組六台與錯誤語意不變於 `contracts/api.md`
- [x] T006 [P] 將產品說明中的組數合法範圍與大型班級行為更新為 2–50 於 `docs/product-trd.md`
- [x] T007 唯讀確認實作前 `server/quiz_server/activity.py` 仍為 `MIN_TEAMS=2`、`MAX_TEAMS=12`、`DEFAULT_TEAMS=4`、`MAX_DEVICES=6`，並把基線記錄於 `specs/010-team-limit-50/verification.md`，此任務不得修改產品程式

**Checkpoint**: 契約已批准並更新，產品常數仍保持實作前基線；後續由 US1 在紅燈後修改唯一的組數上限來源。

---

## Phase 3: User Story 1－老師為大型班級設定最多 50 組（Priority: P1）🎯 MVP

**Goal**: 老師可在準備階段設定 13 或 50 組，所有端點與畫面取得完整、唯一、依數字升序的組別清單，並可加入第 50 組。

**Independent Test**: 依序設定 13 與 50 組，確認老師與學生皆取得完整清單，並成功以第 13 組及第 50 組加入。

### Tests for User Story 1（先寫並確認紅燈）

- [x] T008 [P] [US1] 新增 `team_names(50)` 產生 50 個唯一且依數字升序名稱，以及 `configure_teams(2/12/13/50)` 成功的單元驗收於 `server/tests/test_phases.py`
- [x] T009 [P] [US1] 新增 `POST /api/teacher/teams` 對 2、12、13、50 回傳相同數量組名並廣播完整清單的契約驗收於 `server/tests/test_api_skeleton.py`
- [x] T010 [P] [US1] 新增第 13 組與第 50 組可取得有效身分並完成加入的整合驗收於 `server/tests/test_team_mode.py`
- [x] T011 [US1] 執行 US1 新增測試並把預期紅燈輸出記錄於 `specs/010-team-limit-50/verification.md`

### Implementation for User Story 1

- [x] T012 [US1] 依共用 `MAX_TEAMS=50` 讓 `Activity.configure_teams` 與 `team_names` 支援第 1 組至第 50 組，保持名稱唯一且依數字升序於 `server/quiz_server/activity.py`
- [x] T013 [US1] 執行 `server/tests/test_api_skeleton.py` 驗證 `TeamsBody` 與設定組數端點正確回傳、廣播 50 組清單；若已通過則在 `specs/010-team-limit-50/verification.md` 記錄 `server/quiz_server/app.py` 無須修改，若失敗則修正該檔並重跑至通過
- [x] T014 [US1] 執行 `server/tests/test_phases.py`、`server/tests/test_api_skeleton.py`、`server/tests/test_team_mode.py` 並將 US1 綠燈證據記錄於 `specs/010-team-limit-50/verification.md`

**Checkpoint**: 13 與 50 組可獨立設定、顯示與加入，US1 可作為 MVP 單獨驗收。

---

## Phase 4: User Story 2－邊界與既有活動規則維持安全（Priority: P1）

**Goal**: 只接受準備階段的 2–50 整數；失敗操作不改狀態，合法改組撤銷所有舊身分、邀請碼與草稿；50 組 × 6 台仍隔離且公平。

**Independent Test**: 對 1、2、50、51、無效格式及非準備階段逐一操作；再以 50 組各六台驗證容量、隔離與 20 輪同題並發。

### Tests for User Story 2（先寫並確認紅燈）

- [x] T015 [P] [US2] 新增 1、51、非整數、格式無效皆回 422 且活動狀態不變，以及非 preparing 回 409 且狀態不變的契約驗收於 `server/tests/test_api_skeleton.py`
- [x] T016 [US2] 新增合法改為 50 組時全部 `_tokens`、`_codes`、`drafts` 清除且舊 token 以最少資訊失效的驗收於 `server/tests/test_team_mode.py`
- [x] T017 [US2] 新增 50 組各六台共 300 台可保持有效身分、第 301 台加入已滿組別回 409、第 50 組釋放後可重入的驗收於 `server/tests/test_team_mode.py`
- [x] T018 [P] [US2] 新增 50 組活動中逐組檢查學生 payload 不含其他 49 組答案、無效身分 fail-closed 的負例驗收於 `server/tests/test_isolation.py`
- [x] T019 [P] [US2] 新增 50 組同題並發重複 20 次皆順位無重號且恰一組成功、只採伺服器接收序的驗收於 `server/tests/test_submit.py`
- [x] T020 [US2] 執行 US2 新增測試並把預期紅燈或既有保護已綠的逐項結果記錄於 `specs/010-team-limit-50/verification.md`

### Implementation for User Story 2

- [x] T021 [US2] 修正設定組數的邊界、階段拒絕與原子清除行為，使「整數且 `2 <= count <= 50`；合法改組清除全部 tokens、codes、drafts；拒絕時狀態不變」完整落於 `server/quiz_server/activity.py`
- [x] T022 [US2] 檢查並僅在測試揭露缺陷時修正 50 組下的學生 view fail-closed 裁切，禁止任何學生 payload 含其他組答案於 `server/quiz_server/views.py`
- [x] T023 [US2] 執行容量探針，記錄環境、300/300 最終一致、p95 與最慢送達時間，將實作後證據另存於 `probes/results/2026-11-27-team-limit-50-capacity-implementation.txt`，不得覆寫 Phase 0 原始結果
- [x] T024 [US2] 執行 US2 五個測試檔、三種遊戲模式既有回歸與容量探針，將 SC-002、SC-003、SC-004、SC-006、SC-007 證據記錄於 `specs/010-team-limit-50/verification.md`

**Checkpoint**: 50 組容量不改變每組六台上限，隔離、公平、狀態原子性及既有模式全部通過。

---

## Phase 5: User Story 3－50 組下仍可完成老師與學生操作（Priority: P2）

**Goal**: 選組、組別管理與結果畫面保留全部 50 組，可在桌面與 768 px 寬視窗捲動找到並操作第 50 組。

**Independent Test**: 在一般桌面與 768 px 寬度完成第 50 組選取、加入、釋放、作答及結果定位，均不需瀏覽器縮放且不超過 30 秒。

### Tests for User Story 3（先寫並確認紅燈）

- [x] T025 [US3] 新增 50 組選組、老師管理、結果清單皆完整呈現且第 50 組可操作的元件驗收於 `web/src/pages/team-limit.test.tsx`
- [x] T026 [US3] 執行 `web/src/pages/team-limit.test.tsx` 並把預期紅燈輸出記錄於 `specs/010-team-limit-50/verification.md`

### Implementation for User Story 3

- [x] T027 [P] [US3] 調整學生選組清單保留並可捲動至第 50 組於 `web/src/pages/Home.tsx`
- [x] T028 [P] [US3] 調整老師組數輸入、範圍提示與 50 組管理清單於 `web/src/pages/Teacher.tsx`
- [x] T029 [P] [US3] 調整結果檢視完整保留並可定位第 50 組於 `web/src/pages/Results.tsx`
- [x] T030 [US3] 補足選組、管理與結果容器在桌面及 768 px 寬度的捲動與可操作樣式於 `web/src/styles.css`
- [x] T031 [US3] 執行 `web/src/pages/team-limit.test.tsx`、既有 web 測試與 build，將 US3 綠燈結果記錄於 `specs/010-team-limit-50/verification.md`

**Checkpoint**: 50 組的三個主要 UI 流程可獨立驗收，且第 50 組沒有被截斷或靜默省略。

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: 完成驗收矩陣、人工驗證、圖碼一致性與 S 檔門禁證據。

- [x] T032 [P] 對照 component、class、sequence 三圖逐項核對實作元件、類別約束與訊息序，將含 `path:line` 錨點的結論寫入 `specs/010-team-limit-50/verification.md`
- [x] T033 [P] 依 `specs/010-team-limit-50/quickstart.md` 在一般桌面與 768 px 視窗人工完成第 50 組加入、釋放、作答與結果定位，將驗證者、日期、測試環境、逐步操作、實際觀察、每項耗時及截圖證據記錄於 `specs/010-team-limit-50/verification.md`
- [x] T034 將 M-020、M-021、M-022 的實際驗收落點與狀態由 `uncovered` 更新為 `covered` 於 `eval/acceptance/matrix.yaml`
- [x] T035 執行 `make gate-diagrams`、`make gate-parity SIBLING=../software_fin-openspec`、`make gate`，把原樣輸出與任何有意不改項目記錄於 `specs/010-team-limit-50/verification.md`
- [x] T036 匯出本卡 AI 對話紀錄並登記於 `docs/ai-logs/010-team-limit-50.md`
- [x] T037 依 S 檔流程完成實作輪紅隊與架構評審，將兩通道結論、藥方回驗及「都綠否」逐項狀態寫入 `specs/010-team-limit-50/verification.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 Setup**：立即開始，且必須依序執行 T001 → T002 → T003；T003 完成前禁止修改 `contracts/api.md` 或產品程式，T004 可在批准後保存基線。
- **Phase 2 Foundational**：依賴 T003；T005 依賴契約批准，T007 僅記錄未修改的產品基線。
- **US1（Phase 3）**：依賴 T005、T007；先完成 T008–T011 紅燈，再做 T012–T014。
- **US2（Phase 4）**：依賴 Phase 2；可與 US1 的測試設計平行，但 T021–T024 應在共用常數與契約完成後執行。
- **US3（Phase 5）**：依賴 50 組 API 行為可用；T027–T029 可平行，T030 整合其樣式需求。
- **Polish（Phase 6）**：依賴所有欲交付故事完成；T034 需等故事驗收全綠，T035 後才可送 T037 實作輪評審。

### User Story Dependencies

```text
Setup／Foundational
        |
        +--> US1（50 組設定與加入，MVP）
        |
        +--> US2（邊界、撤銷、300 連線、隔離與公平）
                    |
                    +--> US3（50 組 UI 操作）
                              |
                              +--> Polish／完整門禁與評審
```

- **US1（P1）**：不依賴其他故事，完成後即能展示 50 組基本流程。
- **US2（P1）**：不依賴 US1 的 UI，但共用同一服務端常數；需在完整交付前通過。
- **US3（P2）**：依賴服務端可回傳與操作 50 組，否則元件測試只能使用合成資料。

### Parallel Opportunities

- T008、T009、T010 修改不同測試檔，可平行起草。
- T015–T019 中，T016 與 T017 同為 `test_team_mode.py` 且須依序；T015、T018、T019 修改其他測試檔，可與它們平行。
- T027、T028、T029 修改不同頁面，可平行；T030 在三者需求確定後整合。
- T032 與 T033 可平行蒐集證據。

## Parallel Examples

### User Story 1

```text
Task T008: server/tests/test_phases.py 的 50 組模型驗收
Task T009: server/tests/test_api_skeleton.py 的設定組數契約驗收
Task T010: server/tests/test_team_mode.py 的第 13／50 組加入驗收
```

### User Story 2

```text
Task T015: server/tests/test_api_skeleton.py 的邊界與狀態不變驗收
Task T018: server/tests/test_isolation.py 的 50 組隔離負例
Task T019: server/tests/test_submit.py 的 20 輪並發公平驗收
```

### User Story 3

```text
Task T027: web/src/pages/Home.tsx 的選組清單
Task T028: web/src/pages/Teacher.tsx 的組別管理
Task T029: web/src/pages/Results.tsx 的結果定位
```

## Implementation Strategy

### MVP First（User Story 1）

1. 依序完成 T001–T003 的 parity、提案雙通道評審與批准，再完成 T004–T007 的基線、契約與文件工作；此時不得把 `MAX_TEAMS` 改為 50。
2. 完成 T008–T011 並保存紅燈證據。
3. 完成 T012–T014，獨立驗證 13 與 50 組設定、顯示及加入。
4. 停下驗證 MVP；未通過時不進入 US2／US3。

### Incremental Delivery

1. **US1**：交付 50 組基本設定與加入。
2. **US2**：補齊拒絕原子性、撤銷、300 連線、隔離與公平保證。
3. **US3**：交付桌面與窄視窗的完整 50 組操作。
4. **Polish**：完成圖碼核對、人工紀錄、parity、全量門禁與雙通道評審。

## Notes

- 所有產品測試必須先於對應實作完成，並在 `verification.md` 留下紅燈與綠燈證據。
- 2 秒只作效能觀測目標；300/300 最終一致、隔離、每組六台與並發公平仍是阻塞驗收。
- `contracts/api.md` 是凍結件，T003 未取得明確批准前不得執行 T005。
- 不得把真實學生資料、作答或憑證放入測試、探針與 AI 紀錄。
