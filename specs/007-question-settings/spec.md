# Feature Specification: 題目設定——雙倍分數題

**Feature Branch**: `007-question-settings`
**Created**: 2026-11-12
**Status**: Draft
**Input**: User description: "可選擇加入 double point question（負責人 2026-11-12 裁定列入第二期）"
**需求編號**：X-04（`docs/trd-game-modes.md` T-05 倍率）｜**parity**：`docs/parity.md` §4 `question-settings`｜**檔位**：S（`contracts/` 增端點；TRD §5 原建議 B，依分檔表「命中任一取最高」改 S）
**圖表**：`diagrams/007-question-settings-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師把題目設為雙倍分數 (Priority: P1)

匯入後、開始前，老師在題目清單勾選某題「雙倍分數」；老師與學生都看到該題的「雙倍分數」標記。

**Why this priority**: 對標 Kahoot Double points；任何模式都適用。

**Independent Test**: 勾選第 2 題 → 學生畫面第 2 題有標記；搶答中勾選回 409；重新匯入後全部回到 1 倍。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 老師把第 2 題設為雙倍，**Then** 老師與學生畫面第 2 題標「雙倍分數」。
2. **Given** 搶答中，**When** 老師設定倍率，**Then** 回 409，倍率不變。
3. **Given** 倍率為 3，**When** 老師設定，**Then** 回 422。
4. **Given** 第 2 題雙倍，**When** 老師重新匯入，**Then** 全部題目為 1 倍；**When** 改為結束後重置，**Then** 第 2 題仍為雙倍。

---

### User Story 2 - 雙倍題得分加倍 (Priority: P1)

任何模式下，雙倍題每筆得分為原本的兩倍，得主不變。分數欄名在「經典搶答且全部 1 倍」時為「得題數」，其餘為「得分」。

**Acceptance Scenarios**:

1. **Given** 經典模式第 2 題雙倍、第1組最先送出，**When** 結束，**Then** 第1組第 2 題得 2 分、欄名「得分」。
2. **Given** 只計對錯模式第 2 題雙倍、第1組被判正確，**When** 揭曉，**Then** 第1組第 2 題得 2 分。

### Edge Cases

- 倍率只有 1 與 2（Kahoot 也只有 ×2）。
- 倍率不寫回 Guided Notes，也不從 Guided Notes 讀取（TRD T-05）。
- 倍率不是他組資訊，學生看得到不違反作答隔離。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 老師 MUST 能在 `preparing` 把任一題倍率設為 1 或 2；其他階段 409、其他值 422、題號不存在 404。
- **FR-002**: 重新匯入 MUST 重設全部倍率為 1；重置活動 MUST 保留倍率。
- **FR-003**: 任何模式下倍率 2 的每筆得分 MUST 為倍率 1 的兩倍，得主 MUST 不變。
- **FR-004**: 老師與學生的題目清單 MUST 含每題倍率；分數欄名 MUST 由伺服器提供（`score_label`）。
- **FR-005**: 新增 `POST /api/teacher/question-settings`；`contracts/api.md` 只增不改。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 同一組送出紀錄在倍率 1 與 2 下，兩種規則每筆分數恰為兩倍（`test_multiplier_doubles`，TRD §4）。
- **SC-002**: 設定 API 的 401／404／409／422 各有測試。

## Assumptions

- 老師在開始前就決定哪些題雙倍；搶答中發現設錯，結束後重置重來。
