# Feature Specification: 老師即時作答狀況與結果、學生結束後檢視結果

**Feature Branch**: `004-results-view`
**Created**: 2026-11-11
**Status**: Implemented（人工驗證待負責人）
**Input**: User description: "老師即時檢視作答狀況與結果、學生在搶答結束後檢視結果"
**需求編號**：R-04、R-08｜**parity**：`docs/parity.md` §4 `results-view`｜**檔位**：S（新增送往學生端的資料）
**圖表**：`diagrams/004-results-view-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師即時看作答狀況 (Priority: P1)

老師頁顯示「題號 × 組別」表：每格為該組答案與順位，得主格醒目標示，表尾為各組得題數；有新的送出就即時更新。

**Why this priority**: R-04 必做；Demo 影片要同時展示多組狀況。

**Independent Test**: 兩組送出同一題，老師連線即時收到含答案、順位、得主的表。

**Acceptance Scenarios**:

1. **Given** 搶答中，**When** 第3組送出第 2 題，**Then** 老師畫面立即顯示第 2 題第3組的答案與順位。
2. **Given** 第 2 題已有兩組送出，**When** 老師查看，**Then** 順位 1 的組別標示為搶答成功，各組得題數正確。

---

### User Story 2 - 學生在搶答結束後看結果 (Priority: P1)

搶答結束後，學生看到每題得主組別與答案、本組答案與順位、全部組別答案，以及各組得題數；結束前沒有任何結果資料。

**Why this priority**: R-08 必做；同時是 R-09 的另一面（結束前不能有）。

**Acceptance Scenarios**:

1. **Given** 搶答中，**When** 檢查學生 view，**Then** 不含 `results` 與 `team_scores` 欄位。
2. **Given** 老師結束搶答，**When** 學生查看，**Then** 每題顯示得主與答案、本組順位、未搶答的題目顯示「沒有組別搶答」。

---

### User Story 3 - 老師與學生看到的結果一致 (Priority: P2)

**Acceptance Scenarios**:

1. **Given** 搶答結束，**When** 比較老師的 `board` 與學生的 `results`，**Then** 內容完全相同，`team_scores` 相同。

### Edge Cases

- 尚未匯入題目時老師表為空、各組 0 分。
- 學生畫面欄位在非 ended 階段「不存在」而非空陣列，避免前端誤判為「沒有結果」。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 老師 view MUST 在任何階段含 `board`（每題：題號、子題標籤、排名、得主）與 `team_scores`。
- **FR-002**: 學生 view MUST 只在 `ended` 含 `results` 與 `team_scores`。
- **FR-003**: `board`、`results`、`team_scores` MUST 由同一個函式經 `ScoringRule` 產生，不在 view、前端或匯出重算。
- **FR-004**: 前端 MUST 只顯示伺服器給的 `rank`、`is_winner`，不自行排序或判定。

### Key Entities

- **QuestionResult**：`number`、`labels`、`ranking[]`（組別、答案、順位、是否得主、分數）、`winner`。
- **team_scores**：組別 → 分數（經典規則＝得題數）。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 老師連線在每次送出後收到更新的 board（`test_teacher_board_live`）。
- **SC-002**: 學生 view 在 answering 不含結果欄位、ended 時與老師 board 逐字相同（`test_student_results_only_when_ended`、`test_teacher_and_student_agree`）。

## Assumptions

- 揭曉點是整場結束（R-08），不做每題揭曉（每題排行榜屬第二期 `mode-timed-scoring`）。
