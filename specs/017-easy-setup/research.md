# Research: 017 easy-setup（v1.1）

> **v1.1（提案輪評審：架構 CLEARED 0B/1M/3m、紅隊 NOT CLEARED 0B/4M/4m，皆 0 阻斷；負責人指示「提案審完直接實做」）**：①`create_app` 注入 `Tunnel` **實例**，`__main__` 以伺服器埠建立並與 `--tunnel` 共用（兩通道同抽）②建立中按關閉＝取消旗標，等建立完成後停掉並回 off；「建立中再按開啟」409 在鎖內判斷 ③搶答開始後（非準備階段）關閉回 409 ④`.env` 以 `ENV_LINE` 判鍵、同鍵多行只留第一行、`fullmatch` 且寫入即驗證過的原值（不 strip）、暫存檔 `.env.tmp-*` finally 刪除、檢查到寫入整段加鎖、`create_app(env_file=)`（兩通道同抽）⑤`GoogleSession` 世代號：`complete()` await 後世代不同即丟棄 ⑥cloudflared 意外結束由監看任務轉 off ⑦`start-tunnel` 引用全集逐一處理、`Teacher.tsx` 合流解法 ⑧`start.ps1` 只認 Y／y、UAC 與自動開出網址列含 key 列人工驗證、瀏覽器帳號同步風險。

> 與 OpenSpec 組 `openspec/changes/easy-setup/design.md` R1–R6 一一對應、口徑相同（R_n＝D_n）。圖：`diagrams/017-easy-setup-{component,class,sequence}.puml`（v1.1 已依實作回改）。

知識時點：2026-11-26。Google Cloud Console 介面路徑以當日為準（Google Auth Platform 改版後的 `auth/audience`、`auth/clients/create`）；PATH 刷新以探針③實測（`probes/results/2026-11-26-easy-setup.txt`）；自動開瀏覽器與執行期起停 cloudflared 的探針①②由負責人 2026-11-26 在主會話執行（起草會話被權限拒絕），原樣輸出同檔。**負責人 2026-11-26 定案**：契約五端點＋老師 view `tunnel` 欄位批准；系統環境變數另設時只在 README 註明；矩陣 M-025～M-027；合入在 `teacher-key-hidden`（#29）、`teacher-key-error`（#28）之後。

## 背景

負責人 2026-11-26：「現在的啟動過程有點複雜，需要 .env，有辦法簡化或是在後台頁面裡面引導式操作嗎」，裁定四項全做，補充「希望 make dev 之類的啟動後就能直接進後台做」。

## 決策

### R1 啟動後自動開老師頁一次

- `__main__.py` 改用 `uvicorn.Server(config)`，在背景執行緒以新模組 `quiz_server/launch.py` 的 `open_when_ready(is_started, url, opener=webbrowser.open)` 輪詢 `server.started`（每 0.1 秒、最長 30 秒），變 True 後呼叫 `opener("http://127.0.0.1:<埠>/#/teacher?key=<金鑰>")` **恰一次**；之後不再開（同一行程內）。`should_open(no_browser, env)` 集中判斷旗標。`main(argv=None)` 可注入參數供測試。`base` 一律 `http://127.0.0.1:<port>`（不用 `--host` 值，避免 `0.0.0.0` 開出無效網址）。
- 不開的條件（任一）：`--no-browser`、環境變數 `QUIZ_NO_BROWSER=1`、環境變數 `CI` 非空。測試只用 `create_app`，不經 `__main__`，天然不開；`test_launch.py` 以注入的替身 `open_browser` 函式驗計次。
- 終端機照印老師頁與學生頁網址（備援）；`webbrowser.open` 回 False 或拋例外 ⇒ 印「沒有自動開啟瀏覽器，請手動開上面的老師頁網址」，伺服器照常。
- 與 `teacher-key-hidden` 的關係：自動開的網址含金鑰，老師頁載入後由該卡自網址列移除；瀏覽器「記錄」仍可能保留第一筆（該卡已知限制），本卡不改。**風險登記（紅隊外包 A-6）**：瀏覽器帳號同步開啟時，記錄可能上傳到瀏覽器廠商雲端；金鑰只在本機可用（老師端點限本機 Host）且每次啟動更換，列為可接受。
- 成敗判斷**只看 `webbrowser.open` 的回傳值**：探針①在本機 `webbrowser.get().name` 為空字串、`open` 仍回 True 並開啟瀏覽器，故不以瀏覽器名稱判斷；回 False（或拋例外）時只靠終端機印的網址。
- 證偽欄｜屬取捨：自動開瀏覽器省去複製網址，代價是含金鑰網址進瀏覽器紀錄一次；`QUIZ_NO_BROWSER=1` 可關。可證偽：`test_launch.py` 三旗標各 0 次、預設 1 次、`open` 回 False 時印提示；探針①原樣輸出「① webbrowser.get().name：」（空）「① webbrowser.open 回傳：True」。

