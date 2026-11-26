# Feature Specification: 前端改用 antd 工作檯版型

**Feature Branch**: `013-web-workbench`
**Created**: 2026-11-26
**Status**: Approved（v1.1；提案輪架構 CLEARED、實作輪對抗藥方已落）
**Input**: 負責人 2026-11-26 人工驗證全流程後指出前端「太簡陋」，指定參考 resolve 專案的後台工作檯（`apps/console`：antd 5＋液態玻璃視覺），並裁「引入 antd 重寫」（非純 CSS 移植）。
**需求編號**：R-01、R-04｜**parity**：`docs/parity.md` §4 `web-workbench`｜**檔位**：B（介面流程與版面；行為、文案、作答隔離與 API 不變）
**圖表**：`diagrams/013-web-workbench-{component,class,sequence}.puml`

**v1.1（提案輪架構通道 CLEARED 0B/1M/3m；實作輪對抗通道 0B/1M/0m）**：antd 在 jsdom 首次渲染 5–11 秒、vitest 預設 5 秒逾時致時綠時紅 ⇒ `vite.config.ts` `testTimeout`／`hookTimeout` 30 秒、`test-setup.ts` 預先匯入 antd；時間計分學生倒數測試的截止時刻在 describe 收集時就算好 ⇒ 移進 `it()` 內以渲染當下起算（R5）；R5 文案「不變」範圍過寬 ⇒ 改為按鈕文字、`aria-label` 與提示句不變，列出卡片標題與頁首調整；`styles.css` 寫死色值 11 處 ⇒ 全部改讀 `--qz-*`、去掉備用值（R2）。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師在工作檯同時看控制鈕與作答表 (Priority: P1)

老師頁改為「玻璃頂欄＋左側導覽＋內容卡」：頂欄顯示階段、模式與題目來源；左側導覽點擊即捲到對應內容卡；所有內容卡同時在頁面上。

**Why this priority**: 搶答中老師要同時操作控制鈕並看即時作答表，是 Demo 的主畫面。

**Independent Test**: `TeacherPanel` 整頁渲染的既有元件測試全綠（按鈕文字、可按條件、作答表內容不變）；本機起棧截圖。

**Acceptance Scenarios**:

1. **Given** 老師頁已連線，**When** 點左側導覽「作答狀況與結果」，**Then** 頁面捲到作答狀況表那一張卡，活動控制按鈕仍在頁面上。
2. **Given** 準備中，**When** 老師按「開始搶答」，**Then** 頂欄階段膠囊由「準備中」變為「搶答中」。
3. **Given** 任一階段，**When** 比對改版前後，**Then** 每個按鈕的文字、可按條件與送出的請求都相同。

---

### User Story 2 - 學生用手機作答 (Priority: P1)

學生頁與首頁改為置中窄版卡片；每題一張卡，題目敘述在對應子題輸入欄上方，「搶答送出」為整列主按鈕；手機寬度不需水平捲動。

**Why this priority**: `student-qr` 卡會讓學生用手機掃碼進入。

**Independent Test**: 既有學生端元件測試全綠；手機寬度人工驗證。

**Acceptance Scenarios**:

1. **Given** 搶答中、手機寬度（420px），**When** 學生開啟學生頁，**Then** 每題的輸入欄與「搶答送出」完整顯示在畫面寬度內。
2. **Given** 首頁，**When** 老師輸入金鑰，**Then** 金鑰欄以遮罩顯示（投影時不外露）。

---

### Edge Cases

- 寬度 ≤900px 時老師頁左側導覽移到內容上方。
- 使用者設定「減少動態效果」時背景光暈不漂移。
- 伺服器尚未提供 `student_url` 時，「學生連結」卡用本頁網址。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**：前端 MUST 以精確版本引入 antd 5.29.3、`@ant-design/icons` 5.6.1、`@ant-design/v5-patch-for-react-19` 1.0.3（R1）。
- **FR-002**：顏色 MUST 只在 `web/src/theme.ts` 定義，`styles.css` 只讀 `--qz-*` 變量（R2）。
- **FR-003**：老師頁 MUST 為玻璃頂欄＋左側導覽＋內容卡，所有卡同時渲染，導覽點擊捲到對應卡（R3）。
- **FR-004**：學生頁與首頁 MUST 為置中窄版卡片，手機寬度可作答（R4）。
- **FR-005**：所有按鈕文字、`aria-label`、提示句與可按條件 MUST 不變；卡片標題與頁首依新版型調整（清單見 research R5）；測試只改「找按鈕」的查詢方式與倒數測試的截止起算點，斷言不改（R5）。
- **FR-006**：老師頁 MUST 有「學生連結」卡，顯示 `student_url`（無則本頁網址）與 QR code（R6）。
- **FR-007**：伺服器、`contracts/`、送往學生端的資料 MUST NOT 改變。

## Success Criteria *(mandatory)*

- **SC-001**：`npm --prefix web test` 連跑三次皆 41 passed。
- **SC-002**：`npm --prefix web run typecheck`、`run lint` 無錯誤；`run build` 成功。
- **SC-003**：`make gate`、`make gate-parity SIBLING=../software_fin-openspec` 綠（web 兩組逐字相同）。
- **SC-004**：人工驗證：老師頁導覽捲動、學生頁手機寬度作答。
