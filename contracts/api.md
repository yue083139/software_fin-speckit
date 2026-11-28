# 介面契約：課堂搶答系統（凍結件）

> 首建：卡 `app-skeleton`（2026-11-11）。之後各卡只**增加**端點與欄位，不改既有欄位語意；改語意須經規格變更與負責人批准（`CLAUDE.md`「契約即法律」）。
> 兩組（OpenSpec、SpecKit）實作同一份契約。

## 身分

| 身分 | 憑據 | REST | WebSocket |
|---|---|---|---|
| 老師 | 伺服器啟動時產生的老師金鑰 | 標頭 `X-Teacher-Key` | 查詢參數 `role=teacher&key=<金鑰>` |
| 學生 | `POST /api/student/join` 取得的組別憑證（一組一台裝置；組隊時一組最多 6 台，第二台起憑邀請碼加入——team-mode 語意補充） | 標頭 `X-Team-Token` | 查詢參數 `role=student&token=<憑證>` |

伺服器一律由憑證反查組別，不採信客戶端自報的組別名稱。

**老師身分只在本機**（student-qr，負責人 2026-11-26 批准）：老師 REST 端點、`role=teacher` 的 WebSocket 與 `GET /api/google/callback` 只接受 Host 主機名為 `127.0.0.1`、`localhost`、`[::1]` 且不帶 `cf-connecting-ip`／`cf-ray` 標頭的請求；否則在驗金鑰前回 403 `{"detail": "老師頁只能在本機開啟"}`（WebSocket 以代碼 `4403` 關閉；回呼為固定 HTML）。學生與公開端點不受限。

## 列舉

`phase`：`preparing`（準備中）｜`answering`（搶答中）｜`judging`（判定中，經典模式不使用）｜`ended`（已結束）

`mode`（game-mode-framework）：`classic`（經典搶答，預設）｜`accuracy`（只計對錯；結束搶答後進入 `judging`，老師判定完才揭曉）｜`timed`（時間計分；逐題開放，判定與揭曉在 `answering` 內逐題進行，結束後直接 `ended`；mode-timed-scoring）

## REST 端點

錯誤回應一律為 `{"detail": "<繁體中文訊息>"}`，訊息不含任何學生答案（請求格式錯誤也不回顯請求本體）。

