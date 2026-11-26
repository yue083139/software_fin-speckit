# Tasks: 時間計分模式——逐題開放、伺服器計時、每題揭曉後排行榜

**Input**: `specs/008-mode-timed-scoring/` 與 `diagrams/008-mode-timed-scoring-*.puml`

## Phase 1: User Story 1 - 逐題開放、時間到伺服器自動關閉 (P1) 🎯

### Tests

- [x] T001 [P] [US1] `server/tests/test_timed_mode.py`：開題順序、只收進行中題目、假時鐘截止、`close_due`、提早結束、不因全員送出關閉、並發截止與送出（時序圖前半）；變異實錄
- [x] T002 [P] [US1] `server/tests/test_question_settings.py` 時限；`test_modes.py` 三種模式

### Implementation

- [x] T003 [US1] `modes.py` `sequential`、`timed`；`QuestionAttrs.time_limit`
- [x] T004 [US1] `Activity`：`Round`、`rounds`、`open_next`、`close_question`、`close_due`、計時器、clock 注入、送出前置條件
- [x] T005 [US1] `app.py` `/open-next`、`/close-question`、設定 API `time_limit`；`views.py` `round`

## Phase 2: User Story 2 - 每題判定後依時間計分並揭曉 (P1)

- [x] T006 [P] [US2] `server/tests/test_scoring.py::test_timed_points`、`TimedRule` 表格式
- [x] T007 [US2] `scoring.py` `timed_points`、`TimedRule`；`Activity.reveal_question`、逐題模式的 `judge`／`accept_suggestions`／`end` 前置條件；`app.py` `/reveal-question`

## Phase 3: User Story 3 - 揭曉後公開排行榜，答案仍隔離 (P1)

- [x] T008 [P] [US3] `server/tests/test_isolation.py`：三種回合狀態負例、他組送出 0 則推播、名次只計已揭曉、學生名次不含分數
- [x] T009 [US3] `views.py` `revealed`、`my_total`、`leaderboard`（學生只有名次）
- [x] T010 [US3] web：老師逐題控制、倒數、時限設定、排行榜；學生進行中題目、倒數、揭曉結果；`web/src/pages/timed.test.tsx`

## Phase N: Polish

- [x] T011 真棧探針 `probes/timed_flow_probe.py` 與原樣輸出
- [x] T012 `contracts/api.md`；`eval/acceptance/matrix.yaml` M-014～M-016、M-004 守門擴充
- [x] T013 圖碼一致核對、`make gate` 寫入 `verification.md`
- [ ] T014 人工驗證（待負責人）
