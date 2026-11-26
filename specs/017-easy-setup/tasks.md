# Tasks: 啟動即進老師頁，Google 設定與手機連線都在老師頁引導完成

**Input**: `specs/017-easy-setup/` 與 `diagrams/017-easy-setup-*.puml`

## Phase 0: 提案前置

- [x] T000 探針③ PATH 刷新（`probes/results/2026-11-26-easy-setup.txt`）
- [x] T001 探針①② 自動開瀏覽器、執行期起停 cloudflared：負責人本機執行 `uv run --project server python -X utf8 probes/easy_setup_probe.py --browser-url http://127.0.0.1:8000/ --cycles 3`，回填結果與 research R1、R3（2026-11-26 已回填；探針改固定 204 handler）
- [x] T002 三張圖 `make diagrams`、`make gate-diagrams` 綠
- [x] T003 `docs/parity.md` §4 登記、§5 記變更（與 OpenSpec 組同批）
- [x] T004 提案輪評審（架構 CLEARED 0B/1M/3m、紅隊 NOT CLEARED 0B/4M/4m，皆 0 阻斷；藥方入 v1.1）；負責人批准契約並指示審完直接實作

## Phase 1: 驗收測試（先紅）

- [x] T010 `server/tests/test_google_config.py`（R2）
- [x] T011 `server/tests/test_tunnel_api.py`（R3）
- [x] T012 `server/tests/test_launch.py`（R1）
- [x] T013 web：精靈、手機連線、設定清單（R2–R4）
- [x] T014 `eval/acceptance/matrix.yaml` M-025、M-026、M-027

## Phase 2: 實作

- [x] T020 `envfile.py`、`GoogleSession.reconfigure`、設定端點
- [x] T021 手機連線端點、`Activity.tunnel`、views、lifespan 收尾
- [x] T022 `__main__.py` 就緒後開瀏覽器、`--no-browser`
- [x] T023 web 三元件
- [x] T024 `start.ps1` 代裝（只認 Y／y）並刪 `-Tunnel`；刪 `start-tunnel.cmd`；`start-tunnel` 引用全集依 R3 處理
- [x] T025 `contracts/api.md`、README、`.env.example`、手冊

## Phase 3: 驗證

- [x] T030 `make gate` 原樣輸出；圖碼一致核對（原則 VII 實作階段）
- [ ] T031 實作輪評審（雙通道）
- [ ] T032 人工驗證（負責人）
- [ ] T033 parity 狀態、`make gate-parity` 綠