| 方法與路徑 | 身分 | 本體 | 成功回應 | 錯誤 |
|---|---|---|---|---|
| `GET /api/public/info` | 任何人 | — | `{phase, teams: [組名], joined: [已加入組名], team_play}`（不含台數與邀請碼；team-mode） | — |
| `POST /api/student/join` | 任何人 | `{team, code?}`（組隊時：該組已有邀請碼就必須帶，不分大小寫與全半形、忽略空白） | `{team, token}` | 403 邀請碼不正確（組隊）；404 組別不存在；409 該組已有裝置（非組隊）或此組裝置已滿（組隊，最多 6 台；先比對邀請碼再檢查上限）——team-mode 語意補充 |
| `POST /api/student/draft` | 學生（`X-Team-Token`） | `{question, answers: [每個子題一個字串，可空白]}` | `{question}`（不回顯內容） | 403 憑證無效；404 題號不存在；409 非組隊（「只有組隊模式可以共用草稿」）、非 answering、本組已送出此題、時間計分非開放中題；422 子題數不符、超過 200 字、含控制字元、格式錯誤（team-mode） |
| `POST /api/student/submit` | 學生（`X-Team-Token`） | `{question, answers: [每個子題一個字串]}` | `{question, answers}`（只回本組這筆，不含順位） | 403 憑證無效；404 題號不存在；409 非 answering 或本組已送出此題，時間計分另有「這一題目前沒有開放作答」「本題作答時間已到」；422 子題數不符、空白、超過 200 字、含控制字元、格式錯誤 |
| `GET /api/teacher/state` | 老師 | — | 老師 view（同 WebSocket） | 401 |
| `POST /api/teacher/teams` | 老師 | `{count}`（2–50） | `{teams}`；撤銷所有組別憑證，組隊時另清除邀請碼與草稿 | 401；409 非 preparing；422 超出範圍 |
| `POST /api/teacher/release` | 老師 | `{team}` | `{released}`；撤銷該組憑證（組隊時撤銷該組全部裝置、清草稿，並換新邀請碼——新碼只在老師 view；team-mode 語意補充） | 401；404 |
| `POST /api/teacher/team-play` | 老師 | `{enabled}` | `{team_play}`；值改變時撤銷所有組別憑證、邀請碼與草稿，值不變不動；重置保留（team-mode） | 401；409 非 preparing；422 格式錯誤 |
| `POST /api/teacher/import` | 老師 | `multipart/form-data`，欄位 `file`（.xlsx，≤5 MB） | `{source, count}`；取代題目並清空作答 | 400 檔案或格式不符；401；409 非 preparing |
| `POST /api/teacher/import-url` | 老師 | `{url}`（`https://docs.google.com/spreadsheets/d/<id>/…`；須已以 Google 帳號登入） | `{source, count, sheet_url}`：先以 Drive 複製一份「<原標題>_作答情況」（answer-review 改名），再以 Sheets API 讀取並解析**副本**；`sheet_url` 為副本連結（guided-notes-sheets-sync 語意改變，負責人 2026-11-17 批准） | 依序：401 老師金鑰；409 非 preparing；400 連結不符、分頁不存在（不建立副本）或解析錯誤；401「請先以 Google 帳號登入」「Google 登入已過期，請重新登入」；502 Google 錯誤。登入檢查前不發任何對外請求；副本建立後任何失敗都盡力刪除副本 |
| `POST /api/teacher/export-sheet` | 老師 | — | `{url}`：把得主答案以 `RAW` 寫入匯入時建立的副本（分頁名中的 `'` 以 `''` 跳脫），原試算表不動（guided-notes-sheets-sync）；寫入範圍＝目前有得主的作答格＋上次寫回寫過、這次已無得主的作答格（以匯入時原內容還原），無得主且從未寫過的格不碰；與下載 xlsx 以同一把伺服器鎖序列化（answer-review） | 依序：401 老師金鑰；409「搶答結束後才能匯出」「尚未匯入題目」「題目不是從 Google 試算表匯入，請改用下載 xlsx」；401 Google 未登入／已過期；502 Google 錯誤 |
| `GET /api/teacher/google` | 老師 | — | `{configured, signed_in, email, client_id_hint, redirect_uri}`（不含任何權杖與用戶端密鑰；guided-notes-sheets-sync；easy-setup 增 `client_id_hint`＝遮罩後的用戶端 ID 前 6 碼＋「…」＋`apps.googleusercontent.com`、未設定為 `null`，`redirect_uri` 固定 `http://127.0.0.1:8000/api/google/callback`——負責人 2026-11-26 批准） | 401 |
| `POST /api/teacher/google/config` | 老師 | `{client_id, client_secret}`（不去空白，以 fullmatch 比對：ID `[0-9]{4,30}-[a-z0-9]{8,64}\.apps\.googleusercontent\.com`、密鑰 `GOCSPX-[A-Za-z0-9_-]{20,64}`，各 ≤128 字） | 同 `GET /api/teacher/google`：只改寫 repo 根目錄 `.env` 的 `GOOGLE_CLIENT_ID`、`GOOGLE_CLIENT_SECRET`（同鍵多行只留第一行、其他行保留、原子寫入）並立即生效，不需重啟；作廢進行中的登入（easy-setup） | 依序：403 非本機；401；422「用戶端 ID 格式不符（應以 .apps.googleusercontent.com 結尾）」「用戶端密鑰格式不符（應以 GOCSPX- 開頭）」（不回顯輸入）；409「請先登出 Google 再變更設定」 |
| `DELETE /api/teacher/google/config` | 老師 | — | 同上狀態（`configured: false`）；自 `.env` 移除兩鍵、其他行保留（easy-setup） | 依序：403；401；409「請先登出 Google 再變更設定」 |
| `POST /api/teacher/tunnel` | 老師 | — | `{tunnel: "on", student_url}`：伺服器即時起 cloudflared 快速通道（已開啟則直接回現值）；建立中被關閉則回 `{tunnel: "off", student_url: null}`；不限階段（easy-setup） | 依序：403；401；409「手機連線建立中」；503「找不到 cloudflared，請先安裝：winget install --id Cloudflare.cloudflared -e」；504「建立手機連線逾時，請再試一次」 |
| `DELETE /api/teacher/tunnel` | 老師 | — | `{tunnel: "off", student_url: null}`：停止通道（已關閉則直接回；建立中則等建立完成後停止）（easy-setup） | 依序：403；401；409「搶答進行中不能關閉手機連線」（非準備階段） |
| `POST /api/teacher/google/login` | 老師 | — | `{url}`（Google 授權網址：授權碼＋PKCE S256、`access_type=offline`、`prompt=consent`、scope `openid email spreadsheets drive`）；設 cookie `qz_gstate`＝`sha256(state)`（`HttpOnly`、`SameSite=Lax`、`Path=/api/google`、10 分鐘） | 401；400「伺服器未設定 Google OAuth 用戶端」 |
| `GET /api/google/callback?code&state` | 任何人（以 `state`＋cookie 綁定發起登入的老師瀏覽器） | — | HTML「登入完成，可關閉此分頁」；清 cookie | 400 HTML「登入失敗，請回老師頁重新登入」：`state` 非伺服器發出、過期、已用過、cookie 不符或帶 `error`；回應不回顯任何查詢參數 |
| `POST /api/teacher/google/logout` | 老師 | — | `{signed_in: false}`；以表單本體向 Google 撤銷權杖（失敗也清空本機） | 401 |
| `GET /api/teacher/export` | 老師 | — | xlsx 檔（原 Guided Notes，得主答案寫入作答格、一律為文字；題目來自 Google 試算表時為副本的值與合併、不含格式，作下載備援；xlsx 不允許的分頁名稱字元 `\ / : * ? [ ]` 換成「_」——guided-notes-sheets-sync）；`Content-Disposition` 含 `filename*=UTF-8''<原檔名>_作答情況.xlsx`（answer-review 改名） | 401；409 非 ended 或尚未匯入 |
| `POST /api/teacher/start` | 老師 | — | `{phase}` | 401；409 階段不符或尚未匯入題目 |
| `POST /api/teacher/end` | 老師 | — | `{phase}`（判定模式為 `judging`，經典與時間計分為 `ended`） | 401；409 非 answering，或時間計分尚有未揭曉的題目 |
| `POST /api/teacher/question-settings` | 老師 | `{question, multiplier?, time_limit?}`（倍率 1 或 2；時限 5–120 秒；至少一欄，只給一欄時另一欄不動——mode-timed-scoring 語意補充） | `{question, multiplier, time_limit}`；重新匯入清除、重置保留 | 401；404 題號不存在；409 非 preparing；422 值超出範圍或兩欄皆無 |
| `POST /api/teacher/open-next` | 老師 | — | `{question}`：依題號順序開放下一題並開始計時 | 401；409 非 answering、非逐題模式、目前題未揭曉、已無題目 |
| `POST /api/teacher/close-question` | 老師 | — | `{question}`：提早結束目前這一題 | 401；409 沒有進行中的題目 |
| `POST /api/teacher/reveal-question` | 老師 | — | `{question}` | 401；409 本題未關閉或尚有未判定 |
| `POST /api/teacher/mode` | 老師 | `{mode}` | `{mode}` | 401；409 非 preparing；422 未知模式 |
| `POST /api/teacher/judge` | 老師 | `{question, team, correct}` | `{question, team, correct}`；可改判 | 401；404 該組沒有送出此題；409 非 judging——時間計分改為：非 answering，或該題未關閉／已揭曉（mode-timed-scoring 語意補充） |
| `POST /api/teacher/accept-suggestions` | 老師 | — | `{applied}`：只寫入尚未判定且有建議者；時間計分只處理目前已關閉的那一題 | 401；409 非 judging——時間計分改為：沒有已關閉、未揭曉的題目（mode-timed-scoring 語意補充） |
| `POST /api/teacher/reveal` | 老師 | — | `{phase: "ended"}` | 401；409 非 judging 或尚有未判定 |
| `POST /api/teacher/review` | 老師 | `{question, team, correct}`（`team` 須為該題目前候選） | `{question, team, correct}`（不含答案）；狀態改變並推播（answer-review） | 依序：401；422 格式錯誤；409「只有經典搶答可以檢查」「搶答結束後才能檢查」；404 題號不存在；409「本題已鎖定，請先重設本題」「本題沒有可檢查的答案」「這一組不是目前要檢查的答案，請重新整理」 |
| `POST /api/teacher/review-reset` | 老師 | `{question}` | `{question}`：清除該題檢查結果，回到順位 1 未檢查；推播（answer-review） | 依序：401；422；409 模式、階段；404；409「本題尚未檢查」 |
| `POST /api/teacher/reset` | 老師 | — | `{phase}`；清空作答 | 401；409 階段不符 |

