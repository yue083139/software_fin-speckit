# Feature Specification: 遊戲模式框架、判定階段與「只計對錯」模式

**Feature Branch**: `006-game-mode-framework`
**Created**: 2026-11-12
**Status**: Draft（v1.1，提案輪評審後）
**Input**: User description: "參考 Kahoot 等成熟搶答軟體做多種模式；老師判定對錯，匯入檔有參考答案欄時預填建議（負責人 2026-11-12 裁定 TRD §6）"
**需求編號**：X-04（`docs/trd-game-modes.md` T-01～T-04、T-06、M3）｜**parity**：`docs/parity.md` §4 `game-mode-framework`｜**檔位**：S（活動階段狀態機、作答隔離、Guided Notes 解析口徑、`contracts/`）
**圖表**：`diagrams/006-game-mode-framework-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師在開始前選擇模式 (Priority: P1)

老師在準備階段從「經典搶答」（預設）與「只計對錯」中選一種；老師與學生畫面都顯示目前模式與一行規則說明。

**Why this priority**: 所有第二期模式的入口；經典搶答行為必須不變。

**Independent Test**: 選「只計對錯」後兩邊畫面顯示模式名稱；搶答中切換回 409；經典模式跑完第一期全部測試不改即綠。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 老師選「只計對錯」，**Then** 老師與學生畫面顯示「只計對錯」。
2. **Given** 搶答中，**When** 老師切換模式，**Then** 回 409，模式不變。
3. **Given** 模式鍵不存在，**When** 老師切換，**Then** 回 422。
4. **Given** 只計對錯模式已結束，**When** 老師重置活動，**Then** 模式仍為只計對錯。

---

### User Story 2 - 老師判定每筆送出再揭曉 (Priority: P1)

只計對錯模式下，老師按「結束搶答」後進入「判定中」；作答狀況表每格有「正確／錯誤」兩鈕，可改判；全部判定完才能按「揭曉結果」。正確者各得 1 分；每題得主＝最早送出的正確答案，匯出寫回它。

**Why this priority**: Guided Notes 沒有標準答案，依對錯計分的模式都需要老師判定（TRD §6 裁定）。

**Independent Test**: 兩組作答 → 結束 → 判定中 → 有未判定時揭曉 409 → 判完揭曉 → 學生看到對錯與分數。

**Acceptance Scenarios**:

1. **Given** 只計對錯模式搶答中，**When** 老師結束搶答，**Then** 階段變為 `judging`。
2. **Given** 判定中尚有 1 筆未判定，**When** 老師揭曉，**Then** 回 409 並指出未判定筆數，階段不變。
3. **Given** 判定中，**When** 老師呼叫結束搶答，**Then** 回 409，階段維持 `judging`。
4. **Given** 第 1 題第1組先送出被判錯、第2組後送出被判對，**When** 揭曉並匯出，**Then** 得主為第2組、第2組 1 分第1組 0 分、匯出寫回第2組答案。
5. **Given** 某題全部判錯，**When** 揭曉並匯出，**Then** 該題無得主、作答格不變。
6. **Given** 判定中老師判第1組正確，**When** 檢視第2組收到的內容，**Then** 第2組沒有收到任何訊息，畫面不含第1組答案與判定結果。

---

### User Story 3 - 參考答案預填判定建議 (Priority: P2)

匯入的 Guided Notes 若有參考答案欄（參考答案／正確答案／標準答案／解答／Answer Key），判定畫面每格顯示建議；老師按「採用全部建議」才寫入「尚未判定且有建議」者，不覆蓋已判定的。參考答案與建議永不送往學生。

**Why this priority**: 降低老師判定成本；沒有參考答案欄也能完整使用 US2。

**Independent Test**: 以 `reference.xlsx` 匯入，走完四個階段，學生收到的全部內容不含任何參考答案字串；採用建議只填未判定者。

**Acceptance Scenarios**:

1. **Given** 表頭為「題號／題目／作答／參考答案」，**When** 匯入，**Then** 每個子題的參考答案＝同列參考答案欄內容。
2. **Given** 課程單題範本（無參考答案欄），**When** 匯入，**Then** 成功且所有子題無參考答案。
3. **Given** 3 筆未判定、其中 2 筆有建議，**When** 採用全部建議，**Then** 那 2 筆依建議判定，另 1 筆仍未判定。
4. **Given** 老師已判某筆正確而建議為錯誤，**When** 採用全部建議，**Then** 該筆仍為正確。

### Edge Cases

- 建議比對＝NFKC、去所有空白、不分大小寫後全等；題組任一子題不同即建議錯誤；任一子題缺參考答案即無建議。不做同義詞比對，靠老師改判。
- 參考答案欄的合併範圍只取錨點列；空白視為沒有參考答案。
- 經典模式結束仍直接到 `ended`；`judging` 只能經揭曉到 `ended`。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 提供 `classic`（經典搶答，預設）與 `accuracy`（只計對錯）兩種模式，只能在 `preparing` 切換，重置保留。
- **FR-002**: 經典模式的送出、順位、結果、匯出 MUST 與 001–005 行為相同。
- **FR-003**: 結束搶答 MUST 只在 `answering` 允許；判定模式 MUST 轉 `judging`，經典模式轉 `ended`。
- **FR-004**: `judging` MUST 只能經揭曉轉 `ended`，且揭曉 MUST 要求沒有未判定的送出。
- **FR-005**: 只計對錯模式 MUST 正確 1 分、錯誤 0 分；得主 MUST 為依伺服器接收序最早的正確送出，無人答對無得主。003 的「順位 1 的組別為搶答成功者」自本功能起只適用經典模式（v1.1）。
- **FR-006**: 系統 MUST 可選讀取參考答案欄並產生判定建議；建議 MUST NOT 自動成為判定。
- **FR-007**: 在 `ended` 前（含 `judging`），學生 MUST NOT 收到他組答案、是否送出、順位或判定結果；任何階段學生 MUST NOT 收到參考答案或建議。
- **FR-008**: 老師結果與學生結果 MUST 由同一函式產生，老師版只多老師專屬欄位。
- **FR-009**: 新增 `POST /api/teacher/mode`、`/judge`、`/accept-suggestions`、`/reveal`；`contracts/api.md` 只增不改。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 第一期全部既有測試在本功能後只因新增欄位而更新斷言，行為相關斷言不改即綠。
- **SC-002**: 學生端四個階段的全部傳輸位元組不含任何參考答案字串（`test_reference_never_sent_to_students`）。
- **SC-003**: 拿掉 `reveal` 的未判定檢查、拿掉 `end` 的 `answering` 前置條件，對應測試必紅（變異實錄）。

## Assumptions

- 參考答案欄由老師自行加在 Guided Notes 上；課程範本沒有此欄（`probes/results/2026-11-11-guided-notes-structure.txt`）。
