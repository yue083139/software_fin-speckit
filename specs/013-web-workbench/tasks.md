# Tasks: 前端改用 antd 工作檯版型

**Input**: `specs/013-web-workbench/` 與 `diagrams/013-web-workbench-*.puml`

## Phase 0: 提案前置

- [x] T000 讀 resolve 工作檯視覺單一出處（`theme.ts`、`glass.css`、`AdminShell.tsx`），只取色票、光暈、玻璃層與版型
- [x] T001 依賴版本：取 npm 上 ≥2 週前發布的 antd 5.x 最新版，精確版本寫入 `package.json`
- [x] T002 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T003 提案輪評審（架構通道，全卡掃，與 OpenSpec 組同批）：CLEARED 0B/1M/3m，藥方併入 v1.1

## Phase 1: 驗收（先改查詢方式，斷言不改）

- [x] T010 [P] `web/src/test-utils.ts`：`btn`／`allBtn` 取文字外層 `<button>`
- [x] T011 [P] `web/src/test-setup.ts`：`matchMedia`、`ResizeObserver`、canvas

## Phase 2: User Story 1 - 老師工作檯 (P1) 🎯

- [x] T020 `theme.ts`、`ui.tsx`、`Shell.tsx`、`styles.css`、`main.tsx`
- [x] T021 老師頁：左側導覽＋玻璃頂欄＋內容卡；作答狀況表改 antd `Table`
- [x] T022 「學生連結」卡（QR code，`student_url` 型別預留）

## Phase 3: User Story 2 - 學生用手機作答 (P1)

- [x] T030 學生頁、首頁：置中窄版卡片；題目敘述在輸入欄上方

## Phase 4: 驗證

- [x] T040 typecheck、lint、test、build 全綠
- [x] T041 web 與 OpenSpec 組 `feat/web-workbench` 逐字相同（`git diff 50c3605 d451dc9 -- web` 原樣套用）
- [x] T042 實作輪評審（對抗通道，只掃 diff）：0B/1M/0m，倒數測試截止起算點已修
- [x] T043 圖碼一致核對寫入 `verification.md`
- [ ] T044 人工驗證（負責人，整合後的本地棧）
