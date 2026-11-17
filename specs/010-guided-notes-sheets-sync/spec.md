# Feature Specification: Guided Notes 直接串接雲端 Google Sheets 讀寫

**Feature Branch**: `010-guided-notes-sheets-sync`
**Created**: 2026-11-17
**Status**: Draft（v1.1；待提案輪評審與負責人裁定，契約改動待批）
**Input**: 2026-11-17 課程公告補充說明：「Guided Notes 以 Google Sheets 的形式儲存」指系統需直接串接自己雲端線上的 Google Sheets 進行讀寫，而非下載成 .xlsx 檔在本地端離線處理。負責人 2026-11-17 裁：OAuth 讓老師登入 Google；保留 xlsx 上傳當備援；先複製一份再寫；題組子題 G／H 欄寫入口徑（PR #18 followup）併入本卡。
**需求編號**：R-02、R-05｜**parity**：`docs/parity.md` §4 `guided-notes-sheets-sync`｜**檔位**：S（Guided Notes 解析與寫回口徑、`contracts/`、憑證 Google API、跨元件架構取捨）
**圖表**：`diagrams/010-guided-notes-sheets-sync-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師以 Google 帳號登入 (Priority: P1)

老師在老師頁按「以 Google 帳號登入」，在 Google 同意畫面同意後，老師頁顯示已登入的帳號。伺服器未設定 OAuth 用戶端時，Google 區塊停用並提示設定方式，上傳 xlsx 照常可用。

**Why this priority**: 沒有登入，伺服器無法以老師身分讀寫私人試算表，後兩個故事都做不了。

**Independent Test**: 以替身 Google 端點完成「登入 → 回呼 → 狀態為已登入」；偽造與重放 `state` 都被拒。

**Acceptance Scenarios**:

1. **Given** 已設定 `GOOGLE_CLIENT_ID`、`GOOGLE_CLIENT_SECRET`，**When** 老師登入並同意，**Then** `GET /api/teacher/google` 回 `signed_in: true` 與帳號 email。
2. **Given** 回呼帶伺服器未發出、已過期（10 分鐘）或已用過的 `state`，**When** 呼叫回呼，**Then** 回 400，不換權杖，登入狀態不變。
3. **Given** 未設定 OAuth 用戶端，**When** 老師開老師頁，**Then** Google 區塊停用並提示；`POST /api/teacher/google/login` 回 400「伺服器未設定 Google OAuth 用戶端」。
4. **Given** 已登入，**When** 老師按登出，**Then** 伺服器撤銷並清空權杖，狀態回未登入。

---

### User Story 2 - 從雲端試算表直接匯入 (Priority: P1)

已登入的老師貼上試算表連結，伺服器以 Sheets API 直接讀取儲存格值與合併範圍，沿用現行表頭與合併範圍定位規則解析題目，不下載 xlsx 檔。

**Independent Test**: 以三份夾具轉成的 Sheets 格狀資料替身匯入，題目清單與作答格位置與上傳同一份 xlsx 相同；全程不對 `/export?format=xlsx` 發請求。

**Acceptance Scenarios**:

1. **Given** 已登入、準備階段，**When** 貼上「題組＋單題」範本副本的連結並匯入，**Then** 題目為 4 題、第 1、2 題各 2 子題，作答格位置與上傳 `group.xlsx` 相同。
2. **Given** 未登入，**When** 以連結匯入，**Then** 回 401「請先以 Google 帳號登入」，0 次對外請求。
3. **Given** 連結不是 `https://docs.google.com/spreadsheets/d/<id>` 形式，**When** 匯入，**Then** 回 400，0 次對外請求。
4. **Given** 搶答中，**When** 匯入，**Then** 回 409，0 次對外請求。
5. **Given** 未登入，**When** 上傳 xlsx，**Then** 照常匯入（備援）。

---

### User Story 3 - 結束後寫回雲端試算表的副本 (Priority: P1)

搶答結束後，題目來自 Google 試算表時，老師按「匯出到 Google 試算表」，伺服器複製一份原試算表（名稱「<原標題>-搶答結果」），把每題得主答案寫入副本的填空格，回傳副本連結；原試算表不動。另保留「下載 xlsx」備援。

**Independent Test**: 替身 Drive／Sheets 端點收到一次 `files.copy` 與一次 `values:batchUpdate`；寫入範圍只含作答格、`valueInputOption=RAW`；不對原試算表發出任何寫入。

**Acceptance Scenarios**:

