# Implementation Plan: 啟動即進老師頁，Google 設定與手機連線都在老師頁引導完成

**Branch**: `017-easy-setup` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/017-easy-setup-{component,class,sequence}.puml`（憲章原則 VII：本計畫以三張圖為主要藍圖）

**v1.1（提案輪評審：架構 CLEARED 0B/1M/3m、紅隊 NOT CLEARED 0B/4M/4m，皆 0 阻斷；負責人指示審完直接實作）**：藥方八條見 research.md 抬頭；類別圖改為注入 `Tunnel` 實例、時序圖補 409／504 與建立中取消分支。

## Summary

1. **任一方式啟動就緒後自動開老師頁一次**，旗標可關，終端機備援（R1）。
2. **Google 設定精靈**：限本機＋金鑰、白名單、只改 `.env` 兩鍵、立即生效、密鑰不外洩（R2）。
3. **一鍵開關手機連線**：`create_app` 注入以伺服器埠建立的 `Tunnel` 實例（`--tunnel` 共用）、執行期起停、老師 view `tunnel` 狀態、503／504、建立中關閉取消、搶答中不能關閉、意外結束轉 off；移除 `start-tunnel.cmd`（R3）。
4. **準備階段頂部設定清單**（R4）。
5. **`start.ps1` 代裝 uv／Node.js 並刷新 PATH**（R5；探針③已證）。

**矩陣落點**：M-025（P-06）、M-026（X-04）、M-027（R-01）。

**merge 三問第三問**：負責人指示；助教須用另一份 Guided Notes 測試、須自建 OAuth 用戶端，精靈降低上手成本；Demo 不必切終端機。

## Technical Context

**Language/Version**: Python 3.12、TypeScript（React 19＋antd 5）、PowerShell 5.1
**Primary Dependencies**: 無新增（`webbrowser` 標準庫；cloudflared 為選用外部執行檔）
**Testing**: pytest（`.env` 以 tmp_path 注入、假 Tunnel、替身開瀏覽器）、vitest
**Constraints**: 與 OpenSpec 組同批、程式逐字相同；`contracts/api.md` 改動負責人 2026-11-26 批准；探針①②③皆已執行（`probes/results/2026-11-26-easy-setup.txt`）；探針與測試不得以檔案伺服器接通道

## Constitution Check

- 原則 VII（圖表優先）：三張圖先於實作，實作後核對一致。
- 作答隔離：學生 view 不新增欄位（`tunnel`、`student_url` 只在老師 view）。
- 祕密衛生：密鑰只寫本機 `.env`，`gate-secrets` 持續擋入庫。

## Project Structure

```
server/quiz_server/{__main__,app,google_auth,envfile(新),launch(新),tunnel,activity,views}.py
server/tests/{test_google_config,test_tunnel_api,test_launch}.py（新）
web/src/pages/{GooglePanel,Teacher}.tsx、web/src/pages/SetupChecklist.tsx（新）
start.ps1、start-tunnel.cmd（刪）、contracts/api.md、README.md、.env.example、docs/manual-verification.md
```
