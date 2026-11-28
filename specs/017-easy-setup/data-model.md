# Data Model: 017 easy-setup（v1.1）

對照 `diagrams/017-easy-setup-class.puml`。

| 實體 | 欄位／成員 | 說明 |
|---|---|---|
| `envfile`（新模組） | `ENV_FILE`、`ENV_LINE`（自 `__main__` 移入）；`read_lines(path)`、`write_keys(values, path)`、`remove_keys(keys, path)`、`load_env(path)` | 以 `ENV_LINE` 判鍵；同鍵第一行換新值、其後同鍵行刪除；其他行保留；utf-8-sig 讀、utf-8 寫；暫存檔 `.env.tmp-*`＋`os.replace`，finally 刪除 |
| `launch`（新模組） | `should_open(no_browser, env)`、`open_when_ready(is_started, url, opener, timeout, interval, sleep, now)`、`NO_BROWSER_HINT` | 只看 `opener` 回傳值；False 或例外印提示 |
| `google_auth`（增） | `CLIENT_ID_PATTERN`、`CLIENT_SECRET_PATTERN`、`MAX_LEN = 128`、`BAD_CLIENT_ID`、`BAD_CLIENT_SECRET`、`GoogleConfigInvalid`、`validate_client(id, secret)` | fullmatch 白名單；422 不回顯輸入 |
| `GoogleSession`（增） | `_generation`；`reconfigure(id, secret)`；`client_id_hint`；`status()` 增 `client_id_hint`、`redirect_uri` | reconfigure 遞增世代、清 pending 與權杖；`complete()` await 後世代不同即丟棄 |
| `tunnel.Tunnel`（增） | `available()`、`alive()` | 找得到 cloudflared、子行程仍在 |
| `Activity`（增） | `tunnel_state: "off" \| "starting" \| "on"`；`set_tunnel(state, url)` | 在活動鎖內改狀態並遞增版本；重置與重新匯入保留 |
| `create_app`（增參數） | `tunnel: Tunnel \| None`、`env_file: Path = ENV_FILE`、`tunnel_watch_interval: float = 2.0` | 注入實例；`tunnel_lock`、取消旗標、「建立完成」事件；lifespan 監看與收尾；`config_lock` |
| `__main__`（改） | `main(argv=None)`、`start_browser(server, url)`、`--no-browser` | `Tunnel(a.port)` 注入 app；`uvicorn.Server` 就緒後開一次 |
| 老師 view（增） | `tunnel` | 學生 view 不帶 |
