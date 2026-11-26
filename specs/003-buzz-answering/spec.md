# Feature Specification: 開放／結束搶答、以組送出、伺服器判定最快組、作答隔離

**Feature Branch**: `003-buzz-answering`
**Created**: 2026-11-11
**Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
**Input**: User description: "老師開啟／結束搶答、各組以組為單位送出答案、伺服器以接收序判定最快組、搶答結束前作答隔離"
**需求編號**：R-03、R-06、R-07、R-09、R-10（X-01 題組同時送出）｜**parity**：`docs/parity.md` §4 `buzz-answering`｜**檔位**：S
**圖表**：`diagrams/003-buzz-answering-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 各組搶答送出，最快者得題 (Priority: P1)

老師匯入題目後開始搶答；全部題目同時開放，各組任選題目送出答案；每組每題只能送出一次；伺服器依接收先後判定，最先送出的組別為該題搶答成功者。

**Why this priority**: R-03、R-06、R-07、R-10 是搶答活動本體。

**Independent Test**: 兩組對同一題先後送出，先送出者為得主；並發送出時恰一組順位 1。

**Acceptance Scenarios**:

1. **Given** 尚未匯入題目，**When** 老師按開始，**Then** 回 409。
2. **Given** 準備階段，**When** 學生送出，**Then** 回 409 且不記錄。
3. **Given** 搶答中，**When** 第2組先、第1組後送出第 3 題，**Then** 第 3 題得主為第2組。
4. **Given** 搶答中，**When** 四組同時送出同一題，**Then** 順位 1 到 4 不重複，恰一組為得主。
5. **Given** 第1組已送出第 3 題，**When** 再送出第 3 題，**Then** 回 409，第一次的答案不變。
6. **Given** 老師已結束搶答，**When** 學生送出，**Then** 回 409。

---

### User Story 2 - 題組一次送出全部子題 (Priority: P1)

題組的所有子題必須同一次送出，順位以整題計（X-01）。

**Acceptance Scenarios**:

1. **Given** 第 1 題有 2 個子題，**When** 只送出 1 個答案，**Then** 回 422 且不記錄。
2. **Given** 任一題，**When** 答案空白、超過 200 字或含控制字元，**Then** 回 422 且不記錄。

---

### User Story 3 - 搶答結束前學生看不到他組作答狀況 (Priority: P1)

搶答結束前，學生只看得到自己組送出的內容；看不到他組答案、他組是否送出、順位。

**Why this priority**: R-09 是公平性的前提；洩漏多發生在畫面以外的傳輸內容。

**Independent Test**: 第1組送出獨特字串，擷取第2組收到的所有 WebSocket 訊息與 REST 回應原文，不含該字串；第2組在第1組送出時收到 0 則訊息。

**Acceptance Scenarios**:

1. **Given** 搶答中第1組送出「甲組祕密答案」，**When** 檢查第2組的 WebSocket、送出成功回應、錯誤回應，**Then** 都不含該字串。
2. **Given** 搶答中，**When** 第1組送出，**Then** 第2組連線不收到任何訊息。
3. **Given** 第2組裝置把連線參數改為第1組但沒有第1組憑證，**When** 連線，**Then** 只收到最少資訊。
4. **Given** 老師結束搶答，**When** 第2組查看，**Then** 可看到其他組答案。

### Edge Cases

- 未帶或帶錯組別憑證送出 ⇒ 403，不採信請求內任何組別名稱。
- 請求本體格式錯誤 ⇒ 422 且錯誤訊息不回顯本體（FastAPI 預設會回顯）。
- 日誌只記組別、題號、序號，不記答案。
- `judging` 階段（遊戲模式預留）同樣不含他組資料。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 開始搶答 MUST 以已匯入題目為前提（修改 001 的開始條件）。
- **FR-002**: 學生 MUST 以 `X-Team-Token` 送出 `{question, answers}`；伺服器 MUST 由憑證反查組別。
- **FR-003**: 每組每題 MUST 只能送出一次；題組 MUST 一次送出全部子題；答案去頭尾空白後 MUST 非空、≤ 200 字、不含控制字元。
- **FR-004**: 順位 MUST 依伺服器在活動鎖內配發的遞增序號；MUST NOT 採信客戶端時間；並發送出 MUST 恰一組順位 1。
- **FR-005**: 判定 MUST 經 `ScoringRule` 策略產生（經典規則：序號最小者得 1 分），簽名預留判定結果與題目屬性輸入（`docs/trd-game-modes.md` T-02）。
- **FR-006**: 除 `ended` 以外的所有階段，學生 view MUST 只含本組送出（題號與答案），MUST NOT 含順位、序號、他組是否送出；他組送出 MUST NOT 觸發本組推播。
- **FR-007**: 送出成功回應 MUST 只回本組這筆；錯誤回應 MUST 為固定文字，不回顯答案或請求本體。

### Key Entities

- **Submission**：組別、題號、答案（tuple）、序號、自開始起的伺服器毫秒數（時間計分預留）。
- **Ranked**：組別、答案、序號、順位、是否得主、分數。
- **ScoringRule / ClassicBuzzRule**：判定規則策略。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 4 組同時送出同一題 50 輪，每輪序號＝1..4 且恰一組得主；同組同題並發 10 次恰 1 次成功；拿掉鎖時兩者皆失敗（變異實錄）。
- **SC-002**: 第2組在搶答中收到的所有傳輸內容不含第1組答案（`test_isolation.py`）。
- **SC-003**: 第1組送出後老師結束，第2組下一則訊息的 seq 恰為前一則＋1（中間 0 則推播）。
- **SC-004**: 真伺服器上第2組在第1組送出後 1 秒內收到 0 則訊息（`probes/results/2026-11-11-e2e-flow.txt`）。

## Assumptions

- 「最快」以伺服器接收為準，不補償網路延遲（本機模擬）。
- 經典規則不判對錯：最快但寫錯的答案仍是得主（R-10 字面意義）；錯誤遞補屬第二期 `mode-buzz-fallback`。
