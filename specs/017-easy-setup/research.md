# Research: 017 easy-setup（v1.0）

> 與 OpenSpec 組 `openspec/changes/easy-setup/design.md` R1–R6 一一對應、口徑相同（R_n＝D_n）。圖：`diagrams/017-easy-setup-{component,class,sequence}.puml`。

知識時點：2026-11-26。Google Cloud Console 介面路徑以當日為準（Google Auth Platform 改版後的 `auth/audience`、`auth/clients/create`）；PATH 刷新以探針③實測（`probes/results/2026-11-26-easy-setup.txt`）；自動開瀏覽器與執行期起停 cloudflared 的探針①②**起草時被執行環境權限拒絕，待負責人執行後回填**（tasks 0.2，阻塞提案輪評審前定稿）。

## 背景

負責人 2026-11-26：「現在的啟動過程有點複雜，需要 .env，有辦法簡化或是在後台頁面裡面引導式操作嗎」，裁定四項全做，補充「希望 make dev 之類的啟動後就能直接進後台做」。

## 決策

### R1 啟動後自動開老師頁一次

- `__main__.py` 改用 `uvicorn.Server(config)`，在背景執行緒輪詢 `server.started`（每 0.1 秒、最長 30 秒），變 True 後呼叫 `webbrowser.open(f"{base}/#/teacher?key={key}")` **恰一次**；之後不再開（同一行程內）。`base` 一律 `http://127.0.0.1:<port>`（不用 `--host` 值，避免 `0.0.0.0` 開出無效網址）。
- 不開的條件（任一）：`--no-browser`、環境變數 `QUIZ_NO_BROWSER=1`、環境變數 `CI` 非空。測試只用 `create_app`，不經 `__main__`，天然不開；`test_launch.py` 以注入的替身 `open_browser` 函式驗計次。
- 終端機照印老師頁與學生頁網址（備援）；`webbrowser.open` 回 False 或拋例外 ⇒ 印「沒有自動開啟瀏覽器，請手動開上面的老師頁網址」，伺服器照常。
- 與 `teacher-key-hidden` 的關係：自動開的網址含金鑰，老師頁載入後由該卡自網址列移除；瀏覽器「記錄」仍可能保留第一筆（該卡已知限制），本卡不改。
- 證偽欄｜屬取捨：自動開瀏覽器省去複製網址，代價是含金鑰網址進瀏覽器紀錄一次；`QUIZ_NO_BROWSER=1` 可關。可證偽：`test_launch.py` 三旗標各 0 次、預設 1 次；探針①（待執行）`webbrowser.open` 回 True。

### R2 Google 設定精靈：伺服器寫 `.env` 並立即生效

- **端點**（皆 `dependencies=teacher`，即先 `is_local` 再驗金鑰）：
  - `GET /api/teacher/google` 回應擴充為 `{configured, signed_in, email, client_id_hint, redirect_uri}`：`client_id_hint` 為遮罩後的用戶端 ID（前 6 碼＋「…」＋`.apps.googleusercontent.com`，未設定為 `null`）；`redirect_uri` 固定 `http://127.0.0.1:8000/api/google/callback`（取自 `google_auth.REDIRECT_URI`，給精靈複製）。
  - `POST /api/teacher/google/config {client_id, client_secret}` ⇒ 驗證 → 寫 `.env` → `GoogleSession.reconfigure()` → 設 `os.environ` 兩鍵 → 回 `GET` 同形狀狀態。
  - `DELETE /api/teacher/google/config` ⇒ 自 `.env` 移除兩鍵、清空 session（含權杖，等同登出但不呼叫撤銷）、移除 `os.environ` 兩鍵 → 回狀態。
