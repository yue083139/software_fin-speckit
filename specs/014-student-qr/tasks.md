# Tasks: 手機掃 QR code 進學生頁，老師端限本機

**Input**: `specs/014-student-qr/` 與 `diagrams/014-student-qr-*.puml`

## Phase 0: 提案前置

- [x] T000 探針 `probes/cloudflared_probe.py`，原樣輸出 `probes/results/2026-11-26-cloudflared.txt`（公網 IP 已遮蔽）
- [x] T001 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T002 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）
- [x] T003 提案輪評審（架構通道，全卡掃，與 OpenSpec 組同批；CLEARED 0B/3M/1m）

## Phase 1: User Story 1 - 以通道啟動 (P1) 🎯

- [x] T010 [P] [US1] `server/tests/test_tunnel.py`
- [x] T011 [US1] `server/quiz_server/tunnel.py`
- [x] T012 [US1] `__main__.py --tunnel`／`QUIZ_TUNNEL=1`；`Makefile dev-tunnel`；`start.ps1 -Tunnel`、`start-tunnel.cmd`

## Phase 2: User Story 2 - 老師身分只在本機 (P1)

- [x] T020 [P] [US2] `server/tests/test_api_host.py`、`conftest.py`（testserver 視為本機）
- [x] T021 [US2] `app.py`：`is_local`、老師依賴與 WS、回呼；`create_app(student_url=)`
- [x] T022 [US2] `activity.public_url`、`views.teacher_view.student_url`；`contracts/api.md`、`web/src/types.ts`

## Phase 3: 收尾

- [x] T030 README、`docs/manual-verification.md` 場次 F、`eval/acceptance/matrix.yaml` M-023
- [x] T031 變異實錄、真棧（`probes/results/2026-11-26-student-qr-real-stack.txt`）
- [x] T032 圖表與程式一致性檢查（原則 VII）
- [x] T033 實作輪評審（對抗通道，只掃 diff；CLEARED 0B/0M/1m）；藥方落地
- [ ] T035 前端：`live.ts` 遇 4403 不重連、老師頁提示「老師頁只能在本機開啟」；學生連結 QR（`student_url ?? origin`，antd `QRCode`）——待 `web-workbench` 合入後
- [ ] T034 人工驗證（負責人，場次 F）
