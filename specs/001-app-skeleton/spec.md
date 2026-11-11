# Feature Specification: 前後端骨架、身分進場與活動階段同步

**Feature Branch**: `001-app-skeleton`
**Created**: 2026-11-11
**Status**: Implemented（人工驗證待負責人）
**Input**: User description: "前後端骨架、老師與學生身分（組別憑證）、活動階段狀態機與 WebSocket 同步"
**需求編號**：R-01、R-11（`docs/requirements.md`）｜**parity**：`docs/parity.md` §4 `app-skeleton`｜**檔位**：S
**圖表**（憲章原則 VII）：`diagrams/system-component.puml`、`diagrams/001-app-skeleton-component.puml`、`diagrams/001-app-skeleton-class.puml`、`diagrams/001-app-skeleton-sequence.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師與學生以不同身分進場 (Priority: P1)

老師以伺服器啟動時產生的老師金鑰進入老師頁；學生在首頁選擇組別，取得伺服器發出的組別憑證後進入學生頁。每組同時只能有一台裝置。

**Why this priority**: 所有後續功能都以「誰是老師、誰是哪一組」為前提（R-01），且作答隔離依賴伺服器能可靠辨識組別。

**Independent Test**: 啟動伺服器後，開老師頁與兩個學生分頁，確認各自看到正確身分；以錯誤金鑰或偽造憑證連線只拿到最少資訊。

**Acceptance Scenarios**:

1. **Given** 伺服器已啟動，**When** 學生在首頁選「第2組」，**Then** 學生頁顯示所屬組別「第2組」與目前階段。
2. **Given** 第1組已有裝置加入，**When** 另一台裝置再選第1組，**Then** 伺服器回 409，直到老師釋放第1組。
3. **Given** 任一狀態，**When** 未帶或帶錯老師金鑰呼叫老師端 API，**Then** 回 401 且活動狀態不變。
4. **Given** 任一狀態，**When** 學生連線未帶、帶錯或帶已撤銷的組別憑證（含只改網址上的組別名稱），**Then** 只收到階段與「組別無效」標記，不收到任何組別或老師端資料。

---

### User Story 2 - 活動階段同步給所有使用者 (Priority: P1)

老師開始、結束、重置活動時，所有已連線的老師與學生畫面同步切換階段。

**Why this priority**: R-11「同步所有使用者的活動階段」是核心必做。

**Independent Test**: 三個分頁連線，老師切換階段，三者都收到新階段。

**Acceptance Scenarios**:

1. **Given** 準備階段且開始條件成立，**When** 老師按「開始搶答」，**Then** 所有連線收到 `answering`。
2. **Given** 準備階段，**When** 要求「結束搶答」，**Then** 回 409，階段維持 `preparing`。
3. **Given** 準備階段，**When** 同時送出多個「開始搶答」，**Then** 恰一個成功，其餘回 409。
4. **Given** 經典模式，**When** 老師結束搶答，**Then** 階段由 `answering` 直接到 `ended`（不經 `judging`）。

---

### User Story 3 - 老師設定組數與管理組別 (Priority: P2)

老師在準備階段設定 2 到 12 組，看見哪些組已加入，並可釋放某組讓新裝置加入。

**Why this priority**: 課堂組數不固定；裝置故障時需要老師介入。

**Independent Test**: 老師設定 5 組後首頁出現第1組到第5組；釋放某組後該組舊憑證失效。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 老師設定 5 組，**Then** 所有使用者收到含第1組到第5組的狀態，且所有既有組別憑證撤銷。
2. **Given** 搶答階段，**When** 老師設定組數，**Then** 回 409。

### Edge Cases

- 他組任何動作若不改變本連線的畫面內容，本連線**不得**收到推播（推播時機本身會透露他組活動）。
- 學生分頁關閉後憑證隨分頁消失，需老師釋放該組才能重新加入。
- 伺服器重啟即清空活動（第一期不做快照，`docs/parity.md` §2）。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 提供老師與學生兩種身分；老師 MUST 以啟動時產生的老師金鑰驗證（REST 標頭 `X-Teacher-Key`、WebSocket 參數 `key`）。
- **FR-002**: 學生 MUST 經 `POST /api/student/join` 取得組別憑證；每組同時 MUST 只發給一台裝置；伺服器 MUST 由憑證反查組別，MUST NOT 採信客戶端自報的組別名稱。
- **FR-003**: 活動階段 MUST 為 `preparing`、`answering`、`judging`、`ended` 之一，且只能依轉移表改變；`judging` 為遊戲模式預留，經典模式不經過。
- **FR-004**: 階段變更 MUST 推送給所有已連線使用者；每條連線 MUST 只在自己的畫面內容改變時才收到訊息，訊息序號為每連線各自遞增。
- **FR-005**: 老師 MUST 能在準備階段設定 2–12 組、釋放某組；改組數 MUST 撤銷全部組別憑證。
- **FR-006**: 伺服器終端機輸出 MUST NOT 含組別憑證；老師金鑰只出現在啟動時印出的老師頁網址。
- **FR-007**: 介面契約 MUST 記錄於 `contracts/api.md`（兩組共用，之後只增不改語意）。

### Key Entities

- **Activity（活動）**：唯一狀態來源；階段、組別、組別憑證、版本號。
- **Phase（階段）**：`preparing`／`answering`／`judging`／`ended`。
- **Team Token（組別憑證）**：隨機字串 → 組別；一組一個。
- **View（畫面狀態）**：依身分裁切後推給單一連線的資料。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 老師切換階段後，所有連線在同一次推播收到新階段（`test_phase_sync_all_clients`）。
- **SC-002**: 同時 20 次開始請求恰 1 次成功；同組 10 次並發加入恰 1 次成功；拿掉活動鎖時兩測試皆失敗（變異實錄）。
- **SC-003**: 偽造憑證、改網址組別參數的連線收到的內容等於最少資訊 view（`test_bad_token_gets_minimal_view`）。
- **SC-004**: 真伺服器（uvicorn）運行時終端機輸出含 `token=` 的行數為 0（`probes/results/2026-11-11-e2e-flow.txt`）。

## Assumptions

- 只在本機模擬（需求 §1），老師與學生都是同一台或同一區網的瀏覽器分頁。
- 課堂互信：老師金鑰由老師自行保管；本功能不做帳號系統。
