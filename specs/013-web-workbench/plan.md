# Implementation Plan: 前端改用 antd 工作檯版型

**Branch**: `013-web-workbench` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/013-web-workbench-{component,class,sequence}.puml`

**v1.1（提案輪架構通道 CLEARED 0B/1M/3m；實作輪對抗通道 0B/1M/0m）**：antd 在 jsdom 首次渲染 5–11 秒、vitest 預設 5 秒逾時致時綠時紅 ⇒ `vite.config.ts` `testTimeout`／`hookTimeout` 30 秒、`test-setup.ts` 預先匯入 antd；時間計分學生倒數測試的截止時刻在 describe 收集時就算好 ⇒ 移進 `it()` 內以渲染當下起算（R5）；R5 文案「不變」範圍過寬 ⇒ 改為按鈕文字、`aria-label` 與提示句不變，列出卡片標題與頁首調整；`styles.css` 寫死色值 11 處 ⇒ 全部改讀 `--qz-*`、去掉備用值（R2）。

## Summary

1. **引入 antd 5（精確版本 5.29.3）＋icons 5.6.1＋React 19 相容補丁 1.0.3**（負責人 2026-11-26 裁）／代價：bundle 由約 244 kB 增至約 1.2 MB（未壓縮），本機使用可接受／可被 `npm --prefix web run build` 證偽（R1）。
2. **視覺語言仿 resolve 工作檯**：色票單一出處 `web/src/theme.ts`（主色 `#0f7c83`）、背景光暈＋玻璃頂欄與側欄／屬取捨：只取視覺與版型，不搬業務碼、不引路由與資料快取套件（R2）。
3. **老師頁＝左側導覽＋內容卡，全部同時渲染**／理由：搶答中要同時看控制鈕與作答表（R3）。
4. **學生頁與首頁＝置中窄版卡片**，手機寬度可用（R4）。
5. **行為、按鈕文字、`aria-label` 與提示句不變**（卡片標題與頁首依新版型調整）：測試只把「找按鈕」改到外層 `<button>`、倒數測試截止改在 `it()` 內起算，斷言不改（R5）。

**矩陣落點**：無新列——不新增行為；M-001、M-002、M-004 的 web 守門（`web/src/pages/*.test.tsx`）全數沿用並維持綠。

**merge 三問第三問**：負責人 2026-11-26 指出前端「太簡陋」並指定參考 resolve；Demo 影片佔 20%，須在錄影前完成。

## Technical Context

**Language/Version**: TypeScript、React 19.3
**Primary Dependencies**: antd 5.29.3、@ant-design/icons 5.6.1、@ant-design/v5-patch-for-react-19 1.0.3（新增，精確版本）
**Storage**: 無
**Testing**: vitest＋Testing Library；`test-setup.ts` 補 `matchMedia`、`ResizeObserver`、canvas
**Constraints**: web 與 OpenSpec 組逐字相同（含 `package-lock.json`）；伺服器與 `contracts/` 不動

## Constitution Check

- 原則 VII（PlantUML 設計優先）：三張圖 `diagrams/013-web-workbench-*.puml` 於規格階段建立並轉 PNG；實作後於 `verification.md` 核對圖碼一致。
- 原則 VIII（繁體中文）：antd 語系 `zh_TW`；所有文案沿用。
- 作答隔離：只改呈現，不改任何送往學生端的資料（FR-007）。

## Project Structure

```text
web/package.json, web/package-lock.json   # 三個依賴
web/src/theme.ts                          # 色票、antd 主題、cssVars
web/src/ui.tsx                            # Btn、PhaseTag、Section、Backdrop、GlassHeader
web/src/Shell.tsx                         # 背景光暈＋內容層
web/src/styles.css                        # 光暈、玻璃層、版型
web/src/main.tsx                          # ConfigProvider（zh_TW、主題）
web/src/pages/*.tsx                       # 各頁改用 antd 元件
web/src/test-utils.ts、web/src/test-setup.ts
```
