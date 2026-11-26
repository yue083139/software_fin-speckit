# Feature Specification: 把搶答成功的答案寫回原 Guided Notes 的填空格

**Feature Branch**: `005-guided-notes-export`
**Created**: 2026-11-11
**Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
**Input**: User description: "把搶答成功的組別答案寫回原 Guided Notes 的填空格並匯出 xlsx"
**需求編號**：R-05｜**parity**：`docs/parity.md` §4 `guided-notes-export`｜**檔位**：S（Guided Notes 寫回口徑）
**圖表**：`diagrams/005-guided-notes-export-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師匯出寫好答案的 Guided Notes (Priority: P1)

搶答結束後，老師按「匯出 Guided Notes」下載 xlsx：每題搶答成功組別的答案寫在原題目的填空格，題組各子題寫在對應子題格；其他內容不變。老師再把檔案匯回 Google 試算表。

**Why this priority**: R-05 必做，也是活動的最終產物。

**Independent Test**: 三份夾具（single、group、variant）往返：作答格＝得主答案、其他非空格與合併範圍不變。

**Acceptance Scenarios**:

1. **Given** 第2組搶得單題範本第 3 題並答「位址」，**When** 匯出，**Then** 第 3 題作答格為「位址」。
2. **Given** 第1組搶得題組範本第 1 題並答「CPU」「作業系統」，**When** 匯出，**Then** 兩個作答格為「（1）CPU」「（2）作業系統」。
3. **Given** 作答格原為佔位符「______」，**When** 匯出，**Then** 佔位符被答案取代。
4. **Given** 某題無人搶答，**When** 匯出，**Then** 該題作答格與原檔相同。
5. **Given** 得主答案為「=1+1」，**When** 匯出，**Then** 作答格為文字「=1+1」，不是公式。

---

### User Story 2 - 只有老師、只在結束後可匯出 (Priority: P1)

**Acceptance Scenarios**:

1. **Given** 搶答中，**When** 老師要求匯出，**Then** 回 409。
2. **Given** 已結束，**When** 未帶老師金鑰要求匯出，**Then** 回 401。
3. **Given** 已結束，**When** 匯出兩次，**Then** 兩次都成功（原檔不被修改）。

### Edge Cases

- 中文檔名以 RFC 5987 `filename*` 傳遞：`<原檔名>-搶答結果.xlsx`；連結匯入者為「Google 試算表-搶答結果.xlsx」。
- 圖片、資料驗證、條件式格式等 openpyxl 不完整支援的元素可能遺失（README 註明）。
- 伺服器重啟即清空活動，老師應在結束後先匯出。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 匯出 MUST 以 002 匯入時保存的原檔與作答格位置寫回，MUST NOT 以題號推算座標。
- **FR-002**: 佔位符 MUST 以答案取代第一段底線；否則 MUST 寫成「標籤＋答案」。
- **FR-003**: 寫入的儲存格 MUST 為文字型別。
- **FR-004**: 作答格以外的儲存格內容與合併範圍 MUST 不變；無得主的題目 MUST 不寫。
- **FR-005**: 得主 MUST 經 `ScoringRule` 取得（`results.winning_answers`）。
- **FR-006**: `GET /api/teacher/export` MUST 需老師金鑰，且只在 `ended` 階段允許。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 三份夾具往返測試全綠，作答格以外內容與合併範圍完全相同（`test_guided_notes_export.py`）。
- **SC-002**: 真伺服器完整流程匯出檔中，題組答案在 G5、G6，第 3 題答案在 G11（`probes/results/2026-11-11-e2e-flow.txt`，座標為 group 範本解析結果）。

## Assumptions

- 回到 Google 試算表的方式為「檔案 → 匯入 → 上傳 → 取代試算表」；直接寫回需要 OAuth 憑證，不在本期範圍（`docs/parity.md` §3）。