## WebSocket `/ws`

- 老師金鑰錯誤 ⇒ 先完成交握、不送任何訊息，再以代碼 `4401` 關閉（teacher-key-error：交握前就拒絕時瀏覽器只拿得到 `1006`，無法顯示金鑰錯誤；`4403` 同此做法）；`role=teacher` 但 Host 不是本機或帶 Cloudflare 轉送標頭 ⇒ 先於金鑰檢查以 `4403` 關閉（student-qr）；`role` 不是 `teacher`／`student` ⇒ `1008` 關閉。
- 連線後立即收到一則完整 view；之後**只在本連線自己的 view 內容改變時**才收到新訊息。
- 訊息：`{"type": "state", "seq": <本連線自己的遞增序號，從 1 起>, "view": <view>}`。不含全域版本號。
- 客戶端送來的文字一律忽略（僅供保持連線）。

### 老師 view

```json
{"role": "teacher", "phase": "preparing", "teams": ["第1組", "第2組"], "joined": ["第1組"],
 "source": "group.xlsx", "questions": [{"number": 1, "labels": ["（1）", "（2）"]}, {"number": 3, "labels": [""]}]}
```

`questions[].labels`：每個子題給學生看的標籤，長度＝子題數；單題為 `[""]`。不含作答格座標（guided-notes-import）。`questions[].multiplier`：該題倍率（1 或 2，老師與學生皆有；question-settings）。`questions[].time_limit`：該題時限秒數（mode-timed-scoring）。`questions[].prompts`：每個子題的題目敘述（取自 Guided Notes 題目欄，無題目欄為 `""`），長度與順序同 `labels`；老師 view 任何階段都有（question-text，負責人 2026-11-26 批准）。

