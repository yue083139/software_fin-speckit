# Data Model: 017 easy-setup

對照 `diagrams/017-easy-setup-class.puml`。

| 實體 | 欄位／成員 | 說明 |
|---|---|---|
| `envfile`（新模組） | `ENV_FILE`（固定 repo 根目錄 `.env`）；`write_keys(values, path=ENV_FILE)`、`remove_keys(keys, path=ENV_FILE)` | 只改指定鍵、保留其他行；utf-8-sig 讀、utf-8 寫；暫存檔＋`os.replace` |
| `google_auth.GoogleSession`（增） | `reconfigure(client_id, client_secret)`；`client_id_hint` | 更新用戶端並清空 pending、權杖、email；遮罩 ID |
| `google_auth`（增常數） | `CLIENT_ID_PATTERN`、`CLIENT_SECRET_PATTERN`、`MAX_LEN = 128` | 白名單 |
| `Activity`（增） | `tunnel: "off" \| "starting" \| "on"` | 通道狀態；重置與重新匯入保留 |
| `app`（增） | `tunnel_lock: asyncio.Lock`、`create_app(..., tunnel_factory=Tunnel)` | 序列化起停 |
| `__main__`（改） | `uvicorn.Server`、`open_teacher_page(url, opener=webbrowser.open)`、`--no-browser` | 就緒後開一次 |
| 老師 view（增） | `tunnel` | 學生 view 不帶 |
| `GET /api/teacher/google`（增） | `client_id_hint`、`redirect_uri` | 不含密鑰 |