### R2 Google 設定精靈：伺服器寫 `.env` 並立即生效

- **端點**（皆 `dependencies=teacher`，即先 `is_local` 再驗金鑰）：
  - `GET /api/teacher/google` 回應擴充為 `{configured, signed_in, email, client_id_hint, redirect_uri}`：`client_id_hint` 為遮罩後的用戶端 ID（前 6 碼＋「…」＋`.apps.googleusercontent.com`，未設定為 `null`）；`redirect_uri` 固定 `http://127.0.0.1:8000/api/google/callback`（取自 `google_auth.REDIRECT_URI`，給精靈複製）。
  - `POST /api/teacher/google/config {client_id, client_secret}` ⇒ 驗證 → 寫 `.env` → `GoogleSession.reconfigure()` → 設 `os.environ` 兩鍵 → 回 `GET` 同形狀狀態。
  - `DELETE /api/teacher/google/config` ⇒ 自 `.env` 移除兩鍵、`GoogleSession.reconfigure(None, None)`、移除 `os.environ` 兩鍵 → 回狀態（清除只在未登入時允許，故無權杖可清）。
- **驗證（白名單，先於任何寫入）**：伺服器**不 strip**，以 `re.fullmatch` 對原值比對（`$` 會放過尾端換行，故不用 `match`），寫入 `.env` 的就是驗證過的原值；前端送出前自行去頭尾空白。`client_id` 須符合 `^[0-9]{4,30}-[a-z0-9]{8,64}\.apps\.googleusercontent\.com$`；`client_secret` 須符合 `^GOCSPX-[A-Za-z0-9_-]{20,64}$`；兩者長度 ≤ 128；不符 ⇒ 422「用戶端 ID 格式不符（應以 .apps.googleusercontent.com 結尾）」／「用戶端密鑰格式不符（應以 GOCSPX- 開頭）」。白名單本身排除換行、`=`、引號、`#`，故無法注入第二行或其他鍵。錯誤訊息不回顯輸入值。
- **已登入時變更**：`signed_in` 為 True ⇒ 409「請先登出 Google 再變更設定」（避免結束後尚未匯出時被換掉用戶端而失去寫回權限）。清除設定同規則。
- **寫檔**（新模組 `quiz_server/envfile.py`；`ENV_FILE`、`ENV_LINE` 自 `__main__.py` 移入，`load_env` 改用）：路徑由 `create_app(env_file=ENV_FILE)` 注入（正式碼固定 repo 根目錄 `.env`，**不接受請求指定路徑**；測試傳 tmp_path）；以 utf-8-sig 讀（相容既有帶 BOM 檔）、以 utf-8（無 BOM）寫；逐行以 `ENV_LINE` 判斷鍵名（與 `load_env` 同一規則，故「`KEY = 值`」這種帶空白的寫法也認得），同鍵的**第一行**換成新值、**其後同鍵行全刪**（重複鍵時 `load_env` 取第一行，留著後面的行會讓兩邊語意分岔）；其餘行（含註解、其他鍵、空行）原樣保留；缺的鍵附加在檔尾；先寫同目錄暫存檔 `.env.tmp-<隨機>`（`.gitignore` 的 `.env.*` 已涵蓋）再 `os.replace` 原子取代，`finally` 刪除殘留暫存檔；檔案不存在則新建。清除時刪去所有同鍵行。
- **加鎖**：`config_lock` 涵蓋「檢查 `signed_in` → 寫 `.env` → `reconfigure` → 設 `os.environ`」整段，兩個分頁同時儲存不會交錯。
- **立即生效**：`GoogleSession.reconfigure(client_id, client_secret)` 更新兩欄、清空 `_pending`、權杖與 email，並**遞增世代號** `_generation`；`complete()` 在 await 換權杖前記下世代號，await 回來若世代已變即丟棄結果並以 `GoogleCallbackError` 收場（舊用戶端發起、尚未完成的登入不會在新設定下落地）；`app.state.google` 物件不換（既有閉包引用不變）。同時設 `os.environ`，重啟後 `load_env` 讀 `.env` 結果一致（`load_env` 不覆蓋既有環境變數：若老師在系統環境變數另設了 GOOGLE_CLIENT_ID，重啟後以系統值為準——README 註明）。
- **祕密衛生**：密鑰不出現在任何回應（含錯誤）、view、日誌；`.env` 已在 `.gitignore`；`gate-secrets` 的 `GOCSPX-` 形狀持續擋入庫。
- **通道後端**：實作的 `Tunnel` 一律指向本伺服器（`http://127.0.0.1:<埠>`，老師端點受 `is_local` 保護）；**探針與測試不得以檔案伺服器（如 `SimpleHTTPRequestHandler`）接通道**——通道是公開的，會把工作目錄檔案外洩（負責人 2026-11-26 指出探針舊版此洞，已改固定 204 handler）。
- **前端精靈**（`GooglePanel` 未設定時展開）：六步——①建立專案（`https://console.cloud.google.com/projectcreate`）②啟用 Google Sheets API（`…/apis/library/sheets.googleapis.com`）③啟用 Google Drive API（`…/apis/library/drive.googleapis.com`）④Google Auth Platform「目標對象」選外部、保持測試中、加入測試使用者（`…/auth/audience`）⑤建立用戶端：網頁應用程式，重新導向 URI 一鍵複製（`…/auth/clients/create`）⑥貼上用戶端 ID 與密鑰按「儲存設定」。連結以新分頁開；每步附一句「找不到時：在 Console 上方搜尋列搜尋『…』」。已設定時顯示 `client_id_hint` 與「變更設定」「清除設定」。
- 證偽欄｜可證偽：`test_google_config.py`——`.env` 既有 `FOO=1`、註解、BOM、`GOOGLE_CLIENT_ID = 舊值`（帶空白）與重複鍵時只留一行新值、其他行不變；含換行（含**尾端**換行）、`=`、超長、錯前綴 422 且檔案位元組不變；寫入後無 `.env.tmp-*` 殘留；`os.environ` 一律以 monkeypatch 隔離；世代號：發起登入 → 重設定 → 回呼 ⇒ 不登入；回應與 `caplog` 全文不含密鑰；公開 Host 403 先於 401；已登入 409；存後 `POST /api/teacher/google/login` 回授權網址含新 client_id。屬取捨：伺服器寫入本機檔案（新權能），以「固定路徑＋白名單＋限本機＋金鑰」收斂；不做加密（`.env` 本來就是明文、僅本機）。

