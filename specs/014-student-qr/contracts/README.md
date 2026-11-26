# 014 student-qr 介面契約

**狀態：負責人 2026-11-26 照傾向批准（research R2、R3）**；實作同批改 [`/contracts/api.md`](../../../contracts/api.md)。

| 位置 | 增加 | 規則 |
|---|---|---|
| 身分（全部老師 REST、`role=teacher` WebSocket、`GET /api/google/callback`） | 本機限制 | Host 主機名 ∈ {127.0.0.1, localhost, [::1]} 且不帶 `cf-connecting-ip`／`cf-ray`；否則驗金鑰前回 403 `{"detail": "老師頁只能在本機開啟"}`（WS 4403；回呼固定 HTML） |
| 老師 view | `student_url` | 通道成功為 `https://<隨機>.trycloudflare.com/`，否則 `null`；學生 view 不含 |

**不變**：學生與公開端點、錯誤碼、學生 view、未帶 `--tunnel` 時的所有行為。