- **驗證（白名單，先於任何寫入）**：去頭尾空白後，`client_id` 須符合 `^[0-9]{4,30}-[a-z0-9]{8,64}\.apps\.googleusercontent\.com$`；`client_secret` 須符合 `^GOCSPX-[A-Za-z0-9_-]{20,64}$`；兩者長度 ≤ 128；不符 ⇒ 422「用戶端 ID 格式不符（應以 .apps.googleusercontent.com 結尾）」／「用戶端密鑰格式不符（應以 GOCSPX- 開頭）」。白名單本身排除換行、`=`、引號、`#`，故無法注入第二行或其他鍵。錯誤訊息不回顯輸入值。
- **已登入時變更**：`signed_in` 為 True ⇒ 409「請先登出 Google 再變更設定」（避免結束後尚未匯出時被換掉用戶端而失去寫回權限）。清除設定同規則。
- **寫檔**（新模組 `quiz_server/envfile.py`）：路徑固定 `ENV_FILE`（repo 根目錄 `.env`，`__main__.py` 同一常數，**不接受請求指定路徑**）；以 utf-8-sig 讀（相容既有帶 BOM 檔）、以 utf-8（無 BOM）寫；逐行掃描，只取代 `GOOGLE_CLIENT_ID=`、`GOOGLE_CLIENT_SECRET=` 兩行（大小寫須相符，比照 `load_env` 的 `ENV_LINE`），其餘行（含註解、其他鍵、空行）原樣保留；缺的鍵附加在檔尾；先寫同目錄暫存檔再 `os.replace` 原子取代；檔案不存在則新建。清除時刪去兩行。
- **立即生效**：`GoogleSession.reconfigure(client_id, client_secret)` 更新兩欄並清空 `_pending`、權杖與 email；`app.state.google` 物件不換（既有閉包引用不變）。同時設 `os.environ`，重啟後 `load_env` 讀 `.env` 結果一致（`load_env` 不覆蓋既有環境變數：若老師在系統環境變數另設了 GOOGLE_CLIENT_ID，重啟後以系統值為準——README 註明）。
- **祕密衛生**：密鑰不出現在任何回應（含錯誤）、view、日誌；`.env` 已在 `.gitignore`；`gate-secrets` 的 `GOCSPX-` 形狀持續擋入庫。
- **前端精靈**（`GooglePanel` 未設定時展開）：六步——①建立專案（`https://console.cloud.google.com/projectcreate`）②啟用 Google Sheets API（`…/apis/library/sheets.googleapis.com`）③啟用 Google Drive API（`…/apis/library/drive.googleapis.com`）④Google Auth Platform「目標對象」選外部、保持測試中、加入測試使用者（`…/auth/audience`）⑤建立用戶端：網頁應用程式，重新導向 URI 一鍵複製（`…/auth/clients/create`）⑥貼上用戶端 ID 與密鑰按「儲存設定」。連結以新分頁開；每步附一句「找不到時：在 Console 上方搜尋列搜尋『…』」。已設定時顯示 `client_id_hint` 與「變更設定」「清除設定」。
- 證偽欄｜可證偽：`test_google_config.py`——`.env` 既有 `FOO=1`、註解、BOM 時只改兩鍵；含 `\n`、`=`、超長、錯前綴 422 且檔案位元組不變；回應與 `caplog` 全文不含密鑰；公開 Host 403 先於 401；已登入 409；存後 `POST /api/teacher/google/login` 回授權網址含新 client_id。屬取捨：伺服器寫入本機檔案（新權能），以「固定路徑＋白名單＋限本機＋金鑰」收斂；不做加密（`.env` 本來就是明文、僅本機）。

### R3 老師頁一鍵開關手機連線

- `create_app(..., tunnel_factory=Tunnel)`：app 持有單一 `Tunnel`；`app.state` 新增 `asyncio.Lock` 序列化起停。
- `POST /api/teacher/tunnel`（老師）：已 `on` ⇒ 200 回現值（冪等）；`starting` 中 ⇒ 409「手機連線建立中」；否則設 `Activity.tunnel="starting"` 並推播 → `await asyncio.to_thread(tunnel.start, 30)` → 成功設 `public_url`、`tunnel="on"` 推播，回 `{tunnel: "on", student_url}`；找不到 cloudflared ⇒ `tunnel="off"`、503「找不到 cloudflared，請先安裝：winget install --id Cloudflare.cloudflared -e」；逾時 ⇒ `off`、504「建立手機連線逾時，請再試一次」。`find_cloudflared()` 先於起子行程判斷，以分 503／504。
- `DELETE /api/teacher/tunnel`（老師）：`tunnel.stop()`（`to_thread`）、`public_url=None`、`tunnel="off"`、推播；已 off 冪等 200。
- 老師 view 新增 `tunnel: "off"|"starting"|"on"`；學生 view 不帶（沿用 student-qr「`student_url` 只在老師 view」）。
- `--tunnel` 啟動參數保留：`__main__` 在伺服器啟動前以同一 `Tunnel` 起通道並把結果傳入 `create_app`（初始 `tunnel="on"`）；伺服器結束（`finally`）停止子行程；app lifespan shutdown 也呼叫 `stop()`（重複呼叫安全，`Tunnel.stop` 已檢查 `poll()`）。
- **移除 `start-tunnel.cmd`**（按鈕取代，少一個要選的入口）；保留 `make dev-tunnel`、`--tunnel`、`QUIZ_TUNNEL=1` 給開發者；README 與手冊場次 F 改為「老師頁按『開啟手機連線』」。
- 通道開啟期間 DNS 生效約 1 分鐘（student-qr 探針）：前端在 `on` 後顯示「新網址約 1 分鐘後才連得上」。
- 證偽欄｜可證偽：`test_tunnel_api.py` 以假 Tunnel（可控延遲、可回 None、可模擬找不到）斷言狀態序列、503／504、並發兩次 POST 只呼叫一次 `start`、DELETE 後 `student_url` 為 null、學生 view 不含 `tunnel`／`student_url`、公開 Host 403；探針②（待執行）起停 3 次行程數回基準。屬取捨：通道由老師按鈕即時開，伺服器執行期多一個外部子行程；以鎖序列化並在關閉時回收。

