# Feature Specification: 經典搶答結束後依順位「答對／答錯」檢查，匯出改寫選定答案

**Feature Branch**: `012-answer-review`
**Created**: 2026-11-26
**Status**: Approved（v1.1；提案輪紅隊 0B/2M/3m、架構 0B/1M/3m 皆 0 阻斷，負責人 2026-11-26 裁定並批准契約）
**Input**: 負責人 2026-11-26 驗證全流程後指示：「作答狀況與結果要給一個按鈕可以點擊就換下一個順位的答案（答錯時切換到下一組順位答案）並在匯出的試算表改成選定的答案」「可以有答對和答錯兩顆按鈕，答對就 lock，答錯繼續下一組 check」「匯出到試算表時把試算表的檔名改成 [原名字]_作答情況」。負責人裁：只在結束後、得主與得分跟著變、只套經典搶答（取代 `mode-buzz-fallback`）。
**需求編號**：R-04、R-05、R-10、X-03、X-04｜**parity**：`docs/parity.md` §4 `answer-review`｜**檔位**：S（搶答判定口徑、Guided Notes 寫回口徑、`contracts/`）
**圖表**：`diagrams/012-answer-review-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師依順位檢查答案 (Priority: P1)

經典搶答結束後，老師在作答狀況與結果表看到每題目前候選（順位最前且未被判錯的組別），按「答錯」換下一順位，按「答對」鎖定；誤按可「重設本題」。

**Why this priority**: 最快送出的答案可能是錯的；沒有檢查，匯出只能寫順位 1 的錯答案。

**Independent Test**: 兩組送出同一題，結束後對順位 1 判錯，老師 view 的得主變為順位 2；再判對即鎖定，再判回 409。

**Acceptance Scenarios**:

1. **Given** 經典搶答 `ended`、第 1 題第2組順位 1、第1組順位 2，**When** 老師對第2組按「答錯」，**Then** 第 1 題得主變為第1組，第2組該題 0 分。
2. **Given** 候選為第1組，**When** 老師按「答對」，**Then** 第1組鎖定；再對第 1 題檢查回 409「本題已鎖定，請先重設本題」。
3. **Given** 候選為第2組，**When** 老師連送兩次「答錯」（兩次都帶第2組），**Then** 第二次回 409「這一組不是目前要檢查的答案，請重新整理」，候選只往後移一組。
4. **Given** 第 1 題所有組都被判錯，**When** 老師查看，**Then** 該題無得主，顯示「全部答錯，無得主」。
5. **Given** 已鎖定或已判錯，**When** 老師按「重設本題」，**Then** 回到順位 1 為得主、未檢查；對尚未檢查的題按「重設本題」回 409「本題尚未檢查」。
6. **Given** 只計對錯或時間計分模式，或經典模式在 `answering`，**When** 要求檢查，**Then** 回 409，結果不變。

---

### User Story 2 - 學生看到檢查後的結果 (Priority: P1)

學生在結束後看到的得主、各組分數與每組 ✓／✗，隨老師檢查即時更新，與老師畫面一致。

**Why this priority**: 負責人裁「得主與得分跟著變」；不同步就違反 results-view「老師與學生看到的結果一致」。

**Independent Test**: 老師判錯後，學生 WebSocket 收到新 view，`results` 的得主與老師 `board` 相同。

**Acceptance Scenarios**:

1. **Given** 學生在 `ended` 畫面，**When** 老師判錯第 1 題順位 1，**Then** 學生畫面得主與分數立即更新，與老師相同。
2. **Given** 活動在 `answering`／`judging`，**When** 學生收到任何訊息，**Then** 不含他組答案與判定（既有隔離不變）。

---

### User Story 3 - 匯出寫入選定答案，副本名稱「_作答情況」 (Priority: P1)

匯出到 Google 試算表與下載 xlsx 都寫入檢查後選定的答案；匯入時建立的雲端副本名為「<原標題>_作答情況」，xlsx 下載檔名 `<原檔名>_作答情況.xlsx`。

**Why this priority**: R-05 要求寫回「搶答成功的組別答案」，答錯的不算成功；檔名為負責人指定。

**Independent Test**: 判錯順位 1 後下載 xlsx，填空格為順位 2 答案；替身 Drive 收到的 copy 名稱為「<原標題>_作答情況」；寫回後把該題全部判錯再寫一次，該格回到原內容。

**Acceptance Scenarios**:

1. **Given** 第 3 題順位 1 判錯、順位 2 判對，**When** 老師匯出，**Then** 第 3 題填空格為順位 2 的答案（Google 與 xlsx 皆同）。
2. **Given** 已寫回 Google 試算表，**When** 老師把第 3 題全部判錯再寫回，**Then** 副本第 3 題填空格回到匯入時原內容；從未寫過且無人搶答的題不被寫入。
3. **Given** 以 Google 試算表連結匯入，**When** 匯入完成，**Then** 雲端硬碟多一份「<原標題>_作答情況」。
4. **Given** 以 `group.xlsx` 匯入，**When** 下載 xlsx，**Then** 檔名為 `group_作答情況.xlsx`。
5. **Given** 寫回後重置活動，**When** 新一場第 1 題無人搶答、第 4 題有得主再寫回，**Then** 副本第 1 題還原為原內容、第 4 題為新得主答案。
6. **Given** 寫回後重置並重新匯入（新副本），**When** 新一場只有第 4 題有得主再寫回，**Then** 寫入範圍只有第 4 題的填空格。

---

### Edge Cases

- 某題沒有任何送出：無候選，檢查回 409「本題沒有可檢查的答案」，匯出該題保持原樣。
- 未檢查的題：維持順位 1 得主（R-10），匯出寫順位 1。
- 重置活動或重新匯入：檢查結果清空。
- 匯出後再改判：允許；重匯出寫入目前得主，並把上次寫過、這次已無得主的格還原為原內容。
- 兩個匯出或寫回請求同時到達：伺服器依序執行。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**：經典搶答的得主 MUST 為依伺服器接收序第一個未被判錯的送出；無任何檢查時送出、順位、結果與匯出 MUST 與第一期相同（順位 1 得主）；全部判錯 MUST 無得主。
- **FR-002**：老師 MUST 能以 `POST /api/teacher/review {question, team, correct}` 對目前候選判定，`team` MUST 等於候選；以 `POST /api/teacher/review-reset {question}` 重設該題。
- **FR-003**：檢查 MUST 只在經典搶答 `ended` 允許；其餘模式或階段 MUST 回 409 且狀態不變。
- **FR-004**：得主、各組分數、老師 `board`、學生 `results` 與匯出 MUST 經同一判定規則產生，檢查後 MUST 立即推播。
- **FR-005**：寫回 Google 試算表 MUST 寫入目前有得主的作答格，並 MUST 把上次寫過、這次已無得主的作答格還原為原內容；無得主且從未寫過的格 MUST NOT 被寫入；「上次寫過」的紀錄 MUST 在重置活動時保留（仍寫同一份副本）、在重新匯入時清空（新副本），寫回期間副本已被更換時 MUST NOT 更新；匯出與寫回 MUST 依序執行；xlsx 下載 MUST 由原檔重產。
- **FR-006**：雲端副本名稱 MUST 為「<原標題>_作答情況」；xlsx 下載檔名 MUST 為 `<原檔名>_作答情況.xlsx`。
- **FR-007**：搶答結束前送往學生的資料 MUST NOT 含他組答案與判定（既有隔離不變）。
- **FR-008**：老師畫面 MUST 在經典搶答結束後顯示每題檢查狀態（`board[].review`：候選、已判錯組、是否鎖定）；學生畫面結束後 MUST 顯示被檢查送出的對錯，MUST NOT 含 `review`。
- **FR-009**：檢查成功且狀態改變時 MUST 恰推播一次；任何錯誤 MUST NOT 推播。

### Key Entities

- **Activity.judgments**（共用）：題號 → 組別 → 正確否；經典模式只在 `ended` 由檢查寫入。
- **候選**：某題依順位第一個未被判錯的送出；判定為正確即「鎖定」。

## Success Criteria *(mandatory)*

- **SC-001**：無任何檢查時，經典搶答的結果與現行逐欄相同（既有測試不改即綠）。
- **SC-002**：判錯順位 1 後，老師畫面、學生畫面、xlsx、Google 副本四處的該題答案相同。
- **SC-003**：`git grep -n -- '-搶答結果' -- server web/src contracts README.md docs/requirements.md docs/manual-verification.md` 無輸出。

## Assumptions

- 檢查由單一老師操作；並發點擊以伺服器活動鎖與候選比對處理。
- 既有「-搶答結果」副本不改名。
