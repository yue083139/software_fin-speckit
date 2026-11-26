# 017 easy-setup 介面契約

**狀態：負責人 2026-11-26 批准（research R6）**；實作同批改 [`/contracts/api.md`](../../../contracts/api.md)。所有新端點身分＝老師（先本機檢查 403，再金鑰 401）。

| 方法與路徑 | 本體 | 成功回應 | 錯誤（依序） |
|---|---|---|---|
| `GET /api/teacher/google`（擴充） | — | `{configured, signed_in, email, client_id_hint, redirect_uri}` | 403、401 |
| `POST /api/teacher/google/config` | `{client_id, client_secret}` | 同上狀態 | 403、401、422 格式不符（不回顯輸入）、409「請先登出 Google 再變更設定」 |
| `DELETE /api/teacher/google/config` | — | 同上狀態（`configured: false`） | 403、401、409 |
| `POST /api/teacher/tunnel` | — | `{tunnel: "on", student_url}`（已開則冪等；建立中被關閉回 `{tunnel: "off", student_url: null}`；不限階段） | 403、401、409「手機連線建立中」、503「找不到 cloudflared，請先安裝：winget install --id Cloudflare.cloudflared -e」、504「建立手機連線逾時，請再試一次」 |
| `DELETE /api/teacher/tunnel` | — | `{tunnel: "off", student_url: null}`（已關則冪等；建立中則等建立完成後停止） | 403、401、409「搶答進行中不能關閉手機連線」（非準備階段） |
| 老師 view | — | 新增 `tunnel: "off" \| "starting" \| "on"` | 學生 view 不含 |

**不變**：學生與公開端點、學生 view、既有 Google 登入／回呼／登出、未按開啟時的本機模式。
