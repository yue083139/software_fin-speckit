# Verification: 019-live-feed（v1.0）

## 門禁實錄

本機（Windows 11，無 `make`）依 `Makefile` 的 `gate-pr` 逐項執行，2026-11-27，分支 `019-live-feed`（自 `origin/dev` `43e0103`）：

```
uv run --project server pytest -q server/tests → 367 passed, 1 warning
npm --prefix web test                          → Tests  99 passed (99)
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

web 第二次 `npm --prefix web test`：`Tests  99 passed (99)`。web 與 OpenSpec 組 `feat/live-feed` 逐字相同（`git diff --no-index` 兩邊 `web/src` 無差異）。

## 變異實錄（錯時會紅）

於 OpenSpec 組同一份 web 程式執行（兩邊 web 逐字相同）：

| 變異 | 結果 |
|---|---|
| 拿掉 `prev === null` | 2 failed：「第一次收到 view 只當基準，不出通知」「新送出時右上角跳出通知，開頁時不跳」 |
| 拿掉 `next.phase !== "answering"` | 1 failed：「沒有新送出、或不在搶答中都不出通知」 |
| 拿掉 `classic &&` | 1 failed：「非經典模式一律『送出』（得主要等判定）」 |

## 圖表一致性核對（憲章原則 VII）

| 圖 | 圖元素 | 程式 | 一致 |
|---|---|---|---|
| component | main.tsx AntApp notification maxCount 4 | `main.tsx`「<AntApp notification={{ maxCount: 4 }}>」 | ✅ |
| component | Teacher → LiveFeed（每次新 view） | `Teacher.tsx`「useLiveFeed(view?.role === "teacher" ? view : null)」 | ✅ |
| component | server views 不改 | `git diff origin/dev -- server contracts` 為空 | ✅ |
| class | FeedEvent（key／text） | `LiveFeed.tsx` `interface FeedEvent` | ✅ |
| class | LiveFeed：feedEvents、useLiveFeed、prev useRef | `LiveFeed.tsx` `feedEvents`、`useLiveFeed`、`useRef<TeacherView \| null>` | ✅ |
| sequence | 第一個 view 只記基準 | `feedEvents`「if (prev === null …) return []」、`prev.current = view` | ✅ |
| sequence | 新 view ⇒ feedEvents ⇒ notification.open（不含答案） | `useLiveFeed` 迴圈 `notification.open({ key, message: e.text, placement: "topRight", duration: 3 })` | ✅ |

## 評審紀錄

- 架構通道（全卡掃）：待派。
- 對抗通道（diff）：待派。

## 人工驗證（需求 P-05）

狀態：**待執行**（`docs/manual-verification.md` 場次 J）。
