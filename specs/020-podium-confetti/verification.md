# Verification: 020-podium-confetti（v1.0）

## 門禁實錄

本機（Windows 11，無 `make`）依 `Makefile` 的 `gate-pr` 逐項執行，2026-11-27，分支 `020-podium-confetti`（接在 `019-live-feed` 之後，自 `origin/dev` `43e0103`）：

```
npm --prefix web test                    → Tests  106 passed (106)（含 019-live-feed v1.1）
npm --prefix web run lint                → 無輸出（exit 0）
npm --prefix web run typecheck           → 無輸出（exit 0）
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
diagrams（PlantUML 1.2026.9，Microsoft OpenJDK 21）→ 020 三張圖轉 PNG
gate-diagrams-syntax: 61 個圖檔語法通過
gate-diagrams: 61 個圖檔，0 處問題
gate-parity: 0 處不一致
```

web 第二次 `npm --prefix web test`：`Tests  106 passed (106)`。伺服器、`contracts/`、`web/package.json` 未改；web 與 OpenSpec 組 `feat/podium-confetti` 逐字相同（`diff -rq web/src` 無差異）。

## 變異實錄（錯時會紅）

於 OpenSpec 組同一份 web 程式執行（兩邊 web 逐字相同）：

| 變異 | 結果 |
|---|---|
| 拿掉 `<Confetti />` | 3 failed：「領獎台出現時灑彩帶」「分數更新重繪時彩帶不重播」「只用 --qz-* 變量」 |
| `key={i}` 改成含 `performance.now()`（每次重繪換新元素） | 1 failed：「分數更新重繪時彩帶不重播（同一批元素）」 |
| 顏色改成 `#ff0000` | 1 failed：「每片彩帶位置與顏色固定，只用 --qz-* 變量」 |

三個變異都已還原。

## 圖表一致性核對（憲章原則 VII）

| 圖 | 圖元素 | 程式 | 一致 |
|---|---|---|---|
| component | Podium → Confetti（有名次時、卡片內） | `Podium.tsx`「<Section id="podium" title="領獎台">」下第一個子元素 `<Confetti />`；`places.length === 0` 時整個回 null | ✅ |
| component | Confetti → styles.css 一次性動畫 | `styles.css` `.qz-confetti span`「animation-iteration-count: 1」、`qz-confetti-fall` | ✅ |
| component | server 不改 | `git diff origin/dev -- server contracts web/package.json` 為空 | ✅ |
| class | Confetti：CONFETTI_COUNT = 36、--qz-* 六色、map(i) 內以索引算樣式 | `Podium.tsx` `CONFETTI_COUNT`、`CONFETTI_COLORS`、`Array.from({ length: CONFETTI_COUNT }, (_, i) => …)` | ✅ |
| sequence | 重繪時同一批元素、不重播 | `key={i}`；測試「分數更新重繪時彩帶不重播（同一批元素）」 | ✅ |

## 評審紀錄

- 架構通道（全卡掃，2026-11-27，獨立子代理）：**CLEARED**（0B/0M/2m）。次要：①「約 3 秒」只算單片時長，含延遲最晚約 4.24 秒 ⇒ parity、場次 K、SpecKit 時序圖改「約 4 秒內全部淡出」；②SpecKit 類別圖寫了程式沒有的 `piece(i)` ⇒ 改為「map(i) 內以索引算」。另指出場次 K 第 1 步「可點表格答對／答錯」驗不到 pointer-events（彩帶被裁在領獎台卡內、碰不到表格）⇒ 改為檢查名次文字可讀。
- 對抗通道（diff，2026-11-27，獨立子代理）：**CLEARED**（0B/0M/1m）。次要：全部判錯使領獎台卸下、再判回答對會重新掛上並再灑一次 ⇒ 接受此行為並寫進 design D2／research R2。其餘（不擋點擊、overflow 不破壞卡片陰影與捲動定位、StrictMode、無依賴、#podium 唯一）證偽不成。
- 評審輪次：B 檔兩輪各單通道已用滿；以上皆為文件與圖表訂正，未改產品行為。

## 人工驗證（需求 P-05）

狀態：**已執行**（`docs/manual-verification.md` 場次 K）。

結果：✅ 第 1～4 步全部符合（jinny／2026-11-27，Windows 11 本機瀏覽器；OpenSpec 依 `2f29eb0`、SpecKit 依 `387721a`，兩組皆執行）。揭曉時彩帶約 4 秒內落完、名次文字可讀；學生頁亦灑一次；判答錯使名次更新不重播；F5 重新整理再灑一次。執行中成員重置活動再跑一輪以湊出第 2 名，亦符合。第 5 步（選做，`prefers-reduced-motion`）未執行。