### R4 頂部「開始前的設定」清單

- 老師頁內容區最上方，`phase=preparing` 時顯示一張卡「開始前的設定」，三列：
  - Google：`未設定`（✗，點 → `#google`）／`已設定，尚未登入`（!）／`已登入 <email>`（✓）。
  - 手機連線：`關閉`（選用，點 → `#link`）／`建立中…`／`已開啟`（✓）。
  - 題目：`尚未匯入`（✗，點 → `#import`）／`已匯入 N 題`（✓）。
- 只讀既有 view 與 Google 狀態，不新增伺服器欄位；點列以既有導覽捲動（`scrollIntoView`）。其他階段不顯示。不自動捲動（負責人傾向清單；自動捲動會與老師自己的導覽衝突，評估後不做）。
- Google 未設定時「Google 帳號」分區直接展開精靈（R2），無需另點。
- 證偽欄｜可證偽：元件測試三列各狀態文字與點擊後呼叫捲動；非 preparing 不渲染。

### R5 `start.ps1` 缺工具時詢問代裝

- 缺 uv 或 Node.js：印說明後 `Read-Host '要幫你用 winget 安裝嗎？(Y/N)'`；輸入 Y／y ⇒ `winget install --id <id> -e --accept-source-agreements --accept-package-agreements`，再以 `[Environment]::GetEnvironmentVariable('Path','Machine') + ';' + [Environment]::GetEnvironmentVariable('Path','User')` 刷新 `$env:Path` 並重查；仍找不到 ⇒ 原 Fail 訊息（請重開視窗）。N 或非互動（`Read-Host` 拋錯）⇒ 原 Fail。
- 找不到 `winget` ⇒ 印 Microsoft Store「應用程式安裝程式」說明與手動安裝網址，Fail。
- cloudflared 不在啟動時詢問（R3 按需提示）。
- `start.cmd` 維持 ASCII（`start.cmd:3` 註解：cmd 讀 UTF-8 批次檔位置錯亂）；中文提示只放 `start.ps1`。
- 證偽欄｜可證偽：探針③原樣輸出「移除 cloudflared 目錄後 Get-Command 找得到：False」「刷新 $env:Path 後：True → C:\Program Files (x86)\cloudflared\cloudflared.exe」（PowerShell 5.1.26100.9818）。安裝流程本身（winget 真裝 uv／node）不自動測，列人工驗證。

### R6 契約與文件

- `contracts/api.md`：`GET /api/teacher/google` 回應擴充、`POST`／`DELETE /api/teacher/google/config`、`POST`／`DELETE /api/teacher/tunnel`、老師 view `tunnel`；錯誤碼先後沿用「403 非本機 → 401 金鑰 → 422 本體 → 409 狀態 → 503／504」。
- `.env.example` 註解改為「可在老師頁 Google 設定精靈填寫，或手動複製本檔成 .env」。
- README「開始使用」改為三步：裝工具（或讓 start.cmd 代裝）→ 雙擊 start.cmd（自動開老師頁）→ 依老師頁頂部清單完成設定；「Google 試算表設定」改指向精靈，手動 `.env` 列為備援。
- `docs/manual-verification.md`：場次 A 第 1、6 步、場次 F 改寫；新增步驟「清除設定 → 精靈重設 → 不重啟即可登入」。

## 風險

- Google Console 網址日後改版：每步附搜尋關鍵字作備援。
- 探針①②未跑：若 `webbrowser.open` 在 uv 子行程無效（例：服務帳號下無桌面），R1 退回只印網址，不影響其他決策；若起停殘留行程，R3 加 `taskkill /T` 收尾。兩者阻塞提案輪定稿。
