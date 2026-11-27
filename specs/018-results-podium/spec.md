# Feature Specification: 活動結束後顯示前三名領獎台

**Feature Branch**: `018-results-podium`
**Created**: 2026-11-27
**Status**: Approved（v1.0，評審 CLEARED、已合入 `dev` SpecKit #40；與 OpenSpec 組 `openspec/changes/archive/2026-11-27-results-podium/` 同批）
**Input**: 負責人 2026-11-27 同意成員自行開卡（「你有想改的可以拉出去改」「兩個專案都一起改這樣才有同步」）；成員提議「揭曉後顯示前三名領獎台」。
**需求編號**：R-04、R-08、X-04｜**parity**：`docs/parity.md` §4 `results-podium`｜**檔位**：B（只改 web 畫面）
**圖表**：`diagrams/018-results-podium-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師結束後一眼看出前三名 (Priority: P1)

活動結束後，老師頁「作答狀況與結果」上方出現領獎台，亞軍、冠軍、季軍由左到右，冠軍台最高，標示組別與分數。

**Why this priority**: 揭曉是課堂搶答的高潮；現在只有表格，看不出誰贏，Demo 也缺收尾畫面。

**Independent Test**: 以假 view（`phase: "ended"`、`team_scores`）渲染 `TeacherPanel`，領獎台第 1 名為分數最高的組；`phase: "answering"` 時不出現。

**Acceptance Scenarios**:

1. **Given** 活動結束，第2組 3 分、第3組 2 分、第1組 1 分，**When** 老師看結果，**Then** 由左到右為第 2 名第3組、第 1 名第2組、第 3 名第1組，並顯示分數。
2. **Given** 活動在搶答中，**When** 老師看老師頁，**Then** 不顯示領獎台。
3. **Given** 經典搶答結束，**When** 老師把某題得主檢查為答錯，**Then** 領獎台依新的分數即時更新。

### User Story 2 - 學生看到本組名次 (Priority: P2)

學生結束後的結果頁在「搶答結果」下方看到同一個領獎台，本組旁有「本組」標籤。

**Why this priority**: 讓各組知道自己有沒有上台，提升參與感（X-04）。

**Independent Test**: 渲染 `StudentResults`（`team="第2組"`），第 1 名的第2組旁有「本組」，其他名次沒有。

**Acceptance Scenarios**:

1. **Given** 第2組學生在結束後檢視結果、第2組第 1 名，**When** 看領獎台，**Then** 第 1 名的第2組旁顯示「本組」。

### Edge Cases

- 同分同名次、下一名跳號（1、1、3）；同名次依組別順序。
- 三組並列第 1 ⇒ 沒有第 2、3 名；第 3 名並列 ⇒ 全部上台。
- 0 分不上台；所有組別 0 分 ⇒ 不顯示領獎台。
- 重置活動回準備階段 ⇒ 領獎台消失。

## Requirements *(mandatory)*

- **FR-001**: 活動結束後，老師畫面與學生結果畫面 MUST 顯示前三名領獎台（亞軍、冠軍、季軍由左到右）。
- **FR-002**: 名次 MUST 同分同名次、下一名跳號，同名次依組別順序；名次大於 3 與 0 分 MUST NOT 上台。
- **FR-003**: 沒有任何組別得分時 MUST NOT 顯示領獎台；結束前 MUST NOT 顯示。
- **FR-004**: 學生畫面 MUST 標出本組。
- **FR-005**: 領獎台 MUST 只使用結束後 view 既有的 `team_scores`；MUST NOT 新增伺服器欄位或改變送往學生端的資料。

## Success Criteria *(mandatory)*

- **SC-001**: `web/src/pages/podium.test.tsx` 13 例全綠，web 連跑兩次；拿掉「結束後才顯示」判斷時紅。
- **SC-002**: 伺服器、`contracts/` 無變更（`git diff origin/dev -- server contracts` 為空）。