### R3 老師頁一鍵開關手機連線

- `create_app(..., tunnel: Tunnel | None = None)` 注入**實例**（兩通道同抽：工廠無從得知伺服器埠）；`__main__` 以 `Tunnel(a.port)` 建立並傳入，`--tunnel` 啟動也用同一實例，故 DELETE 停得掉啟動時開的通道；`None`（測試預設）⇒ 開啟回 503。`Tunnel` 增 `available()`（`find_cloudflared()` 非 None）與 `alive()`（子行程仍在）。`tunnel_lock` 序列化狀態轉換（不包住約 4 秒的 `start`）。
- `POST /api/teacher/tunnel`（老師，不限階段）：**鎖內**判斷——已 `on` ⇒ 200 回現值（冪等）；`starting` ⇒ 409「手機連線建立中」；`tunnel` 為 None 或 `available()` 為 False ⇒ 503「找不到 cloudflared，請先安裝：winget install --id Cloudflare.cloudflared -e」；否則清取消旗標、清「建立完成」事件、經 `Activity.set_tunnel("starting", None)` 推播。**鎖外** `await asyncio.to_thread(tunnel.start, 30)`。回到**鎖內**：取消旗標已設 ⇒ `stop()`、`off`、回 `{tunnel: "off", student_url: null}`；`start` 回 None ⇒ `off`、504「建立手機連線逾時，請再試一次」；否則 `on`＋`public_url`、回 `{tunnel: "on", student_url}`；任何結果（含例外）`finally` 設「建立完成」事件並確保不停在 `starting`。
- `DELETE /api/teacher/tunnel`（老師）：**非準備階段 ⇒ 409「搶答進行中不能關閉手機連線」**（紅隊重要：搶答中關掉會讓手機上的組別全部斷線；開啟不限階段）。鎖內：`starting` ⇒ 設取消旗標，鎖外等「建立完成」事件後回 `{tunnel: "off", student_url: null}`（POST 那端負責停子行程）；`on` ⇒ `stop()`（`to_thread`）、`off` 推播；已 `off` 冪等 200。
- **意外結束（紅隊次要）**：lifespan 啟動一個監看任務，每 2 秒（`create_app(tunnel_watch_interval=)` 可調）在 `on` 時檢查 `tunnel.alive()`，已死 ⇒ 鎖內轉 `off`、清 `public_url` 並推播，記 warning（不記網址）。lifespan 結束時取消監看並 `stop()`。
- 狀態只經 `Activity.set_tunnel(state, url)` 在活動鎖內改變並遞增版本（`server/CLAUDE.md`：活動狀態只在 `Activity` 內改變）。
- 老師 view 新增 `tunnel: "off"|"starting"|"on"`；學生 view 不帶（沿用 student-qr「`student_url` 只在老師 view」）。
- `--tunnel` 啟動參數保留：`__main__` 在伺服器啟動前以同一 `Tunnel` 起通道並把結果傳入 `create_app`（初始 `tunnel="on"`）；伺服器結束（`finally`）停止子行程；app lifespan shutdown 也呼叫 `stop()`（重複呼叫安全，`Tunnel.stop` 已檢查 `poll()`）。
- **移除 `start-tunnel.cmd`**（按鈕取代，少一個要選的入口）；保留 `make dev-tunnel`、`--tunnel`、`QUIZ_TUNNEL=1` 給開發者。引用全集（`git grep -n -e start-tunnel -e -Tunnel -- :/ ':!openspec/changes/archive' ':!docs/ai-logs'`）逐一處理：`README.md:36` 改述為老師頁按鈕；`docs/manual-verification.md:120-121` 場次 F 改寫；`start.ps1:2` 註解與 `-Tunnel` 參數及分支刪除；`web/src/pages/Teacher.tsx:241` 提示改為「按下方『開啟手機連線』」；`web/src/pages/qr.test.tsx:18` 斷言同步；`docs/parity.md:55`（student-qr 歷史列）**有意不改**（記錄當時行為），由本卡 §5 紀錄列說明移除。Makefile 無此引用（只有 `dev-tunnel` 目標，保留）。
- **`Teacher.tsx` 合流**：本卡已 rebase 到含 #29 `teacher-key-hidden` 的 `origin/dev`（`BadKeyNotice`、`isBadTeacherKey`、`setError` 401 分支），疊在其上修改；#28 `teacher-key-error` 只剩伺服器 WebSocket 段與契約 :61，誰後合入誰 rebase。
- 通道開啟期間 DNS 生效約 1 分鐘（student-qr 探針）：前端在 `on` 後顯示「新網址約 1 分鐘後才連得上」。
- 證偽欄｜可證偽：`test_tunnel_api.py` 以假 Tunnel（可控延遲、可回 None、可模擬找不到、可模擬死亡）斷言狀態序列、503／504、建立中再開 409 且只呼叫一次 `start`、建立中關閉 ⇒ 兩端都回 off 且 `stop` 被呼叫、搶答中關閉 409、子行程死亡 ⇒ 轉 off、DELETE 後 `student_url` 為 null、學生 view 不含 `tunnel`／`student_url`、公開 Host 403；`test_launch.py` 斷言 `__main__` 的通道埠＝伺服器埠且 `create_app` 收到同一實例、`--tunnel` 時 `start` 在同一實例上；探針②（待執行）起停 3 次行程數回基準。屬取捨：通道由老師按鈕即時開，伺服器執行期多一個外部子行程；以鎖序列化並在關閉時回收。探針②原樣輸出：三次「start 3.9／3.9／4.0 秒 → 取得 https://<遮蔽>.trycloudflare.com/；執行中 2；stop 後 1（基準 1）」，「結束 cloudflared 行程數：1（基準 1）」——起停不殘留；建立約 4 秒，前端 `starting` 狀態有意義，30 秒逾時足夠。

