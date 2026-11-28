# software_fin — Vibe Coding 課堂搶答系統（SpecKit 組）

NCU SE6005 2026 軟體工程期末專題。老師匯入填空式學習單（Guided Notes），開啟搶答後各組線上作答，伺服器判定最快送出的組別；結束後揭曉結果，並把搶答成功的答案寫回原 Guided Notes 的填空格。

本 repo 以 **SpecKit** 流程開發（constitution → specify＋PlantUML 圖 → clarify → plan → tasks → analyze → implement，導入 Diagram First Development）；姊妹 repo [`software_fin-openspec`](../software_fin-openspec) 以另一套流程實作**相同功能**。

| 文件 | 內容 |
|---|---|
| [`docs/product-trd.md`](docs/product-trd.md) | **第一次看專案先讀這份**：產品一句話、功能一覽、專案特色、架構與閱讀路線 |
| [`docs/requirements.md`](docs/requirements.md) | 需求基線（兩組共用，編號 R-／X-／P-） |
| [`docs/parity.md`](docs/parity.md) | 兩組功能一致協議、共用技術選型、功能清單與未決事項 |
| [`docs/trd-game-modes.md`](docs/trd-game-modes.md)、[`docs/research/competitors.md`](docs/research/competitors.md) | 多模式搶答 TRD（時間計分、雙倍分數、組隊等）與競品探索 |
| [`CLAUDE.md`](CLAUDE.md)／`AGENTS.md` | AI 代理工程規範（Claude Code／Codex） |
| [`docs/workflow.md`](docs/workflow.md) | 開發工作流導讀 |
| [`docs/manual-verification.md`](docs/manual-verification.md) | 人工驗證手冊（需求 P-05）：給組員照做的場次與結果表 |
| [`docs/demo-recording.md`](docs/demo-recording.md) | Demo 影片錄製指南：課程要求對照、錄前準備、分鏡時間表（≤ 4:40）、OpenSpec／SpecKit 兩部的差異段落、錄後檢查表 |
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md)、[`specs/`](specs/)、[`diagrams/`](diagrams/) | 憲章、各子功能規格、PlantUML 圖表（評分檢驗 constitution／spec／plan／tasks／圖表） |

## 開始使用（老師／Demo）

第一次使用照下面五步走，約 15 分鐘（其中 Google 設定約 5–10 分鐘，只做一次）。之後每次只要第 2 步。

### 1. 準備工具（只要一次）

只需要 Windows 與網路。**不用自己先裝任何東西**：第 2 步的 `start.cmd` 發現缺 uv 或 Node.js 時會問「要幫你用 winget 安裝嗎？(Y/N)」，輸入 **Y** 就自動裝（可能跳出「是否允許變更」視窗，按「是」）；只認 Y／y，直接按 Enter 視為不裝。Python 不用另外裝，uv 會自動下載。

想自己先裝也可以，在 PowerShell 執行：

```powershell
winget install --id astral-sh.uv -e
winget install --id OpenJS.NodeJS.LTS -e
```

### 2. 啟動

在檔案總管雙擊 repo 根目錄的 **`start.cmd`**（習慣終端機的人執行 `make dev` 也一樣）。第一次會先安裝前端依賴，約一兩分鐘。伺服器就緒後會**自動用預設瀏覽器開老師頁**，網址列載入後只剩 `http://127.0.0.1:8000/#/teacher`（老師金鑰已移到這個分頁的記憶，重新整理仍可用）。

那個黑色視窗就是伺服器：**關掉它活動就結束、資料清空**（結束前請先匯出）。視窗裡也印著老師頁與學生頁網址，瀏覽器沒自動開時用它：

```
老師頁（只能在本機開啟）：http://127.0.0.1:8000/#/teacher?key=<每次啟動隨機產生>
學生頁：http://127.0.0.1:8000/
```

老師頁網址含老師金鑰，不要給學生。老師頁**只能在本機**（`127.0.0.1`）開；學生頁可以在本機分頁開，或讓手機掃 QR code（第 3 步）。

### 3. 照「開始前的設定」清單完成三項

老師頁最上方有一張「**開始前的設定**」卡，列出三項目前狀態；點任一列會跳到對應區塊。

**(1) Google 帳號**（課程規定 Guided Notes 要直接讀寫雲端 Google 試算表）

第一次會顯示「伺服器未設定 Google OAuth 用戶端」與六步**設定精靈**。每一步都有 Google Cloud Console 的直達連結（新分頁開），找不到頁面時照該步的「找不到時」用 Console 上方搜尋列：

