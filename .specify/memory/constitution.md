<!--
同步影響報告（Sync Impact Report）
- 版本：（範本）→ 1.0.0（首次制定）
- 新增原則：I 需求即法律與兩組一致、II 作答隔離、III 順位以伺服器為準、IV Guided Notes 動態定位、
  V 測試先行與人工驗證、VI 簡單與本機優先、VII 圖表優先（PlantUML 設計優先）、VIII 繁體中文與資料衛生
- 新增章節：技術約束、開發流程與品質門禁、治理
- 範本對齊：.specify/templates/plan-template.md 的 Constitution Check 以本檔八條逐條勾核（✅ 由 /speckit-plan 執行時填）；
  spec-template.md、tasks-template.md 無須改動，圖表與驗證任務由原則 VII 與「開發流程」章節要求加入
- 待辦：無
-->

# software_fin 課堂搶答系統 憲章（SpecKit 組）

## 核心原則

### I. 需求即法律，兩組功能一致

系統功能以 `docs/requirements.md`（需求編號 R-／X-／P-）為準。本組與 OpenSpec 組的系統功能**必須一致**：凡改使用者可感知行為的功能，在 `/speckit-specify` 之前先登記 `docs/parity.md` 並通知另一組，兩個 repo 的共用檔同批修改。每份 spec.md 必須列出涵蓋的需求編號。

理由：評分要求兩組功能一致，且以需求文件、程式碼與 Demo 影片三者一致為檢驗標準。

### II. 作答隔離（不可協商）

搶答結束之前，任何送往學生端的訊息與回應（WebSocket 事件、REST 回應、錯誤訊息）**不得**包含其他組別的作答內容。學生端資料一律由單一個依「活動階段＋身分」裁切的函式產生；遇到無法辨識的身分或階段時回最少資訊，不得退回完整狀態。每條學生端通道都要有「搶答中 A 組收到的 payload 不含 B 組答案」的負例測試。

理由：需求 R-09；洩漏多發生在畫面以外的傳輸內容，只驗畫面會假綠。

### III. 順位以伺服器為準（不可協商）

「最快」只依伺服器接收並寫入的先後（同一處理序內遞增序號），不採信客戶端時間戳。同一題的判定在單一臨界區完成，並發送出時恰有一組成功、順位無重號，並以並發測試證明。

理由：需求 R-10；客戶端時鐘可被竄改或漂移。

### IV. Guided Notes 動態定位（不可協商）

匯入以**表頭文字**定位欄位、以**合併範圍**判斷題組與作答格；匯出依匯入時記下的作答格位置寫回，其餘儲存格的內容與格式不得改變。禁止以寫死的儲存格座標定位題目。驗收至少涵蓋三份版面不同的 Guided Notes（官方單題範本、題組範本、自製位移改名變形檔）。

理由：需求 §4 明訂禁止靜態匯入／匯出，助教會以另一份 Guided Notes 測試。

### V. 測試先行與人工驗證

先寫會失敗的驗收測試，再寫實作（紅→綠→重構）。驗收標準須能以指令機械執行並讀出計數。除 AI 自動驗證外，每個功能完成時必須附**人工驗證紀錄**（誰、哪天、照什麼步驟、看到什麼），寫在該功能目錄的 `verification.md`。

理由：需求 P-05；AI 自報「完成」不等於完成。

### VI. 簡單與本機優先

只在本機執行，不架設對外伺服器、不引入資料庫或訊息佇列；狀態放伺服器記憶體並以 JSON 快照保存。額外功能（X-01～X-04）只在核心功能全部合入後才開始，且須經兩組協議。

理由：需求 §1 明示本機模擬即可；複雜度必須由需求支撐。

### VII. 圖表生成（Diagram Generation）

**名稱**：PlantUML 設計優先（Design-First with PlantUML）

**規則**：

