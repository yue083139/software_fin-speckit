# Feature Specification: 匯入題目敘述，開放作答後顯示給學生

**Feature Branch**: `011-question-text`
**Created**: 2026-11-26
**Status**: Approved（v1.1；提案輪紅隊＋架構皆 0 阻斷，負責人 2026-11-26 指示全部做完再測、契約照傾向批准）
**Input**: 負責人 2026-11-26 人工驗證全流程時指出：「學生頁有辦法看到題目嗎？現在只有答題欄」。原情境是老師收回講義後才搶答，學生只見題號無從作答。負責人裁「S 檔壓縮版」：提案輪、實作輪各一次雙通道評審，同一會話連續跑，負責人在對話裡裁。
**需求編號**：X-04｜**parity**：`docs/parity.md` §4 `question-text`｜**檔位**：S（Guided Notes 解析口徑、`contracts/`、新增送往學生端的欄位）
**圖表**：`diagrams/011-question-text-{component,class,sequence}.puml`

**v1.1（提案輪評審，紅隊 0B/2M/2m、架構 0B/0M/5m，皆 0 阻斷）**：紅隊——子題標籤（`labels`）取自作答格原文，作答格寫「…稱為 ____」時題目文字會經標籤在準備階段送出（現行行為）⇒ R2 明寫敘述＝題目欄、登記有意不改；驗收 SC-004 掃整個目錄會被 `"S256"` 誤中 ⇒ 限縮兩檔並附負例；行號 105→110。架構——修改的需求漏列倍率與時限 ⇒ 補（FR-005）；探針檔缺指令與合併範圍 ⇒ 探針入庫 `probes/question_text_probe.py` 重跑；情境漏第 2 題、「結束後全帶」「老師任何階段」無守門 ⇒ 補情境與 `test_prompts_all_after_timed_end`。**負責人 2026-11-26 指示全部做完再測**：契約改動照傾向批准。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 匯入時讀取題目敘述 (Priority: P1)

老師匯入 Guided Notes（上傳 xlsx 或從 Google 試算表），系統除了題號與作答格，也讀取可選的題目欄，題組的每個子題各有自己那一列的敘述；沒有題目欄的檔照常匯入。

**Why this priority**: 沒有敘述，學生端無從顯示題目。

**Independent Test**: 四份夾具（single、group、variant、reference）逐子題比對敘述與題目欄該列文字；合成「無題目欄」檔匯入成功、敘述全為空字串。

**Acceptance Scenarios**:

1. **Given** 「題組＋單題」範本，**When** 匯入，**Then** 第 1、2 題的兩個子題各有自己那一列的敘述，第 3、4 題各有一段敘述。
2. **Given** 表頭只有題號與作答欄的檔，**When** 匯入，**Then** 匯入成功、題數與原檔一致，每個子題敘述為空字串。
3. **Given** 題組敘述縱向合併跨兩個子題列，**When** 匯入，**Then** 只有錨點列的子題有敘述，其餘子題為空字串。
4. **Given** 匯入後結束搶答，**When** 匯出（xlsx 或 Google 試算表），**Then** 寫回的儲存格與內容與未讀取敘述時相同。

---

### User Story 2 - 學生在搶答開始後看到題目 (Priority: P1)

學生在準備階段只見題號；老師開始搶答後，作答卡在每個子題輸入欄上方顯示敘述；時間計分（逐題開放）只顯示已開放過的題；結束後全部顯示。老師任何階段都看得到敘述。

**Why this priority**: 這是負責人指出的缺口本身。

**Independent Test**: 老師 view 在 `preparing` 每題已有 `prompts`；學生 view 在 `preparing` 每題無 `prompts` 鍵；經典搶答 `answering` 每題有 `prompts` 且長度＝子題數、payload 不含他組答案；時間計分只開第 1 題時只有第 1 題帶 `prompts`；時間計分只開過第 1 題就結束時 `ended` 每題都帶。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 學生查看畫面，**Then** 每題只見題號與子題輸入欄，view 不含 `prompts`。
2. **Given** 經典搶答已開始，**When** 學生查看畫面，**Then** 每題（含題組子題）顯示敘述；payload 不含他組答案。
3. **Given** 時間計分只開放了第 1 題，**When** 學生查看畫面，**Then** 只有第 1 題帶 `prompts`，其餘題不帶。
4. **Given** 已結束，**When** 學生查看結果表，**Then** 題號旁顯示敘述。
6. **Given** 準備階段，**When** 老師查看畫面，**Then** 老師 view 每題都含 `prompts`。
7. **Given** 時間計分只開放過第 1 題就結束活動，**When** 學生查看畫面，**Then** 每一題都含 `prompts`。
5. **Given** 某子題敘述為空字串，**When** 顯示作答卡，**Then** 不留空白段。

