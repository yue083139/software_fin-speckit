# Tasks: 015-teacher-key-hidden（v1.1）

## Phase 1：圖表與測試（先紅）
- [x] T001 三張圖 `diagrams/015-teacher-key-hidden-{component,class,sequence}.puml`＋PNG
- [x] T002 `web/src/route.test.ts`
- [x] T003 `web/src/pages/teacherkey.test.tsx`（v1.1：Google 401 不清、操作 401 與 4401 清除）、`web/src/app.test.tsx`（重貼同一網址、先錯後對）
- [x] T004 `eval/acceptance/matrix.yaml` M-024

## Phase 2：實作
- [x] T010 `web/src/route.ts`
- [x] T011 `web/src/App.tsx`
- [x] T012 `web/src/pages/Teacher.tsx`
- [x] T013 `web/CLAUDE.md`＋`make sync-agents`；README；手冊場次 G；parity

## Phase 3：驗證
- [x] T020 `make gate`（web 連跑兩次）、`make gate-parity SIBLING=../wt-os-key`
- [x] T021 圖碼一致核對
- [x] T022 評審（架構全卡掃＋對抗 diff）
- [ ] T023 人工驗證（負責人，場次 G）
