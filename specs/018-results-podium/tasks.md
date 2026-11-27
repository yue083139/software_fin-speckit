# Tasks: 活動結束後顯示前三名領獎台

**Input**: `specs/018-results-podium/` 與 `diagrams/018-results-podium-*.puml`

## Phase 0: 前置
- [x] T000 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T001 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）

## Phase 1: User Story 1 (P1) 🎯
- [x] T010 [US1] 測試先行：`web/src/pages/podium.test.tsx`（`podiumPlaces` 五例（前三名與 0 分、1-1-3 跳號、第三名並列、三組並列第 1、全部 0 分）；畫面三例（左右順序與分數、0 分不顯示、學生標本組）；老師頁三例（搶答中不顯示、結束後顯示、分數欄名讀 `score_label`）；學生頁兩例（搶答中即使 view 帶分數也不顯示、結束後顯示並標本組））
- [x] T011 [US1] `web/src/pages/Podium.tsx`：`podiumPlaces`＋`Podium`
- [x] T012 [US1] `web/src/pages/Teacher.tsx`：`ended` 時於作答狀況與結果上方顯示
- [x] T013 [US1] `web/src/styles.css`：領獎台樣式（只用 `--qz-*` 變量）

## Phase 2: User Story 2 (P2)
- [x] T020 [US2] `web/src/pages/Results.tsx`：`StudentResults` 顯示並標本組

## Phase 3: 驗證
- [x] T030 `eval/acceptance/matrix.yaml` 新增 M-028；`docs/manual-verification.md` 新增場次 I
- [x] T031 web 測試連跑兩次、`lint`、`typecheck` 綠；變異實錄
- [x] T032 圖表一致性核對（`verification.md`）
- [x] T033 評審（架構全卡掃＋對抗 diff，皆 CLEARED；followup 已落，見 `verification.md`）
- [x] T034 人工驗證（`docs/manual-verification.md` 場次 I；2026-11-27 jinny 執行，第 1～4 步全部符合）
