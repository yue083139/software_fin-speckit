# Tasks: 搶答中老師頁即時搶答快訊

**Input**: `specs/019-live-feed/` 與 `diagrams/019-live-feed-*.puml`

## Phase 0: 前置
- [x] T000 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T001 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）

## Phase 1: User Story 1 (P1) 🎯
- [x] T010 [US1] 測試先行：`web/src/pages/livefeed.test.tsx`（`feedEvents` 五例：第一個 view 當基準、經典搶下／送出、非經典一律送出、無新送出與非搶答中不出、文案不含答案；hook 一例：新送出跳通知、開頁不跳）
- [x] T011 [US1] `web/src/pages/LiveFeed.tsx`：`feedEvents`＋`useLiveFeed`
- [x] T012 [US1] `web/src/pages/Teacher.tsx`：`useLiveView` 之後呼叫 `useLiveFeed`
- [x] T013 [US1] `web/src/main.tsx`：`<AntApp notification={{ maxCount: 4 }}>`

## Phase 2: 驗證
- [x] T020 `eval/acceptance/matrix.yaml` 新增 M-029；`docs/manual-verification.md` 新增場次 J
- [x] T021 web 測試連跑兩次、`lint`、`typecheck` 綠；變異實錄
- [x] T022 圖表一致性核對（`verification.md`）
- [ ] T023 評審（架構全卡掃＋對抗 diff）
- [ ] T024 人工驗證（`docs/manual-verification.md` 場次 J）
