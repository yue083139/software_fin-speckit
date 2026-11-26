# server — 元件規範

- Python 3.12、uv 管理依賴（`uv sync --project server`、`uv run --project server pytest`）；ruff 為唯一 lint 工具。
- 活動狀態只在 `quiz_server.activity.Activity` 內改變，所有改變經同一把 `asyncio.Lock`；不得在端點或 view 裡直接改狀態。
- 送往學生的畫面狀態**只能**由 `quiz_server.views.student_view` 產生，學生身分只能由組別憑證反查（`Activity.team_of`）；送出成功回應與錯誤回應不得含他組資料。新增任何學生可見的欄位或通道，必須同批加「搶答中他組答案不出現」的負例測試（`CLAUDE.md`「作答隔離」）。
- 搶答結果只經 `quiz_server.scoring` 的規則產生，不在 view、匯出或前端重算。
- Guided Notes 定位只能來自解析結果；定位程式中不得出現寫死的儲存格座標（`CLAUDE.md`「Guided Notes 動態定位」）。
- 日誌只記活動版本、組別、題號、序號與結果碼；不記學生答案、不記老師金鑰。
- 測試不得連網：Google Sheets 下載以 httpx `MockTransport` 替身。
