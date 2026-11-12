# Feature Specification: 時間計分模式——逐題開放、伺服器計時、每題揭曉後排行榜

**Feature Branch**: `008-mode-timed-scoring`
**Created**: 2026-11-12
**Status**: Draft
**Input**: User description: "可選擇加入「時間計分」（Kahoot 式）；排行榜每題揭曉後公開（負責人 2026-11-12 裁定）"
**需求編號**：X-04（`docs/trd-game-modes.md` M2、T-04、T-05 時限、§6 排行榜）｜**parity**：`docs/parity.md` §4 `mode-timed-scoring`｜**檔位**：S（判定口徑、作答隔離、階段狀態機、`contracts/`）
**圖表**：`diagrams/008-mode-timed-scoring-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 逐題開放、時間到伺服器自動關閉 (Priority: P1) 🎯

老師選「時間計分」並在準備階段設定每題時限（5–120 秒，預設 20）。開始後老師按「開放下一題」依題號順序開放；學生只看到進行中那一題與倒數；時間到伺服器關閉該題並推送，老師也可提早結束。

**Why this priority**: 作答秒數需要共同起點（T-04），所以題目必須逐題開放。

**Independent Test**: 假時鐘下開第 1 題 → 送第 2 題 409 → 時鐘到時限＋0.001 秒送出 409 → 計時器關閉後所有人收到 `closed`。

**Acceptance Scenarios**:

1. **Given** 第 1 題進行中，**When** 學生送出第 2 題，**Then** 回 409。
2. **Given** 第 1 題時限 20 秒，**When** 學生在開題後 20.001 秒送出，**Then** 回 409 且不記錄。
3. **Given** 第 1 題時限到，**When** 計時器觸發，**Then** 所有使用者收到第 1 題已關閉。
4. **Given** 所有已加入組別都送出第 1 題，**When** 時限未到，**Then** 第 1 題維持進行中（不因全員送出提早關閉，以免學生推知他組已送出）。
5. **Given** 時限設為 3 秒，**When** 老師設定，**Then** 回 422。

---

### User Story 2 - 每題判定後依時間計分並揭曉 (Priority: P1)

題目關閉後，老師判定每筆送出，全部判定後按「揭曉本題」。正確者得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（t ≤ 0.5 秒得 1000 × 倍率），錯誤與未作答 0 分；得主＝最早送出的正確答案。

**Acceptance Scenarios**:

1. **Given** 時限 30 秒、第1組 2 秒時送出且判正確，**When** 揭曉，**Then** 第1組該題 967 分。
2. **Given** 雙倍題、第1組 0.4 秒時送出且判正確，**When** 揭曉，**Then** 第1組該題 2000 分。
3. **Given** 第 1 題已關閉但未判完，**When** 老師揭曉，**Then** 回 409。
4. **Given** 第 1 題已關閉未揭曉，**When** 老師開放下一題或結束活動，**Then** 回 409。

---

### User Story 3 - 揭曉後公開排行榜，答案仍隔離 (Priority: P1)

每題揭曉後，學生看到本組該題對錯與得分、以及全部組別在已揭曉題目的累積排行榜；他組答案、順位、作答秒數在活動結束前一律看不到。

**Acceptance Scenarios**:

1. **Given** 第 1 題揭曉、第1組 967 分第2組 0 分，**When** 學生查看，**Then** 排行榜為第1組 967、第2組 0。
2. **Given** 第 1 題揭曉後，**When** 擷取第2組收到的全部內容，**Then** 不含第1組答案文字。
3. **Given** 第 2 題已判定未揭曉，**When** 學生查看排行榜，**Then** 只含第 1 題分數。

### Edge Cases

- 截止判斷在送出路徑以伺服器單調時鐘比對；計時器只決定何時推送「已關閉」，計時器晚到也不會多收。
- 學生倒數以 `deadline_epoch_ms − Date.now()` 顯示，只影響畫面；截止以伺服器為準。
- 未開放的題目沒有送出，結束後無得主、匯出不改。
- 重置或重新匯入取消計時器並清空回合。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 時間計分模式 MUST 依題號順序逐題開放，同時至多一題進行中，只接受進行中那一題的送出。
- **FR-002**: 作答秒數 MUST 為伺服器單調時鐘自開題起量測；超過時限的送出 MUST 回 409 且不記錄。
- **FR-003**: 時限到伺服器 MUST 關閉該題並推送；老師 MUST 能提早結束；MUST NOT 因全員送出而關閉。
- **FR-004**: 每題時限 MUST 可在 `preparing` 設為 5–120 秒（預設 20）。
- **FR-005**: 正確者分數 MUST 依上述公式（四捨五入，不用銀行家捨入），錯誤與未作答 0 分；得主 MUST 為最早正確送出。
- **FR-006**: 該題全部判定前 MUST NOT 能揭曉；前一題揭曉前 MUST NOT 能開放下一題或結束活動。
- **FR-007**: 揭曉後學生 MUST 看到本組該題對錯與得分、及已揭曉題目的累積排行榜；`ended` 前 MUST NOT 收到他組答案、順位或作答秒數。
- **FR-008**: 新增 `POST /api/teacher/open-next`、`/close-question`、`/reveal-question`；設定 API 增 `time_limit`；`contracts/api.md` 只增不改。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: TRD §4 三個數值案例（t＝0.4 ⇒ 1000；t＝T ⇒ 500；T＝30、t＝2 ⇒ 967）通過。
- **SC-002**: 拿掉送出路徑的截止比對，逾時測試必紅（變異實錄）。
- **SC-003**: 真 uvicorn 探針跑完一個回合，收到伺服器自動關閉的推播（`probes/results/` 原樣輸出）。

## Assumptions

- 本機模擬下網路延遲可忽略；作答秒數含學生端到伺服器的傳輸時間。