1. **建立專案**：名稱隨意（例：課堂搶答），建立後確認上方專案選單已切到它。
2. **啟用 Google Sheets API**：按「啟用」。
3. **啟用 Google Drive API**：按「啟用」。
4. **設定目標對象與測試使用者**：Google Auth Platform 第一次會要你填應用程式名稱與聯絡信箱；目標對象選「**外部**」、發布狀態保持「**測試中**」，在「測試使用者」加入**你要登入的 Google 帳號**（沒加的帳號登入時會看到「已封鎖存取權」）。
5. **建立用戶端**：類型選「**網頁應用程式**」，「已授權的重新導向 URI」按精靈的「複製」貼上 `http://127.0.0.1:8000/api/google/callback`（JavaScript 來源留空），建立後畫面會顯示用戶端 ID 與密鑰。
6. **貼上用戶端 ID 與密鑰**按「儲存設定」：伺服器寫進 repo 根目錄的 `.env`（不會進版本控制），**立即生效、不用重啟**。格式不對會顯示「用戶端 ID 格式不符…」或「用戶端密鑰格式不符（應以 GOCSPX- 開頭）」。

存好後按「**以 Google 帳號登入**」：瀏覽器開新分頁到 Google，選第 4 步加入的帳號 → 看到「**Google 尚未驗證這個應用程式**」按「**繼續**」（這是測試中的應用程式的正常畫面）→ 權限頁**全部勾選**後按「繼續」→ 新分頁顯示「登入完成，可關閉此分頁」，老師頁變成「已登入：<你的帳號>」。之後可在同一區「變更設定」「清除設定」（已登入時要先登出）。

**(2) 手機連線**（選用：要讓學生用手機掃 QR code 才需要）

在「學生連結」區按「**開啟手機連線**」，約 5 秒後 QR code 換成 `https://….trycloudflare.com/` 公開網址，手機用 4G 也能連；新網址約 **1 分鐘**後才連得上。第一次用會顯示「找不到 cloudflared」與安裝指令 `winget install --id Cloudflare.cloudflared -e`（有「複製指令」鈕），在 PowerShell 裝好後再按一次即可，不用重啟。搶答開始後不能關閉手機連線（以免手機上的組別斷線）；每次重啟伺服器網址都會不同。不開手機連線時，學生頁就在**同一台電腦**的分頁開。

**(3) 匯入題目**

把課程「題組＋單題」範本（或你自己的 Guided Notes）在 Google 試算表「檔案 → 建立副本」到自己的雲端硬碟，複製網址貼到「題目與匯入」區按「**從 Google 試算表匯入**」：系統會在你的雲端硬碟複製一份「**<原標題>_作答情況**」，題目從這份副本讀，原試算表不動。題目清單會列出每題題號與題目敘述（題組顯示每個子題）。沒有 Google 設定時可改「選擇 xlsx 檔 → 上傳 xlsx」（備援）。

### 4. 一場活動

1. **學生加入**：手機掃「學生連結」區的 QR code，或在電腦開學生頁，選組別加入；每組一台裝置（開「組隊」時一組最多 6 台，第二台起憑邀請碼）。準備階段學生只看得到題號。
2. （選用）選**模式**（經典搶答／只計對錯／時間計分）、在題目清單勾**雙倍分數**。
3. 老師按「**開始搶答**」：學生每題輸入欄上方出現題目敘述，各組作答、送出（每題每組一次，題組一次送出全部子題）。老師的「作答狀況與結果」表即時看到每組答案與順位；**學生看不到別組的答案或是否已送出**。
4. 老師按「**結束搶答**」：學生看到每題得主、全部答案與順位、各組得題數。
5. **依順位檢查答對／答錯**（經典搶答）：結束後老師表每題從第 1 順位開始標「檢查中」，答案錯了按「**答錯**」換下一組、對了按「**答對**」鎖定；得主、得分與學生畫面會跟著變，全部答錯該題就沒有得主。沒檢查的題維持最快者得主。按錯了可「重設本題」。
6. 按「**匯出到 Google 試算表**」：每題得主答案寫進「<原標題>_作答情況」副本的填空格（題組寫在每個子題標籤右邊），畫面出現副本連結。另可按「下載 xlsx（備援）」得到「<原檔名>_作答情況.xlsx」。
7. 要再玩一場：在「已結束」按「重置活動」（保留題目與設定、清空作答）。

限制：伺服器重啟即清空活動與 Google 登入（結束後請先匯出）；搶答結束前請勿改動副本的版面（插入列、改分頁名），否則答案可能寫錯格；從 Google 匯入時「下載 xlsx」只含值與合併、不含格式；未開組隊時一組只能一個分頁，分頁關閉後由老師在「組別與裝置」區按「釋放」。