1. **Given** 以連結匯入、已結束，**When** 按「匯出到 Google 試算表」，**Then** 回 `{url}`（副本），副本填空格為得主答案，原試算表 0 次寫入。
2. **Given** 得主答案為「=1+1」，**When** 寫回，**Then** 副本該格為文字「=1+1」。
3. **Given** 非 ended，**When** 寫回，**Then** 回 409。
4. **Given** 未登入，**When** 寫回，**Then** 回 401，0 次對外請求。
5. **Given** 題目來自上傳 xlsx，**When** 寫回 Google 試算表，**Then** 回 409「題目不是從 Google 試算表匯入，請改用下載 xlsx」；下載 xlsx 照常。

---

### User Story 4 - 題組子題答案寫入標籤右側的填空格 (Priority: P2)

官方「題組＋單題」範本的子題列，左格是「（1）」標籤、右格空白；答案應寫在右格，標籤保留。

**Acceptance Scenarios**:

1. **Given** 作答表頭橫跨兩欄（`G4:H4` 合併），子題列 `G5`「（1）」、`H5` 空白且不屬合併範圍，**When** 匯入，**Then** 該子題填空格為 `H5`，學生看到的子題標籤為「（1）」。
2. **Given** 第1組搶得第 1 題答「CPU」「作業系統」，**When** 匯出（xlsx 或 Google 試算表），**Then** `G5`、`G6` 仍為「（1）」「（2）」，`H5`、`H6` 為「CPU」「作業系統」。
3. **Given** single、variant 夾具（作答格本身為橫向合併），**When** 匯入匯出，**Then** 作答格位置與本功能前相同。

### Edge Cases

- 帳號不在同意畫面「測試使用者」名單：Google 顯示封鎖頁且不導回（探針實測），伺服器端 `state` 10 分鐘後過期，老師重按登入即可。
- access token 過期（約 1 小時）：伺服器以 refresh token 自動換新；refresh 失敗 ⇒ 401 並把狀態設為未登入。
- Google API 回錯（權限不足、試算表不存在）：回 502 並只轉 Google 錯誤的 `status` 字串，不回顯請求網址。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**：系統 MUST 支援老師以 Google 帳號 OAuth 2.0 授權碼流程＋PKCE 登入與登出；回呼 MUST 只接受伺服器為已驗證老師請求發出、未過期、未用過的 `state`。
- **FR-002**：以連結匯入 MUST 以 Sheets API 直接讀取雲端試算表的值與合併範圍，MUST NOT 下載 xlsx 檔；未登入 MUST 回 401。
- **FR-003**：Sheets 來源與 xlsx 來源 MUST 經同一套表頭與合併範圍定位規則解析（不寫死座標）。
- **FR-004**：寫回 Google 試算表 MUST 先複製原試算表，只寫入副本，原試算表 MUST NOT 被修改；寫入 MUST 以文字（`RAW`）儲存。
- **FR-005**：上傳 xlsx 匯入與下載 xlsx 匯出 MUST 保留為備援，不需登入。
- **FR-006**：MUST 移除未登入的公開連結下載（`/export?format=xlsx`）。
- **FR-007**：access token、refresh token、授權碼與 client secret MUST 只存在伺服器記憶體，MUST NOT 出現在任何 API 回應、WebSocket 訊息或日誌。
- **FR-008**：題組子題標籤格右側、仍在作答表頭合併範圍欄寬內、空白且不屬合併範圍的儲存格 MUST 視為填空格（xlsx 與 Sheets 兩條路徑同一規則）。
- **FR-009**：搶答結束前任何送往學生端的資料 MUST NOT 含他組答案（既有隔離不變），且 MUST NOT 含任何 Google 欄位。

### Key Entities

- **GoogleSession**：老師的 Google 登入狀態與權杖（記憶體，單一老師）。
- **Grid**：解析器讀取的最小工作表介面（openpyxl 工作表與 Sheets 格狀資料各一個實作）。
- **Activity.source_sheet_id**：題目來自 Google 試算表時的試算表 id；上傳 xlsx 時為空。

## Success Criteria *(mandatory)*

- **SC-001**：以 Google 試算表連結匯入「題組＋單題」範本副本，題目與作答格位置與 `group.xlsx` 相同（探針 `probes/results/2026-11-17-google-sheets.txt` 步驟 2 已實測相同）。
- **SC-002**：寫回後原試算表 0 處改變，副本每題填空格為得主答案。
- **SC-003**：`git grep -n "export?format=xlsx" -- server web/src` 無輸出。
- **SC-004**：學生端所有通道與日誌不含權杖字串（隔離負例全綠）。

## Assumptions

- 只在本機執行、單一老師；伺服器重啟須重新登入。
- OAuth 同意畫面維持「測試中」，Demo 與測試帳號須登記為測試使用者。