### R4 頂部「開始前的設定」清單

- 老師頁內容區最上方，`phase=preparing` 時顯示一張卡「開始前的設定」，三列：
  - Google：`未設定`（✗，點 → `#google`）／`已設定，尚未登入`（!）／`已登入 <email>`（✓）。
  - 手機連線：`關閉`（選用，點 → `#link`）／`建立中…`／`已開啟`（✓）。
  - 題目：`尚未匯入`（✗，點 → `#import`）／`已匯入 N 題`（✓）。
- 只讀既有 view 與 Google 狀態，不新增伺服器欄位；點列以既有導覽捲動（`scrollIntoView`）。其他階段不顯示。不自動捲動（負責人傾向清單；自動捲動會與老師自己的導覽衝突，評估後不做）。
- Google 未設定時「Google 帳號」分區直接展開精靈（R2），無需另點。
- 證偽欄｜可證偽：元件測試三列各狀態文字與點擊後呼叫捲動；非 preparing 不渲染。

### R5 `start.ps1` 缺工具時詢問代裝

- 缺 uv 或 Node.js：印說明後 `Read-Host '要幫你用 winget 安裝嗎？(Y/N)'`；**只認 Y／y**，空值（直接按 Enter）與其他輸入一律視為 N；輸入 Y／y ⇒ `winget install --id <id> -e --accept-source-agreements --accept-package-agreements`，再以 `[Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')` 刷新 `$env:Path` 並重查；仍找不到 ⇒ 原 Fail 訊息（請重開視窗）。N 或非互動（`Read-Host` 拋錯）⇒ 原 Fail。
- 找不到 `winget` ⇒ 印 Microsoft Store「應用程式安裝程式」說明與手動安裝網址，Fail。
- cloudflared 不在啟動時詢問（R3 按需提示）。
- `start.cmd` 維持 ASCII（`start.cmd:3` 註解：cmd 讀 UTF-8 批次檔位置錯亂）；中文提示只放 `start.ps1`。
- 證偽欄｜可證偽：探針③原樣輸出「移除 cloudflared 目錄後 Get-Command 找得到：False」「刷新 $env:Path 後：True → C:\Program Files (x86)\cloudflared\cloudflared.exe」（PowerShell 5.1.26100.9818）。安裝流程本身（winget 真裝 uv／node，可能跳出 UAC 提權視窗須按「是」）不自動測，列人工驗證。