老師與學生 view 皆含 `round`（mode-timed-scoring）：目前回合 `{question, state: "open"|"closed", deadline_epoch_ms}`，沒有則 `null`；`deadline_epoch_ms` 只供倒數顯示，截止以伺服器為準。`mode` 另含 `sequential`（是否逐題開放）。時間計分模式下老師 view 另含 `leaderboard: [{team, rank, score}]`（只計已揭曉題）。

老師 view 另含（game-mode-framework）：`mode: {key, label, judged}`、`modes: [{key, label}]`、`score_label`（經典模式且全部倍率為 1 時「得題數」，其餘「得分」）、`pending_judgments`（未判定筆數）；`board[]` 另含 `reference: [每個子題的參考答案或 null]`，`board[].ranking[]` 另含 `suggestion`（`true`／`false`／`null`）。參考答案與建議**只在老師 view**。

老師 view 另含（student-qr）：`student_url`——以 `--tunnel` 啟動或老師頁開啟手機連線（easy-setup）且通道建立成功時為學生公開網址（`https://<隨機>.trycloudflare.com/`），否則 `null`（前端改用自身網址）；學生 view 不含。

老師 view 另含（easy-setup）：`tunnel`——手機連線狀態 `"off"`｜`"starting"`｜`"on"`，變化時推播；cloudflared 子行程意外結束自動轉 `"off"` 並清 `student_url`。學生 view 不含 `tunnel`。