完整操作與驗收步驟見 [`docs/manual-verification.md`](docs/manual-verification.md)；錄 Demo 影片見 [`docs/demo-recording.md`](docs/demo-recording.md)。

### 5. 常見問題

| 狀況 | 怎麼辦 |
|---|---|
| 瀏覽器沒有自動開 | 黑色視窗會印「沒有自動開啟瀏覽器，請手動開上面的老師頁網址」：複製視窗裡的老師頁網址貼到瀏覽器。不想自動開：`make dev` 前設 `QUIZ_NO_BROWSER=1`，或 `python -m quiz_server --no-browser`。 |
| 手機掃 QR code 打不開 | 新通道網址約 1 分鐘後才連得上，稍等再重掃；每次重啟伺服器網址都會換，要重新開手機連線、重掃。 |
| 老師頁顯示「老師金鑰錯誤」 | 關掉分頁或開了新分頁時會這樣（金鑰只存在原分頁）：用黑色視窗印的完整老師頁網址重開，或回首頁重新輸入金鑰。 |
| 老師頁顯示「老師頁只能在本機開啟」 | 用了手機連線的公開網址開老師頁：改用 `http://127.0.0.1:8000` 開。 |
| 「Google 登入已過期，請重新登入」或「請先以 Google 帳號登入」 | 伺服器重啟後要重新登入；到「Google 帳號」區按「以 Google 帳號登入」。 |
| 登入時「已封鎖存取權」 | 這個帳號不在測試使用者名單：回精靈第 4 步把它加入。 |
| 找不到 cloudflared | 照「學生連結」區顯示的指令在 PowerShell 安裝，裝好再按「開啟手機連線」。 |
| 一組的分頁被拒絕加入 | 該組已有裝置：老師在「組別與裝置」區按「釋放」，或開「組隊」。 |

### 附錄：進階／備援——手動設定 `.env`

設定精靈其實就是幫你寫 repo 根目錄的 `.env`。不想用精靈時，可以複製 `.env.example` 成 `.env`，填入：

```
GOOGLE_CLIENT_ID=<用戶端 ID>
GOOGLE_CLIENT_SECRET=<用戶端密鑰>
```

存檔後重新啟動伺服器。`.env` 不會進版本控制；若系統環境變數另設了 `GOOGLE_CLIENT_ID`／`GOOGLE_CLIENT_SECRET`，重新啟動後以系統環境變數為準。開發者也可用 `make dev-tunnel`（`--tunnel`）在啟動時就開手機連線。

## 開發

除了上面兩個工具，另需 GNU make 與 bash（Windows 用 Git Bash；make 可用 `winget install --id GnuWin32.Make -e`，再把 `C:\Program Files (x86)\GnuWin32\bin` 加進 PATH）。轉 PlantUML 圖另需 Java 或 Docker（`make diagrams`）。

```bash
make hooks            # clone 後一次：pre-push 鉤子擋推 main／dev
uv sync --group dev   # 門禁工具依賴
make dev              # 啟動（缺依賴自動安裝）
make test             # 單元測試：server、門禁腳本、前端
make gate-pr          # 開 PR 前的門禁，CI 跑同一套
make help             # 全部指令
```

| 位置 | 內容 |
|---|---|
| `server/quiz_server/` | 後端（FastAPI＋WebSocket）：`activity.py` 活動狀態、`judging.py` 搶答判定、`guided_notes.py` 匯入匯出、`views.py` 依角色裁切資料、`app.py` 路由 |
| `web/src/` | 前端（React＋Vite）：`pages/` 各畫面、`api.ts` 呼叫後端、`live.ts` 即時連線 |
| `contracts/api.md` | API 契約，兩組共用；要改先提規格修訂經負責人批准 |
| `server/tests/`、`web/src/pages/*.test.tsx` | 測試 |
| `specs/`、`diagrams/` | 各子功能規格（spec／plan／tasks／verification）與 PlantUML 圖 |

改程式的流程：從 `origin/dev` 開分支 → 依 [`CLAUDE.md`](CLAUDE.md) 定檔（S／B／C）→ 開 PR 到 `dev`，門禁全綠才合併。詳見 [`docs/workflow.md`](docs/workflow.md)。

## 狀態

| 卡 | 狀態 |
|---|---|
| 專案建置（治理文件、SpecKit 初始化、門禁、CI） | 已完成 |
| 第一～三期子功能 `001-app-skeleton`～`009-team-mode` | 已合入 `dev`，見 `specs/` 各功能 `verification.md` 與 `diagrams/` |
| 功能卡 | 見 [`docs/parity.md`](docs/parity.md) §4 |