- **規格制定階段（Specification Phase）**：在 `speckit.specify` 階段，必須使用 PlantUML 語法生成組件圖（Component diagram）、類別圖（Class diagram）和時序圖（Sequence diagram）。這些圖表檔案（`.puml`）必須儲存在 `./diagrams/` 目錄中。
- **產物生成（Artifact Generation）**：檔案建立後，必須使用 PlantUML CLI（`java -jar plantuml.jar "./diagrams/*.puml"`，本倉封裝為 `make diagrams`）將所有 `.puml` 檔案轉換為 PNG 圖片，且輸出的圖片必須儲存在相同的目錄中。
- **規劃階段（Planning Phase）**：`speckit.plan` 階段必須將這些圖表作為主要藍圖，用以生成應用程式的架構與組件。
- **實作階段（Implementation Phase）**：在 `speckit.implement` 階段完成程式碼生成後，必須執行驗證步驟，以確保最終的程式碼與圖表完全一致。

**本倉補充**：

- 圖檔命名 `diagrams/<NNN-功能>-<component|class|sequence>.puml`；跨功能的總覽圖為 `diagrams/system-component.puml`。每個功能只增改受它影響的圖。
- 驗證步驟的產物是該功能 `verification.md` 的「圖碼一致核對表」：逐一列出圖上的組件／類別／訊息 → 程式落點（`path:line`）→ 一致／偏離；偏離時**先改圖再改碼**，不得只改碼。
- 判據：`make gate-diagrams`（每個 `.puml` 皆有同名 `.png`；CI 另以 PlantUML `-checkonly` 驗語法）。

理由：需求 P-04；圖表讓 AI 有明確的規劃依據，也讓開發者有可視化的對照基準。

### VIII. 繁體中文與資料衛生

文件、規格、註解、提交訊息、PR 與介面文案一律使用繁體中文（判據 `make gate-zh-hant`）。不得在文件、程式碼或 repo 中放入密碼、金鑰或真實學生資料（判據 `make gate-secrets`）；憑證只走環境變數。

理由：需求 P-06；團隊慣例。

## 技術約束

- 共用技術選型以 `docs/parity.md` §2 為準：server＝Python 3.12、FastAPI、WebSocket、openpyxl，uv 管理依賴；web＝React、Vite、TypeScript，npm 管理依賴。偏離須先改 `docs/parity.md` 並經兩組同意。
- 介面契約（REST 端點與 WebSocket 事件）由第一個功能建立於 `contracts/`，之後為凍結件，改動須經規格變更與負責人批准。
- 每個功能是一個子功能目錄 `specs/NNN-<卡名>/`，卡名與 `docs/parity.md` §4 一致；不得把兩張卡的範圍併入一個功能。

## 開發流程與品質門禁

- 流程：`/speckit-specify`（含原則 VII 的三種圖）→ `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → 提案輪評審 → `/speckit-implement` → 圖碼一致核對 → 實作輪評審 → PR 合入 `dev`。
- 變更分檔（S／B／C）、評審輪次上限、派單骨架與「都綠否」依根目錄 `CLAUDE.md`；本憲章與 `CLAUDE.md` 衝突時以本憲章為準。
- 門禁：`make gate-pr`（lint、測試、繁體、金鑰形狀、圖表、Codex 規範同步）綠才可合入；`make gate-parity SIBLING=../software_fin-openspec` 於合入前在本機補跑。
- 分支：`main`／`dev` 受保護，所有變更走功能分支→PR；agent 不得推送。

## 治理

- 本憲章高於其他實務文件；修訂須以 PR 提出，寫明版本號變更理由，經負責人核准後合入，並同步檢查 `.specify/templates/` 與 `CLAUDE.md` 是否需要跟著改。
- 版本採語意化：移除或重新定義原則＝MAJOR；新增原則或實質擴充＝MINOR；措辭澄清＝PATCH。
- 每個 PR 與評審都要核對是否符合本憲章；`/speckit-plan` 的 Constitution Check 必須逐條通過或在 Complexity Tracking 寫明理由。

**Version**: 1.0.0 | **Ratified**: 2026-11-11 | **Last Amended**: 2026-11-11