### R6 契約與文件

- `contracts/api.md`：`GET /api/teacher/google` 回應擴充、`POST`／`DELETE /api/teacher/google/config`、`POST`／`DELETE /api/teacher/tunnel`（關閉另有 409 非準備階段）、老師 view `tunnel`；錯誤碼先後沿用「403 非本機 → 401 金鑰 → 422 本體 → 409 狀態 → 503／504」。
- `.env.example` 註解改為「可在老師頁 Google 設定精靈填寫，或手動複製本檔成 .env」。
- README「開始使用」改為三步：裝工具（或讓 start.cmd 代裝）→ 雙擊 start.cmd（自動開老師頁）→ 依老師頁頂部清單完成設定；「Google 試算表設定」改指向精靈，手動 `.env` 列為備援。
- `docs/manual-verification.md`：場次 A 第 1、6 步、場次 F 改寫；新增步驟「清除設定 → 精靈重設 → 不重啟即可登入」「自動開出的網址列先含 `key=`、載入後被移除」「缺工具時 winget 安裝可能跳 UAC」（紅隊次要 A-7）。

## 風險

- Google Console 網址日後改版：每步附搜尋關鍵字作備援。
- 無桌面環境（服務帳號、遠端無頭）`webbrowser.open` 可能回 False：R1 只印網址，不影響其他決策。
