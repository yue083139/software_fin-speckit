# Verification: 019-live-feed（v1.1）

## 門禁實錄

本機（Windows 11，無 `make`）依 `Makefile` 的 `gate-pr` 逐項執行，2026-11-27，分支 `019-live-feed`（自 `origin/dev` `43e0103`）：

```
uv run --project server pytest -q server/tests → 367 passed, 1 warning
npm --prefix web test                          → Tests  102 passed (102)（v1.1）
npm --prefix web run lint                      → 無輸出（exit 0）
npm --prefix web run typecheck                 → 無輸出（exit 0）
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-agents: 0 處漂移
diagrams（PlantUML 1.2026.9，Microsoft OpenJDK 21）→ 019 三張圖轉 PNG
gate-diagrams-syntax: 58 個圖檔語法通過
gate-diagrams: 58 個圖檔，0 處問題
gate-parity: 0 處不一致
```

web 第二次 `npm --prefix web test`：`Tests  102 passed (102)`（v1.1；v1.0 為 99）。web 與 OpenSpec 組 `feat/live-feed` 逐字相同（`git diff --no-index` 兩邊 `web/src` 無差異）。

## 變異實錄（錯時會紅）

於 OpenSpec 組同一份 web 程式執行（兩邊 web 逐字相同）：

| 變異 | 結果 |
|---|---|
| 拿掉 `prev === null` | 2 failed：「第一次收到 view 只當基準，不出通知」「新送出時右上角跳出通知，開頁時不跳」 |
| 拿掉 `next.phase !== "answering"` | 1 failed：「沒有新送出、或不在搶答中都不出通知」 |
| 拿掉 `classic &&` | 1 failed：「非經典模式一律『送出』（得主要等判定）」 |
| （v1.1）拿掉斷線清基準 `if (!connected)` | 1 failed：「斷線重連後第一個新 view 只當基準，之後的新送出照跳」 |
| （v1.1）拿掉 `view === stale.current` | 1 failed：同上 |

## 圖表一致性核對（憲章原則 VII）

| 圖 | 圖元素 | 程式 | 一致 |
|---|---|---|---|
| component | main.tsx AntApp notification maxCount 4 | `main.tsx`「<AntApp notification={{ maxCount: 4 }}>」 | ✅ |
| component | Teacher → LiveFeed（每次新 view） | `Teacher.tsx`「useLiveFeed(view?.role === "teacher" ? view : null, connected)」 | ✅ |
| component | server views 不改 | `git diff origin/dev -- server contracts` 為空 | ✅ |
| class | FeedEvent（key／text） | `LiveFeed.tsx` `interface FeedEvent` | ✅ |
| class | LiveFeed：feedEvents、useLiveFeed(view, connected)、prev／stale useRef | `LiveFeed.tsx` `feedEvents`、`useLiveFeed`、`useRef<TeacherView \| null>` | ✅ |
| sequence | 斷線清基準、重連等第一個新 view（v1.1） | `useLiveFeed`「if (!connected) { prev.current = null; stale.current = view; … }」「view === stale.current」 | ✅ |
| sequence | 第一個 view 只記基準 | `feedEvents`「if (prev === null …) return []」、`prev.current = view` | ✅ |
| sequence | 新 view ⇒ feedEvents ⇒ notification.open（不含答案） | `useLiveFeed` 迴圈 `notification.open({ key, message: e.text, placement: "topRight", duration: 3 })` | ✅ |

## 評審紀錄

- 架構通道（全卡掃，2026-11-27，獨立子代理）：**NOT CLEARED(0B/1M/1m)**。重要：規格、兩組 parity／矩陣寫「重連後第一個 view 不出通知」，程式卻沿用斷線前的基準、會補跳斷線期間的送出 ⇒ v1.1 改程式照規格（見 research R2）。次要：矩陣「學生端無快訊」沒有學生頁測試 ⇒ 補「學生頁沒有快訊」一例。
- 對抗通道（diff，2026-11-27，獨立子代理）：**NOT CLEARED(0B/0M/1m)**，同指重連基準；另指出伺服器重啟時新一輪同組同題可能被舊基準吞掉 ⇒ 同一修法解決，補一例。其餘（StrictMode 重跑、同 view 重推、reset 後新一輪、作答隔離）證偽不成。
- 評審輪次：B 檔兩輪各單通道已用滿；藥方由主會話落地並以變異實錄自證，未再派回驗（輪次已滿），交負責人終審。

## 人工驗證（需求 P-05）

狀態：**已執行**（`docs/manual-verification.md` 場次 J）。

結果：✅ 第 1～5 步全部符合（jinny／2026-11-27，Windows 11 本機瀏覽器；OpenSpec 依 `beeb8c6`、SpecKit 依 `5e180ab`，兩組皆執行）。開始搶答不跳；新送出跳「搶下／送出」且約 3 秒消失、不含答案；F5 重新整理不重跳；學生頁無快訊。斷線重連由單元測試涵蓋，未人工模擬斷線。
