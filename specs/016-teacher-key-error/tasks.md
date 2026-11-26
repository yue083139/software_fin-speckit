# Tasks: 老師金鑰錯誤時顯示提示

**Input**: `specs/016-teacher-key-error/` 與 `diagrams/016-teacher-key-error-*.puml`

## Phase 0: 前置
- [x] T000 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T001 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）

## Phase 1: User Story 1 (P1) 🎯
- [x] T010 [US1] 測試先行：`server/tests/test_api_host.py` 三例（實作前 3 failed）；`web/src/live.test.tsx`、`web/src/pages/qr.test.tsx`
- [x] T011 [US1] `server/quiz_server/app.py` 金鑰錯誤分支先 accept 再關
- [x] T012 [US1] `web/src/pages/Teacher.tsx` `BadKeyNotice`
- [x] T013 `contracts/api.md` 補述；矩陣 M-001 守門補

## Phase 2: 驗證
- [ ] T020 `make gate` 綠、web 連跑兩次
- [ ] T021 評審（架構全卡掃＋對抗 diff）
- [ ] T022 人工驗證（負責人整合後）