老師 view 另含（team-mode）：`team_play`、`devices: {組名: 已發出的憑證數}`、`invite_codes: {組名: 邀請碼}`（只列有邀請碼的組，含被釋放後待重新加入者）。老師 view 不含組內草稿。開始搶答時所有邀請碼換新。

老師 view 另含（results-view）：`board`（格式同學生 view 的 `results`，任何階段即時更新）與 `team_scores`（`{組名: 分數}`；欄名見 `score_label`，經典模式且全部倍率為 1 時等於得題數——question-settings 語意補充）。

老師 view 另含（answer-review）：經典模式下 `board[]` 每題另含 `review: {candidate, rejected, locked}`——`candidate` 為目前候選組名（＝`winner.team`；全部判錯或無送出為 `null`），`rejected` 為依順位已被判錯的組名清單，`locked` 為候選是否已判對鎖定。其他模式不帶此鍵；學生 `results` 永不帶。

### 學生 view

```json
{"role": "student", "phase": "preparing", "team": "第1組", "team_valid": true,
 "questions": [{"number": 1, "labels": ["（1）", "（2）"]}, {"number": 3, "labels": [""]}]}
```

`questions[].prompts` 只在搶答開始後才帶：`preparing` 每題都不帶此鍵；`answering`／`judging` 非逐題模式每題都帶、逐題模式只有已開放過的題帶；`ended` 每題都帶（question-text）。所有階段都含 `mode: {key, label, sequential}`、`score_label`、`round` 與 `my_submissions`（只有本組：`[{question, answers}]`，不含順位、序號、他組是否送出）。`judging` 與 `answering` 相同，不含判定結果。另含 `team_play`；組隊時 `preparing` 另含 `invite_code`（本組邀請碼），`answering` 另含 `drafts: [{question, answers}]`（只有本組、最後寫入者為準，送出即清除）；其餘階段兩者皆不帶（team-mode）。時間計分模式在 `ended` 前另含 `revealed: [{question, submitted, correct, score}]`（只有本組、只列已揭曉題）、`my_total`（本組累積）與 `leaderboard: [{team, rank}]`（依已揭曉題累積分數的名次，同分同名次；**不含他組分數**——分數可反推作答秒數）。只有 `ended` 階段另含 `results`：

```json
{"results": [{"number": 3, "labels": [""], "winner": {"team": "第2組", "answers": ["位址"]},
              "ranking": [{"team": "第2組", "answers": ["位址"], "rank": 1, "is_winner": true, "score": 1},
                          {"team": "第1組", "answers": ["地址"], "rank": 2, "is_winner": false, "score": 0}]}]}
```

順位依伺服器接收序；經典規則得主得 1 × 該題倍率分（buzz-answering D2；question-settings 語意補充）。經典搶答的得主＝依順位第一個未被老師判錯者：未檢查即順位 1；結束後判錯依順位遞補、判對鎖定；全部判錯則 `winner` 為 `null`、全部 0 分（answer-review，負責人 2026-11-26 批准）。`results[]` 另含 `multiplier`。`ranking[]` 另含 `correct`（經典：未檢查為 `null`，結束後老師檢查為 `true`／`false`——answer-review；只計對錯為老師判定），只計對錯的得主＝最早送出的正確答案，正確者各得 1 × 倍率分（game-mode-framework、question-settings）。`ended` 另含 `team_scores`。老師的 `board` 與學生的 `results` 由同一函式產生，內容一致（results-view D1）。

憑證缺、錯或已撤銷：

```json
{"role": "student", "phase": "preparing", "team": null, "team_valid": false}
```
