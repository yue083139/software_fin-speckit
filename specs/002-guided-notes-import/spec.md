# Feature Specification: 匯入 Guided Notes 並動態辨識題號、題組與作答格

**Feature Branch**: `002-guided-notes-import`
**Created**: 2026-11-11
**Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
**Input**: User description: "匯入 Guided Notes（xlsx 或 Google 試算表連結），以表頭與合併範圍動態辨識題號、題組與作答格"
**需求編號**：R-02、X-01｜**parity**：`docs/parity.md` §4 `guided-notes-import`｜**檔位**：S（Guided Notes 解析口徑）
**圖表**：`diagrams/002-guided-notes-import-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師上傳 xlsx 匯入題目 (Priority: P1)

老師把 Google 試算表下載為 xlsx 後上傳；系統列出題號與每題子題數，題數與原檔一致，所有使用者同步看到題目清單。

**Why this priority**: R-02 必做；沒有題目就無法搶答。

**Independent Test**: 分別上傳官方單題範本、題組範本、自製變形檔，題目清單與檔案一致。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 上傳官方「題組＋單題」範本，**Then** 題目為 4 題，第 1、2 題各 2 個子題（標籤「（1）」「（2）」），第 3、4 題各 1 個。
2. **Given** 準備階段，**When** 上傳表頭在第 8 列、從 C 欄開始、欄名為「編號／答案」的檔案，**Then** 題數與每題作答格位置與檔案內容一致（5 題，子題數 1、3、1、2、1）。
3. **Given** 搶答階段，**When** 老師匯入，**Then** 回 409，題目不變。
4. **Given** 準備階段，**When** 上傳 .csv 或壞檔，**Then** 回 400 並說明原因，題目不變。

---

### User Story 2 - 老師貼 Google 試算表連結匯入 (Priority: P2)

老師貼上「知道連結者可檢視」的試算表連結，伺服器下載 xlsx 匯出版本並以同一規則解析。

**Why this priority**: Guided Notes 以 Google 試算表儲存（需求 §4），貼連結少一步下載。

**Independent Test**: 以替身傳輸層模擬 Google 回應：連結改寫、轉址、私人試算表、非 Google 主機。

**Acceptance Scenarios**:

1. **Given** 連結 `https://docs.google.com/spreadsheets/d/<id>/edit#gid=0`，**When** 匯入，**Then** 伺服器向 `…/d/<id>/export?format=xlsx&gid=0` 下載。
2. **Given** 非 https 或非 `docs.google.com` 的連結，**When** 匯入，**Then** 回 400 且不發出任何請求。
3. **Given** 下載途中被轉址到非 Google 網域，**When** 匯入，**Then** 中止並回 400，不對該主機發出請求。
4. **Given** 私人試算表（回傳登入頁），**When** 匯入，**Then** 回 400 提示改共用設定或改用上傳。

---

### User Story 3 - 學生在準備階段看到題號清單 (Priority: P3)

學生只看到題號與子題標籤，看不到題目敘述與作答格座標。

**Acceptance Scenarios**:

1. **Given** 已匯入，**When** 學生查看畫面，**Then** 依序列出題號與子題標籤，傳輸內容不含座標、檔名與題目敘述。

### Edge Cases

- 表頭寫法不在別名清單 ⇒ 400，訊息列出可用的表頭名稱。
- 題號重複、某題無作答格、表頭下沒有任何正整數題號 ⇒ 400 並指出題號。
- 題號欄寫成「第2題」「Q5」等非數字 ⇒ 該列不算題目（followup：匯入時提示略過列數）。
- 同一作答格內有多段底線 ⇒ 只算一個作答格（followup）。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 系統 MUST 接受 .xlsx 上傳（≤ 5 MB）與 Google 試算表連結兩種來源；只在準備階段允許。
- **FR-002**: 系統 MUST 以「整格等於」表頭別名（題號／編號／題次／No／No./#；作答／答案／回答／Answer，NFKC 正規化）定位題號欄與作答欄，逐工作表找第一個符合者。
- **FR-003**: 題號格（或其合併範圍左上角）為正整數即開始一題；該題列範圍＝題號格縱向合併範圍；範圍內每列作答欄（合併取左上角）為一個作答格；橫跨題號欄的合併列不是作答格。
- **FR-004**: 系統 MUST 記錄每個作答格的（工作表, 座標）、原有標籤與是否為佔位符（連續 3 個以上底線），供 005 寫回；解析程式 MUST NOT 含寫死的儲存格座標。
- **FR-005**: 連結匯入 MUST 只接受 https、`docs.google.com`、無自訂埠、`/spreadsheets/d/<id>` 且 id 符合 `[A-Za-z0-9_-]{20,}`；逐跳跟隨轉址且每跳限 `docs.google.com` 或 `*.googleusercontent.com`；串流讀取超過 5 MB 中止。
- **FR-006**: 匯入成功 MUST 取代題目、清空作答並推送給所有使用者；學生 view 只含題號與子題標籤。

### Key Entities

- **ParsedNotes**：工作表名稱＋題目序列。
- **Question**：題號＋作答格序列；作答格數 ≥ 2 即題組（X-01）。
- **Slot**：工作表、座標、標籤、是否佔位符、給學生看的顯示標籤。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 三份版面不同的夾具（single、group、variant）解析結果的題數、子題數與作答格位置全部正確（`test_guided_notes_parse.py`）。
- **SC-002**: `git grep -nE '"[A-Z]{1,2}[0-9]+"' -- server/quiz_server` 無輸出。
- **SC-003**: 非 Google 主機、轉址到外部主機、非準備階段三種情況下對外請求數皆為 0（`test_api_import.py`）。

## Assumptions

- 助教的 Guided Notes 沿用「題號／題目／作答」表頭，可能改名或位移，但仍為一格一空的簡答題。
- 不讀題目敘述（R-02 明訂不要求）。
