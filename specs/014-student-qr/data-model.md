# Data Model: 014 student-qr

對照 `diagrams/014-student-qr-class.puml`。

| 實體 | 欄位／成員 | 說明 |
|---|---|---|
| `Activity`（增） | `public_url: str \| None` | 通道公開網址；伺服器設定，重置與重新匯入保留 |
| `app`（增常數） | `LOCAL_HOSTNAMES`、`TUNNEL_HEADERS`、`WS_NOT_LOCAL = 4403`、`NOT_LOCAL` | 本機允許清單、Cloudflare 標頭、WS 關閉碼、403 訊息 |
| `app.is_local(headers)`（新，`create_app` 內） | → `bool` | Host 主機名 ∈ `LOCAL_HOSTNAMES` 且無 `TUNNEL_HEADERS` |
| `tunnel.Tunnel`（新） | `port`、`proc`；`start(timeout=30) -> str \| None`、`stop()` | cloudflared 子行程起停 |
| `tunnel.parse_url(line)`、`wait_for_url(stream, timeout)`、`find_cloudflared()`（新） | → `str \| None` | 只認表框列；PATH 再預設安裝路徑 |
| 老師 view（增） | `student_url: str \| null` | 學生 view 不帶 |
