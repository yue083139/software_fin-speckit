# Implementation Plan: 020-podium-confetti

**Branch**: `020-podium-confetti` | **Date**: 2026-11-27 | **Spec**: `specs/020-podium-confetti/spec.md`
**藍圖**：`diagrams/020-podium-confetti-{component,class,sequence}.puml`（憲章原則 VII）

## Summary

1. **純 CSS 動畫、不加套件**（R1）：36 片 `<span>` 以 `@keyframes` 落下淡出／代價：效果較物理引擎類套件簡單／可被「領獎台出現時灑彩帶」證偽。
2. **位置與顏色由索引算出固定值、不在 render 取亂數**（R2）：重繪時 DOM 不變、不重播／可被「分數更新重繪時彩帶不重播」證偽。
3. **顏色只用 `--qz-*` 變量**（R3）／可被「只用 --qz-* 變量」證偽。
4. **無障礙**（R4）：`aria-hidden`、`pointer-events: none`、`prefers-reduced-motion` 不顯示／前兩項單元測試、第三項人工驗證場次 K 第 5 步。

**矩陣落點**：M-030（R-04、R-08、X-04）守門 `web/src/pages/podium.test.tsx`（領獎台彩帶）。
**merge 三問第三問**：`results-podium` 揭曉收尾強化，對標 Kahoot 結束彩帶，提升課堂參與感與 Demo 效果（X-04）；只改前端、不加依賴。

## Technical Context
React 19＋antd 5＋TypeScript＋CSS。`web/src/pages/Podium.tsx` 新增 `Confetti`（`CONFETTI_COUNT = 36`）；`web/src/styles.css` 新增 `#podium` 定位裁切、`.qz-confetti`、`qz-confetti-fall`。不改 server、contracts、依賴。

## Constitution Check
- 作答隔離：不新增任何資料，只在既有領獎台內加裝飾 ✅
- 圖表優先：三張圖先於實作 ✅；實作後核對見 `verification.md`
- 兩組一致：web 與 OpenSpec 組逐字相同 ✅

## 程式與圖對照
| 圖元素 | 程式 |
|---|---|
| Confetti（CONFETTI_COUNT、索引決定樣式） | `web/src/pages/Podium.tsx` `Confetti` |
| Podium（卡片內第一個子元素掛 Confetti） | `web/src/pages/Podium.tsx` `Podium` |
| qz-confetti-fall／prefers-reduced-motion | `web/src/styles.css` |
