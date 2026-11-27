# Tasks: 揭曉領獎台時灑彩帶

**Input**: `specs/020-podium-confetti/` 與 `diagrams/020-podium-confetti-*.puml`

## Phase 0: 前置
- [x] T000 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T001 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）

## Phase 1: User Story 1 (P1) 🎯
- [x] T010 [US1] 測試先行：`web/src/pages/podium.test.tsx`「領獎台彩帶」四例（出現時 36 片且 `aria-hidden`、沒有領獎台沒有彩帶、重繪不重播、只用 `--qz-*` 且位置分散）
- [x] T011 [US1] `web/src/pages/Podium.tsx`：`Confetti`
- [x] T012 [US1] `web/src/styles.css`：`#podium` 定位裁切、`.qz-confetti`、`qz-confetti-fall`、`prefers-reduced-motion` 隱藏

## Phase 2: 驗證
- [x] T020 `eval/acceptance/matrix.yaml` 新增 M-030；`docs/manual-verification.md` 新增場次 K
- [x] T021 web 測試連跑兩次、`lint`、`typecheck` 綠；變異實錄
- [x] T022 圖表一致性核對（`verification.md`）
- [x] T023 評審（架構全卡掃＋對抗 diff，皆 CLEARED；次要訂正已落，見 `verification.md`）
- [ ] T024 人工驗證（`docs/manual-verification.md` 場次 K）