### Edge Cases

- 題目欄與作答欄或參考答案欄落在同一欄：該欄只歸作答或參考答案，不取作敘述。
- 題目欄值為整數值的浮點數（`1.0`）：轉成 `"1"`；其餘值以 `str()`，去頭尾空白、保留內部換行。
- 學習單把答案提示寫在題目欄：提示會隨敘述送給學生——屬老師檔案內容，與他組作答無關，手冊提醒老師題目欄只放題目。
- 無效憑證：view 不變（不含 `questions`）。
- **有意不改**：子題標籤（`labels`）取自作答格原文（`guided_notes._display`）；學習單若把題目寫進作答格（例：「負責執行指令的核心元件稱為 ____」），題目文字會經標籤在任何階段送出——`002-guided-notes-import` 起的現行行為，本功能不改；手冊與 README 提醒老師題目寫在題目欄、作答格只放標籤或底線。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**：系統 MUST 在表頭列以別名（題目、題目敘述、問題、題幹、question；NFKC、去空白、小寫後全等比對）尋找可選的題目欄；表頭格屬合併範圍時 MUST 取最左欄。
- **FR-002**：每個子題的敘述 MUST 取自該子題所在列的題目欄值；縱向合併 MUST 只取錨點列，其餘列為空字串；找不到題目欄時敘述 MUST 為空字串且匯入 MUST 照常成功。
- **FR-003**：敘述 MUST NOT 參與作答格定位與寫回（xlsx 與 Google 試算表兩條路徑）。
- **FR-004**：老師 view MUST 在任何階段每題帶 `prompts`（長度與順序同 `labels`）。
- **FR-005**：學生 MUST 只收到題號、子題數、子題標籤、倍率與時限（`contracts/api.md` 的 `questions[]` 欄位），以及依階段開放的題目敘述，MUST NOT 收到作答格座標、參考答案或原檔其他內容；學生 view MUST 只在搶答開始後帶 `prompts`：`preparing` MUST NOT 帶；`answering`／`judging` 非逐題模式每題帶、逐題模式只帶已開放過的題（開放中、已關閉、已揭曉）；`ended` 每題帶；看不到的題 MUST NOT 含此鍵（fail-closed）。
- **FR-006**：搶答結束前任何送往學生端的資料 MUST NOT 含他組答案（既有隔離不變，含帶 `prompts` 的 payload）。
- **FR-007**：web MUST 以純文字渲染敘述（不解讀 HTML），換行以 `white-space: pre-wrap` 呈現。

### Key Entities

- **Slot.prompt**：子題敘述（預設空字串），只供顯示，不參與寫回。
- **questions[].prompts**：view 中每題的子題敘述陣列，依身分與階段帶或不帶。

## Success Criteria *(mandatory)*

- **SC-001**：四份夾具每個子題的敘述等於題目欄該列文字（探針 `probes/results/2026-11-26-question-text.txt`（`uv run --project server python -X utf8 probes/question_text_probe.py tests/fixtures/guided-notes/*.xlsx`，含表頭、題目欄逐列全文與合併範圍））。
- **SC-002**：準備階段學生 view 0 個 `prompts` 鍵；時間計分開第 1 題後只有第 1 題帶。
- **SC-003**：匯出與 Google 寫回測試不改即綠。
- **SC-004**：`git grep -nE '"[A-Z]{1,2}[0-9]+"' -- server/quiz_server/guided_notes.py server/quiz_server/views.py` 無輸出（定位與裁切程式仍無寫死座標；只掃這兩檔，因 `google_auth.py` 的 OAuth 參數值 `"S256"` 會誤中）；負例：暫存副本插入 `"G5"` 後同指令有輸出。

## Assumptions

- R-02 不要求題目敘述，本功能屬 X-04（增進活動品質）。
- 前端整體改版另卡 `web-workbench`（B 檔），本功能只在現有元件加顯示。
