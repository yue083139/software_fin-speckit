# Research: 014 student-qr（v1.1）

**v1.1 評審（S 檔壓縮版一輪：提案輪架構全卡掃＋實作輪對抗 diff，雙通道，與 OpenSpec 組同批）**：架構 0B/3M/1m、對抗 0B/0M/1m，皆 CLEARED。藥方——檔位改 S、提交標 `[CORE]`；`docs/parity.md` §4／§5 登記；前端遇 4403 不重連並提示「老師頁只能在本機開啟」（`web-workbench` 合入後接上）；註解決策編號訂正、`contracts/api.md` WebSocket 關閉代碼補 4403；`tunnel.URL` 只認 `INF |` 表框列且排除 `api.trycloudflare.com`，補負例。

知識時點：2026-11-26。cloudflared 2026.11.2（winget `Cloudflare.cloudflared`）。外部行為以探針為準：`uv run --project server python -X utf8 probes/cloudflared_probe.py "C:/Program Files (x86)/cloudflared/cloudflared.exe"`，原樣輸出 `probes/results/2026-11-26-cloudflared.txt`（公網 IP 已遮蔽）。本檔 R1–R4 與 OpenSpec 組 `openspec/changes/student-qr/design.md` D1–D4 一一對應、口徑相同。

## R1 通道：子行程起 cloudflared 快速通道，讀輸出取網址

- **Decision**：`quiz_server/tunnel.py`：`find_cloudflared()` 先 `shutil.which`，再找 `C:\Program Files (x86)\cloudflared\cloudflared.exe`、`C:\Program Files\cloudflared\cloudflared.exe`；`Tunnel.start()` 執行 `cloudflared tunnel --no-autoupdate --url http://127.0.0.1:<埠>`，合併 stdout／stderr，以 `parse_url` 搜尋 `(?:^|\s)INF \|\s+(https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com)\s+\|`（只認 INF 等級的表框列、排除 `api.trycloudflare.com`；實作輪對抗評審）；30 秒內沒拿到 ⇒ 結束子行程回 `None`；拿到後另起執行緒讀掉輸出。`finally` 時 `terminate`，10 秒不退再 `kill`。啟動：`--tunnel`／`QUIZ_TUNNEL=1`、`make dev-tunnel`、`start-tunnel.cmd`（`start.ps1 -Tunnel`）。
- **Rationale**：不需帳號與網域，手機 4G 可連；讀輸出最簡單。
- **Alternatives**：區網模式（負責人不採：須同 Wi-Fi、易遇防火牆與校園網隔離）；ngrok（須註冊）；`--metrics` API 取網址（多一個埠與版本相依）。
- **證偽欄｜可證偽**：探針①「含網址的輸出行（3.3 秒）：2026-11-26T12:54:52Z INF |  https://penny-cheap-centered-fewer.trycloudflare.com  |」；②「經通道 GET /echo（第 31 次嘗試）」——DNS 約 60 秒生效。

## R2 老師身分只在本機

- **Decision**：`app.is_local(headers)`：Host 去掉埠後小寫 ∈ `LOCAL_HOSTNAMES = {127.0.0.1, localhost, [::1]}`，且無 `cf-connecting-ip`、`cf-ray`。`require_teacher` 在驗金鑰前檢查（403「老師頁只能在本機開啟」）；老師 WebSocket 不符 ⇒ **先 accept、不送任何 view** 再以 4403 關閉（實作偏離回稿：交握前就關，瀏覽器只收到 HTTP 403、關閉碼為 1006，前端無從分辨；真實用戶端實測帶 `cf-connecting-ip` 收到關閉碼 4403）；Google 回呼不符 ⇒ 403 固定 HTML。測試：conftest autouse fixture 把 TestClient 的 `testserver` 加進 `LOCAL_HOSTNAMES`（正式碼不含）。
- **Rationale**：經通道的 Host 是公開網域，且 Cloudflare 邊緣一定加 `cf-connecting-ip`；雙條件任一被繞過另一條仍擋。
- **Alternatives**：以 `client.host` 判斷（不採：uvicorn 預設信任 127.0.0.1 的 `X-Forwarded-For` 改寫它，而通道請求都從 127.0.0.1 進來）。
- **證偽欄｜可證偽**：探針②經通道「'host': 'penny-cheap-centered-fewer.trycloudflare.com'」「'cf-connecting-ip 存在': True」；④「經通道偽造 Host: 127.0.0.1:8020：HTTP 403」；②對照「本機直連、偽造 Host 與 X-Forwarded-For：'client.host': '1.2.3.4'」。變異實錄：拿掉標頭條件 1 failed、一律放行 5 failed。

## R3 老師 view 的 `student_url`

- **Decision**：`Activity.public_url`（伺服器設定，重置與重新匯入保留），由 `create_app(student_url=)` 設定；`teacher_view` 帶 `student_url`（無通道為 `null`）；學生 view 不帶。
- **證偽欄｜可證偽**：`test_student_url_only_in_teacher_view`；真棧「本機老師 view student_url：https://maui-graphic-latino-logistics.trycloudflare.com/」。

## R5 前端（web-workbench 合入後接上；實作輪架構藥方）

- **Decision**：`live.ts` `NO_RECONNECT = {4401, 4403}`、`shouldReconnect(code)`，4403 不重連；老師頁收到 WebSocket 4403 或任何老師 REST（含開頁即查的 Google 狀態）回 403「老師頁只能在本機開啟」⇒ 整頁 antd `Result`「老師頁只能在本機開啟」「請用 http://127.0.0.1:8000 開老師頁。」；「學生連結」分區顯示 `student_url ?? origin + "/"`、「複製連結」、antd `QRCode`（220 px），`student_url` 為 null 時提示「目前只在本機可連；要讓手機掃碼請用 start-tunnel.cmd 或 make dev-tunnel 啟動」。
- **證偽欄｜可證偽**：`web/src/live.test.tsx`（4403 後 5 秒內不開新連線、1006 一秒後重連）；`web/src/pages/qr.test.tsx`（QR 值＝`student_url`；null 退回 origin 並提示；本機提示文案）。

## R4 不變

- **Decision**：不帶 `--tunnel` 行為與現行相同；OAuth 回呼仍為 127.0.0.1。

## 風險

- 通道開著時學生頁與公開端點對網際網路公開；網址隨機且每次不同，Demo 用途可接受，老師可用「釋放」踢掉陌生裝置。
