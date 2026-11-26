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
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md)、[`specs/`](specs/)、[`diagrams/`](diagrams/) | 憲章、各子功能規格、PlantUML 圖表（評分檢驗 constitution／spec／plan／tasks／圖表） |

## 開始使用（老師／Demo）

**三步開始**（easy-setup）：

1. 在檔案總管雙擊根目錄的 **`start.cmd`**（習慣終端機的人執行 `make dev` 也一樣）。缺 uv 或 Node.js 時會問「要幫你用 winget 安裝嗎？(Y/N)」，輸入 Y 就自動裝（可能跳出「是否允許變更」視窗，按「是」）；只認 Y／y，直接按 Enter 視為不裝。Python 不用另外裝，uv 會自動下載。第一次啟動會先安裝依賴，約需一兩分鐘。
2. 伺服器就緒後會**自動用預設瀏覽器開老師頁**（不想自動開：`make dev` 加 `QUIZ_NO_BROWSER=1`，或 `python -m quiz_server --no-browser`）。
3. 照老師頁最上方「**開始前的設定**」清單完成：Google 帳號（第一次會出現設定精靈）、手機連線（選用）、匯入題目。點清單的任一列會跳到對應區塊。

想自己裝工具也可以：`winget install --id astral-sh.uv -e`、`winget install --id OpenJS.NodeJS.LTS -e`。視窗仍會印出兩個網址當備援（瀏覽器沒自動開時用）：

```
老師頁：http://127.0.0.1:8000/#/teacher?key=<每次啟動隨機產生>
學生頁：http://127.0.0.1:8000/
```

老師頁網址含老師金鑰，不要給學生。開啟老師頁後網址列只剩 `#/teacher`（金鑰已移到本分頁記憶，重新整理仍可用）；關掉分頁後要再開，請重新貼終端機印的完整網址。關閉視窗（或按 Ctrl+C）就停止伺服器，活動隨之清空。

**讓手機掃 QR code 進學生頁**（選用）：在老師頁「學生連結」區按「**開啟手機連線**」，伺服器會即時建立 Cloudflare 快速通道，QR code 換成 `https://….trycloudflare.com/` 的公開網址（約 5 秒）；不用了按「關閉手機連線」（搶答開始後不能關，以免手機上的組別斷線）。第一次用要先安裝 cloudflared：找不到時老師頁會顯示安裝指令 `winget install --id Cloudflare.cloudflared -e` 與複製鈕，裝好再按一次即可，不用重新啟動。開發者也可以用 `make dev-tunnel`（`--tunnel`）在啟動時就開。手機用 4G 也能連，不必與電腦同一個 Wi-Fi。新網址約 1 分鐘後才連得上，每次啟動都不同。老師頁**只能在本機**（`127.0.0.1`）開啟，用公開網址開會顯示「老師頁只能在本機開啟，請用 http://127.0.0.1:8000 開老師頁」。找不到 cloudflared 時照常以本機模式啟動。

### 一場活動

1. 老師開老師頁網址。學生頁在**同一台電腦**開，**每組一個分頁**：組別憑證存在分頁裡，關閉分頁即失效。系統只在本機執行，別台電腦連不到。
2. 老師在老師頁按「以 Google 帳號登入」（第一次使用先完成老師頁的 Google 設定精靈，見下方「Google 試算表設定」），貼上試算表連結按「從 Google 試算表匯入」：系統會在老師的雲端硬碟複製一份「<原標題>_作答情況」，題目從這份副本讀取，原試算表不動。沒有 Google 設定時可改上傳 xlsx（備援）。
3. 老師按「開始搶答」；各組作答、送出（每題每組一次，題組一次送出全部子題）；最先送出的組別得該題。
4. 老師按「結束搶答」後，學生看到結果；老師按「匯出到 Google 試算表」，答案直接寫進那份副本的填空格，畫面會出現副本連結。另可按「下載 xlsx（備援）」。

限制：伺服器重啟即清空活動與 Google 登入（結束後請先匯出）；搶答結束前請勿改動副本的版面（插入列、改分頁名），否則答案可能寫錯格；從 Google 匯入時「下載 xlsx」只含值與合併、不含格式；匯出只保證儲存格內容與合併範圍不變，圖片、資料驗證等 openpyxl 不完整支援的元素可能遺失；未開組隊時一組只能一個分頁，分頁關閉後由老師在組別區按「釋放」；開組隊時一組最多 6 個分頁，第二個起憑該組邀請碼加入。

完整操作與驗收步驟見 [`docs/manual-verification.md`](docs/manual-verification.md)。

### Google 試算表設定（第一次使用做一次）

課程規定 Guided Notes 須直接串接雲端 Google Sheets 讀寫，所以老師要用 Google 帳號登入。**老師頁「Google 帳號」區在未設定時會展開設定精靈**：每一步都有 Google Cloud Console 的直達連結、重新導向 URI 有複製鈕，最後貼上用戶端 ID 與密鑰按「儲存設定」，伺服器會寫進 repo 根目錄的 `.env`（不會進版本控制）並**立即生效，不用重新啟動**；之後可在同一區「變更設定」或「清除設定」（已登入時要先登出）。精靈的步驟與下面相同：

1. 到 [Google Cloud Console](https://console.cloud.google.com/) 建立專案，啟用 **Google Sheets API** 與 **Google Drive API**。
2. 「Google Auth Platform」：目標對象選「外部」、發布狀態保持「測試中」，把要登入的 Google 帳號加到「測試使用者」（沒加的帳號會看到「已封鎖存取權」）。
3. 「用戶端 → 建立用戶端」：類型「網頁應用程式」，已授權的重新導向 URI 填 `http://127.0.0.1:8000/api/google/callback`（JavaScript 來源留空）。
4. 在老師頁精靈貼上用戶端 ID 與密鑰按「儲存設定」。也可以手動寫進 repo 根目錄的 `.env`（格式見 `.env.example`）後重新啟動；若你在系統環境變數另設了 `GOOGLE_CLIENT_ID`／`GOOGLE_CLIENT_SECRET`，重新啟動後以系統環境變數為準。
5. 登入時若看到「Google 尚未驗證這個應用程式」，按「繼續」。

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
