# Research: 013 web-workbench（v1.1）

**v1.1（提案輪架構通道 CLEARED 0B/1M/3m；實作輪對抗通道 0B/1M/0m）**：antd 在 jsdom 首次渲染 5–11 秒、vitest 預設 5 秒逾時致時綠時紅 ⇒ `vite.config.ts` `testTimeout`／`hookTimeout` 30 秒、`test-setup.ts` 預先匯入 antd；時間計分學生倒數測試的截止時刻在 describe 收集時就算好 ⇒ 移進 `it()` 內以渲染當下起算（R5）；R5 文案「不變」範圍過寬 ⇒ 改為按鈕文字、`aria-label` 與提示句不變，列出卡片標題與頁首調整；`styles.css` 寫死色值 11 處 ⇒ 全部改讀 `--qz-*`、去掉備用值（R2）。

知識時點：2026-11-26。參考對象 `C:\workspace\resolve\apps\console`（antd 5、液態玻璃視覺）。本檔 R1–R6 與 OpenSpec 組 `openspec/changes/web-workbench/design.md` D1–D6 一一對應、口徑相同。

背景：負責人 2026-11-26 人工驗證全流程後指出前端「太簡陋」，指定參考 resolve 的後台工作檯，並裁「引入 antd 重寫」。現行 web 為 React 19＋純 CSS。

## R1 依賴：antd 5.29.3＋icons 5.6.1＋React 19 相容補丁 1.0.3，精確版本

- **Decision**：取 npm 上 2026-11-12 之前發布的 5.x 最新版（antd 5.29.3 發布於 2025-12-18；icons 5.6.1 於 2025-02-07）；React 19 需 `@ant-design/v5-patch-for-react-19`（peerDependencies `antd >=5.22.6`、`react >=19.0.0`），於 `main.tsx` 最先匯入。
- **Rationale**：與 resolve 同為 antd 5，主題 token 與元件 API 可直接對照。
- **Alternatives**：antd 6（原生支援 React 19；不採：token 與 API 與 resolve 有差）；純 CSS 移植（不採：負責人裁 antd）。
- **證偽欄｜可證偽**：`npm --prefix web run build` 成功。

## R2 視覺單一出處

- **Decision**：`web/src/theme.ts` 定 `palette`（主色 `#0f7c83`、文字三階灰、發絲線、光暈四色、玻璃材質漸層／邊框／陰影、內容卡陰影、卡內列底色、徽標陰影）、`quizTheme`、`cssVars()`；`styles.css` 不寫任何色值，一律讀 `--qz-*`、不寫備用值。三層：背景光暈 → 內容卡（半透明白）→ 玻璃功能層（頂欄、側欄）。`prefers-reduced-motion` 時光暈不漂移。
- **Rationale**：顏色一處改全站跟著改。
- **Alternatives**：搬 resolve 的追光、折射特效（不採：成本高、無功能價值）。
- **證偽欄｜屬取捨**：只取視覺語言。

## R3 老師頁版型：左側導覽＋內容卡，全部同時渲染

- **Decision**：頂欄＝品牌＋階段、模式、題目來源膠囊；左側 antd `Menu` 七項（活動控制、模式、作答狀況與結果、學生連結、Google 帳號、題目與匯入、組別與裝置），點擊 `scrollIntoView` 到有 `id` 的卡；≤900px 導覽移到上方。作答狀況表改 antd `Table`（`summary` 列放分數，得主格 `winner` 底色）。
- **Rationale**：搶答中老師要同時看控制鈕與作答表。
- **Alternatives**：分頁切換（不採：多一步操作）。
- **證偽欄｜可證偽**：`TeacherPanel` 整頁渲染的既有測試全綠。

## R4 學生頁與首頁：置中窄版卡片

- **Decision**：學生頁頂欄顯示組別與階段；每題一張卡，「題目敘述 → 子題標籤 → 大尺寸輸入欄」，「搶答送出」整列主按鈕；首頁學生選組大按鈕格、老師金鑰欄 `Input.Password`。
- **Rationale**：學生會以手機掃碼進入（`student-qr`）。
- **Alternatives**：沿用寬版（不採：手機難操作）。
- **證偽欄｜可證偽**：本機 8010 埠截圖；手機寬度人工驗證。

## R5 行為、按鈕文字、`aria-label` 與提示句不變；卡片標題與頁首依新版型調整；測試只改查詢方式

- **調整清單**：老師頁 h1「老師頁」→ 玻璃頂欄「課堂搶答・老師工作檯」；「組別」→「組別與裝置」；「匯入 Guided Notes」→「題目與匯入」；xlsx 檔案欄 → antd `Upload`「選擇 xlsx 檔」按鈕（選檔不送出，按「上傳 xlsx」才送）；學生頁 h1 拿掉（頂欄顯示組別與階段）；首頁 h1 改頂欄「課堂搶答」；學生結果「本組X：」改為統計塊「本組X」（無冒號）。
- **Decision**：所有按鈕文字、`aria-label`、提示句沿用；兩字按鈕關閉 antd 自動插空白（`Btn` 與 `ConfigProvider button.autoInsertSpace=false`）。antd 按鈕文字包在 `<span>`，停用判定改查外層 `<button>`（`web/src/test-utils.ts` 的 `btn`／`allBtn`），斷言不改。
- **Rationale**：證明改版不改行為。
- **Alternatives**：改用 `getByRole`（不採：按鈕內圖示的 `aria-label` 會混進可及名稱）。
- antd 首次渲染在 jsdom 要 5–11 秒：`vite.config.ts` 設 `testTimeout`、`hookTimeout` 30 秒，`test-setup.ts` 預先匯入 antd；時間計分學生倒數測試的截止改在 `it()` 內以渲染當下起算（斷言 `/1[45] 秒/` 不變）。
- **證偽欄｜可證偽**：`npm --prefix web test` 連跑三次皆 41 passed（`verification.md`）。

## R6 學生連結卡（為 `student-qr` 預留）

- **Decision**：顯示 `view.student_url ?? window.location.origin + "/"` 的連結與 antd `QRCode`；`TeacherView.student_url?: string` 型別預留。
- **Rationale**：伺服器欄位由 `student-qr` 卡加入，本卡先備好呈現。
- **證偽欄｜屬取捨**：127.0.0.1 下手機掃了連不到，由 `student-qr` 的公開通道網址解決。
