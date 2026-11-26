# Implementation Plan: 手機掃 QR code 進學生頁，老師端限本機

**Branch**: `014-student-qr` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/014-student-qr-{component,class,sequence}.puml`

**v1.1 評審（S 檔壓縮版一輪：提案輪架構全卡掃＋實作輪對抗 diff，雙通道，與 OpenSpec 組同批）**：架構 0B/3M/1m、對抗 0B/0M/1m，皆 CLEARED。藥方——檔位改 S、提交標 `[CORE]`；`docs/parity.md` §4／§5 登記；前端遇 4403 不重連並提示「老師頁只能在本機開啟」（`web-workbench` 合入後接上）；註解決策編號訂正、`contracts/api.md` WebSocket 關閉代碼補 4403；`tunnel.URL` 只認 `INF |` 表框列且排除 `api.trycloudflare.com`，補負例。

## Summary

1. **`--tunnel` 時以子行程起 `cloudflared tunnel --url`，讀輸出表框列取網址**；失敗退回本機模式（R1）。
2. **老師身分只在本機**：Host 主機名＋無 Cloudflare 標頭雙條件，先於金鑰檢查；不用 `client.host`（R2）。
3. **老師 view 加 `student_url`**，學生 view 不帶（R3）。
4. 預設行為不變（R4）。

**矩陣落點**：新增 M-023（X-04、P-06）。

**merge 三問第三問**：負責人要求手機掃碼作答（Demo 須展示至少 2 組學生端）；課程說明「不必架設可供其他設備連線的伺服器」是不強制、非禁止；範圍成本一個子行程、一道 Host 檢查，不碰搶答與隔離口徑。

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: 外部執行檔 cloudflared（選用；不入 Python 依賴）
**Testing**: pytest（`test_api_host.py`、`test_tunnel.py`，不真起 cloudflared）；真棧探針
**Constraints**: 與 OpenSpec 組同批，server／web 程式逐字相同；`contracts/api.md` 改動負責人 2026-11-26 照傾向批准

## Constitution Check

- 原則 VII（圖表優先）：三張圖為藍圖——組件圖（cloudflared 子行程、Cloudflare 邊緣、本機守衛）、類別圖（`Tunnel`、`is_local`、`Activity.public_url`）、時序圖（啟動取網址、手機經通道作答、公開網址開老師頁被拒）。
- 作答隔離：`student_url` 不進學生 view（FR-004）；學生端點行為不變。
- 簡單與本機優先：預設只綁 127.0.0.1；通道為選用。

## Project Structure

```
server/quiz_server/tunnel.py          新：找 cloudflared、解析網址、子行程起停
server/quiz_server/app.py             is_local、老師依賴與 WS、回呼；create_app(student_url=)
server/quiz_server/__main__.py        --tunnel／QUIZ_TUNNEL=1
server/quiz_server/activity.py        public_url
server/quiz_server/views.py           teacher_view.student_url
server/tests/test_api_host.py、test_tunnel.py、conftest.py
Makefile（dev-tunnel）、start.ps1（-Tunnel）、start-tunnel.cmd、README、docs/manual-verification.md 場次 F
contracts/api.md、web/src/types.ts、eval/acceptance/matrix.yaml（M-023）
```

## 實作後驗證（原則 VII）

圖表與程式一致性：`Tunnel` 的方法（`start`、`stop`）、`parse_url`、`wait_for_url`、`find_cloudflared`、`is_local`、`LOCAL_HOSTNAMES`、`TUNNEL_HEADERS` 皆與類別圖同名；時序圖三條流程與 `test_api_host.py` 情境一一對應。
