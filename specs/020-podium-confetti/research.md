# Research: 020-podium-confetti（與 OpenSpec design D1–D4 一一對應，R_n＝D_n）

知識時點：2026-11-27。

## 對標
- Kahoot：一局結束顯示領獎台時伴隨彩帶與音效（依公開產品操作經驗）。
- 裁剪：只做一次性彩帶，不做音效、不做逐名揭曉。

## R1 純 CSS 動畫、不加套件
- Decision：`Confetti` 輸出 36 個 `<span>`，`qz-confetti-fall` 從卡片上緣落下 320px、旋轉並淡出，`iteration-count: 1; fill-mode: forwards`。
- Rationale：不引入 canvas-confetti 之類套件，不改 `package.json`／鎖檔，兩組依賴不必同步。
- 證偽：「領獎台出現時灑彩帶，且對讀屏軟體隱藏」；變異拿掉 `<Confetti />` ⇒ 3 failed。

## R2 位置與顏色以索引算出固定值
- Decision：`left＝(i×37) mod 100 %`、延遲 `(i mod 9)×0.12s`、時長 `2.2＋(i mod 5)×0.3s`，漂移與旋轉亦由 `i` 決定；`key＝i`。
- Rationale：render 內取亂數會讓每次推播重繪換新元素 ⇒ 動畫重播（經典搶答檢查答錯時名次即時變，不該一直重灑）；只有 `Podium` 重新掛上（揭曉、重新整理）才再灑。
- 另一條重新掛上路徑（評審 followup，接受）：經典搶答結束後老師把所有得分組都判答錯 ⇒ 全部 0 分、領獎台卸下；再判回答對 ⇒ 領獎台重新出現並再灑一次。符合「領獎台出現就灑」的語意，不另記「本場已灑過」旗標。
- 證偽：「分數更新重繪時彩帶不重播（同一批元素）」；變異 `key` 含 `performance.now()` ⇒ 1 failed。

## R3 顏色只用 `--qz-*` 變量
- Decision：`--qz-accent`、`--qz-accent-bright`、`--qz-danger`、`--qz-ok-text`、`--qz-glow-3`、`--qz-glow-4` 輪替（`styles.css` 檔頭規定不寫色值常量）。
- 證偽：「每片彩帶位置與顏色固定，只用 --qz-* 變量」；變異改 `#ff0000` ⇒ 1 failed。

## R4 無障礙與不干擾
- Decision：容器 `aria-hidden="true"`、`pointer-events: none`、`z-index: 1`；`#podium { position: relative; overflow: hidden }`；`prefers-reduced-motion: reduce` 時 `display: none`。
- 證偽：`aria-hidden` 由單元測試核；不擋點擊與減少動態效果由人工驗證場次 K 第 1、5 步核（jsdom 不算版面與媒體查詢）。
