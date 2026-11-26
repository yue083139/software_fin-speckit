# Feature Specification: 手機掃 QR code 進學生頁（Cloudflare 快速通道），老師端限本機

**Feature Branch**: `014-student-qr`
**Created**: 2026-11-26
**Status**: Approved（v1.1；與 OpenSpec 組 `openspec/changes/student-qr/` 同批）
**Input**: 負責人 2026-11-26：「學生的作答連結要能夠用手機掃描 QR CODE」「有辦法直接讓網域對外公開嗎」⇒ 裁：走 Cloudflare 快速通道（非區網模式）；老師端點與老師 WebSocket 只接受本機 Host；OAuth 維持 127.0.0.1；前端 QR 畫面併入 `web-workbench`（antd `QRCode`），本功能只做伺服器、啟動與文件。
**需求編號**：R-01、X-04｜**parity**：`docs/parity.md` §4 `student-qr`｜**檔位**：S（`contracts/`、OAuth 回呼與安全邊界：老師身分限本機；原判 B，架構通道評審改 S）
**圖表**：`diagrams/014-student-qr-{component,class,sequence}.puml`

**v1.1 評審（S 檔壓縮版一輪：提案輪架構全卡掃＋實作輪對抗 diff，雙通道，與 OpenSpec 組同批）**：架構 0B/3M/1m、對抗 0B/0M/1m，皆 CLEARED。藥方——檔位改 S、提交標 `[CORE]`；`docs/parity.md` §4／§5 登記；前端遇 4403 不重連並提示「老師頁只能在本機開啟」（`web-workbench` 合入後接上）；註解決策編號訂正、`contracts/api.md` WebSocket 關閉代碼補 4403；`tunnel.URL` 只認 `INF |` 表框列且排除 `api.trycloudflare.com`，補負例。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 以通道啟動，取得學生公開網址 (Priority: P1)

老師雙擊 `start-tunnel.cmd`（或 `make dev-tunnel`），終端機印出 `https://<隨機>.trycloudflare.com/` 學生網址，老師 view 的 `student_url` 為該網址，老師頁據此顯示 QR code。

**Why this priority**: 沒有公開網址，手機（4G）連不到本機伺服器。

**Independent Test**: `test_tunnel.py` 以 cloudflared 真實輸出列解析網址；真棧 `probes/results/2026-11-26-student-qr-real-stack.txt`。

**Acceptance Scenarios**:

1. **Given** 已安裝 cloudflared，**When** 以 `--tunnel` 啟動，**Then** 終端機印出學生公開網址，老師 view `student_url` 為該網址。
2. **Given** 未安裝 cloudflared 或 30 秒內拿不到網址，**When** 以 `--tunnel` 啟動，**Then** 印安裝提示、照常以本機模式啟動，`student_url` 為 `null`。
3. **Given** 不帶 `--tunnel`，**When** 啟動，**Then** 行為與現行相同（只開 127.0.0.1）。

---

### User Story 2 - 老師身分只在本機 (Priority: P1)

通道開著時學生頁對網際網路公開；經公開網址開老師頁、呼叫老師端點或 Google 回呼一律被拒，且不洩漏金鑰對錯。

**Why this priority**: 老師金鑰在網址參數裡，公開網域可被探測；沒有這道檢查，通道等於把老師後台開放到網路上。

**Independent Test**: `server/tests/test_api_host.py`；變異實錄。

**Acceptance Scenarios**:

1. **Given** Host 為公開網域、帶 `cf-connecting-ip` 的本機 Host、或區網 IP，**When** 呼叫 `/api/teacher/*`（正確或錯誤金鑰），**Then** 回 403「老師頁只能在本機開啟」。
2. **Given** 同上，**When** 以 `role=teacher` 連 WebSocket，**Then** 以 4403 關閉。
3. **Given** 公開 Host，**When** 呼叫 `/api/google/callback`，**Then** 回 403 固定 HTML，不回顯參數。
4. **Given** 公開 Host，**When** 學生加入、送出、連學生 WebSocket，**Then** 行為與本機相同。

### Edge Cases

- 硬砍伺服器行程（工作管理員結束 python）時 cloudflared 可能殘留；Ctrl+C 與關閉視窗會一起結束（同一主控台）。
- 新通道網址 DNS 約 60 秒才解析得到；終端機與 README 提示「約 1 分鐘後才連得上」。
- 用公開網址開老師頁時靜態頁仍載得到，API 全部 403；前端顯示提示由 `web-workbench` 處理。

## Requirements *(mandatory)*

- **FR-001**：以 `--tunnel` 或 `QUIZ_TUNNEL=1` 啟動時，系統 MUST 嘗試建立 Cloudflare 快速通道並把網址提供給老師 view `student_url`；失敗 MUST 照常以本機模式運作。
- **FR-002**：老師 REST、老師 WebSocket、Google 回呼 MUST 只接受 Host 主機名 ∈ {127.0.0.1, localhost, [::1]} 且不帶 `cf-connecting-ip`／`cf-ray` 的請求，MUST 在驗金鑰前檢查。
- **FR-003**：學生與公開端點 MUST NOT 受 FR-002 限制。
- **FR-004**：`student_url` MUST 只在老師 view，MUST NOT 出現在學生 view。
- **FR-005**：未要求通道時 MUST 只綁 127.0.0.1；Google OAuth 回呼 MUST 維持 `http://127.0.0.1:8000/api/google/callback`。

## Success Criteria *(mandatory)*

- **SC-001**：`uv run --project server pytest -q server/tests/test_api_host.py server/tests/test_tunnel.py` passed。
- **SC-002**：變異實錄——拿掉 Cloudflare 標頭條件 ⇒ `test_api_host.py` 1 failed；一律視為本機 ⇒ 5 failed。
- **SC-003**：真棧：公開 `/api/public/info` 200、公開 `/api/teacher/state` 403、本機 200、`student_url` 為通道網址。
- **SC-004**：人工驗證 `docs/manual-verification.md` 場次 F（手機 4G 掃碼作答；公開網址開老師頁被拒）。

**矩陣落點**：新增 M-023（X-04、P-06）「經公開網域的請求拿不到老師身分」，守門 `server/tests/test_api_host.py`、`test_tunnel.py`。
