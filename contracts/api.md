# 介面契約：課堂搶答系統（凍結件）

> 首建：卡 `app-skeleton`（2026-11-11）。之後各卡只**增加**端點與欄位，不改既有欄位語意；改語意須經規格變更與負責人批准（`CLAUDE.md`「契約即法律」）。
> 兩組（OpenSpec、SpecKit）實作同一份契約。

## 身分

| 身分 | 憑據 | REST | WebSocket |
|---|---|---|---|
| 老師 | 伺服器啟動時產生的老師金鑰 | 標頭 `X-Teacher-Key` | 查詢參數 `role=teacher&key=<金鑰>` |
| 學生 | `POST /api/student/join` 取得的組別憑證（一組一台裝置） | 標頭 `X-Team-Token` | 查詢參數 `role=student&token=<憑證>` |

伺服器一律由憑證反查組別，不採信客戶端自報的組別名稱。

## 列舉

`phase`：`preparing`（準備中）｜`answering`（搶答中）｜`judging`（判定中，經典模式不使用）｜`ended`（已結束）

`mode`（game-mode-framework）：`classic`（經典搶答，預設）｜`accuracy`（只計對錯；結束搶答後進入 `judging`，老師判定完才揭曉）｜`timed`（時間計分；逐題開放，判定與揭曉在 `answering` 內逐題進行，結束後直接 `ended`；mode-timed-scoring）

## REST 端點

錯誤回應一律為 `{"detail": "<繁體中文訊息>"}`，訊息不含任何學生答案（請求格式錯誤也不回顯請求本體）。

| 方法與路徑 | 身分 | 本體 | 成功回應 | 錯誤 |
|---|---|---|---|---|
| `GET /api/public/info` | 任何人 | — | `{phase, teams: [組名], joined: [已加入組名]}` | — |
| `POST /api/student/join` | 任何人 | `{team}` | `{team, token}` | 404 組別不存在；409 該組已有裝置 |
| `POST /api/student/submit` | 學生（`X-Team-Token`） | `{question, answers: [每個子題一個字串]}` | `{question, answers}`（只回本組這筆，不含順位） | 403 憑證無效；404 題號不存在；409 非 answering 或本組已送出此題，時間計分另有「這一題目前沒有開放作答」「本題作答時間已到」；422 子題數不符、空白、超過 200 字、含控制字元、格式錯誤 |
| `GET /api/teacher/state` | 老師 | — | 老師 view（同 WebSocket） | 401 |
| `POST /api/teacher/teams` | 老師 | `{count}`（2–12） | `{teams}`；撤銷所有組別憑證 | 401；409 非 preparing；422 超出範圍 |
| `POST /api/teacher/release` | 老師 | `{team}` | `{released}`；撤銷該組憑證 | 401；404 |
| `POST /api/teacher/import` | 老師 | `multipart/form-data`，欄位 `file`（.xlsx，≤5 MB） | `{source, count}`；取代題目並清空作答 | 400 檔案或格式不符；401；409 非 preparing |
| `POST /api/teacher/import-url` | 老師 | `{url}`（`https://docs.google.com/spreadsheets/d/<id>/…`，知道連結者可檢視） | `{source, count}` | 400 連結或下載不符；401；409 非 preparing |
| `GET /api/teacher/export` | 老師 | — | xlsx 檔（原 Guided Notes，得主答案寫入作答格、一律為文字）；`Content-Disposition` 含 `filename*=UTF-8''<原檔名>-搶答結果.xlsx` | 401；409 非 ended 或尚未匯入 |
| `POST /api/teacher/start` | 老師 | — | `{phase}` | 401；409 階段不符或尚未匯入題目 |
| `POST /api/teacher/end` | 老師 | — | `{phase}`（判定模式為 `judging`，經典與時間計分為 `ended`） | 401；409 非 answering，或時間計分尚有未揭曉的題目 |
| `POST /api/teacher/question-settings` | 老師 | `{question, multiplier?, time_limit?}`（倍率 1 或 2；時限 5–120 秒；至少一欄，只給一欄時另一欄不動——mode-timed-scoring 語意補充） | `{question, multiplier, time_limit}`；重新匯入清除、重置保留 | 401；404 題號不存在；409 非 preparing；422 值超出範圍或兩欄皆無 |
| `POST /api/teacher/open-next` | 老師 | — | `{question}`：依題號順序開放下一題並開始計時 | 401；409 非 answering、非逐題模式、目前題未揭曉、已無題目 |
| `POST /api/teacher/close-question` | 老師 | — | `{question}`：提早結束目前這一題 | 401；409 沒有進行中的題目 |
| `POST /api/teacher/reveal-question` | 老師 | — | `{question}` | 401；409 本題未關閉或尚有未判定 |
| `POST /api/teacher/mode` | 老師 | `{mode}` | `{mode}` | 401；409 非 preparing；422 未知模式 |
| `POST /api/teacher/judge` | 老師 | `{question, team, correct}` | `{question, team, correct}`；可改判 | 401；404 該組沒有送出此題；409 非 judging |
| `POST /api/teacher/accept-suggestions` | 老師 | — | `{applied}`：只寫入尚未判定且有建議者 | 401；409 非 judging |
| `POST /api/teacher/reveal` | 老師 | — | `{phase: "ended"}` | 401；409 非 judging 或尚有未判定 |
| `POST /api/teacher/reset` | 老師 | — | `{phase}`；清空作答 | 401；409 階段不符 |

## WebSocket `/ws`

- 老師金鑰錯誤 ⇒ 以代碼 `4401` 關閉；`role` 不是 `teacher`／`student` ⇒ `1008` 關閉。
- 連線後立即收到一則完整 view；之後**只在本連線自己的 view 內容改變時**才收到新訊息。
- 訊息：`{"type": "state", "seq": <本連線自己的遞增序號，從 1 起>, "view": <view>}`。不含全域版本號。
- 客戶端送來的文字一律忽略（僅供保持連線）。

### 老師 view

```json
{"role": "teacher", "phase": "preparing", "teams": ["第1組", "第2組"], "joined": ["第1組"],
 "source": "group.xlsx", "questions": [{"number": 1, "labels": ["（1）", "（2）"]}, {"number": 3, "labels": [""]}]}
```

`questions[].labels`：每個子題給學生看的標籤，長度＝子題數；單題為 `[""]`。不含作答格座標（guided-notes-import）。`questions[].multiplier`：該題倍率（1 或 2，老師與學生皆有；question-settings）。`questions[].time_limit`：該題時限秒數（mode-timed-scoring）。

老師與學生 view 皆含 `round`（mode-timed-scoring）：目前回合 `{question, state: "open"|"closed", deadline_epoch_ms}`，沒有則 `null`；`deadline_epoch_ms` 只供倒數顯示，截止以伺服器為準。`mode` 另含 `sequential`（是否逐題開放）。時間計分模式下老師 view 另含 `leaderboard: [{team, rank, score}]`（只計已揭曉題）。

老師 view 另含（game-mode-framework）：`mode: {key, label, judged}`、`modes: [{key, label}]`、`score_label`（經典模式且全部倍率為 1 時「得題數」，其餘「得分」）、`pending_judgments`（未判定筆數）；`board[]` 另含 `reference: [每個子題的參考答案或 null]`，`board[].ranking[]` 另含 `suggestion`（`true`／`false`／`null`）。參考答案與建議**只在老師 view**。

老師 view 另含（results-view）：`board`（格式同學生 view 的 `results`，任何階段即時更新）與 `team_scores`（`{組名: 分數}`；欄名見 `score_label`，經典模式且全部倍率為 1 時等於得題數——question-settings 語意補充）。

### 學生 view

```json
{"role": "student", "phase": "preparing", "team": "第1組", "team_valid": true,
 "questions": [{"number": 1, "labels": ["（1）", "（2）"]}, {"number": 3, "labels": [""]}]}
```

所有階段都含 `mode: {key, label, sequential}`、`score_label`、`round` 與 `my_submissions`（只有本組：`[{question, answers}]`，不含順位、序號、他組是否送出）。`judging` 與 `answering` 相同，不含判定結果。時間計分模式在 `ended` 前另含 `revealed: [{question, submitted, correct, score}]`（只有本組、只列已揭曉題）、`my_total`（本組累積）與 `leaderboard: [{team, rank}]`（依已揭曉題累積分數的名次，同分同名次；**不含他組分數**——分數可反推作答秒數）。只有 `ended` 階段另含 `results`：

```json
{"results": [{"number": 3, "labels": [""], "winner": {"team": "第2組", "answers": ["位址"]},
              "ranking": [{"team": "第2組", "answers": ["位址"], "rank": 1, "is_winner": true, "score": 1},
                          {"team": "第1組", "answers": ["地址"], "rank": 2, "is_winner": false, "score": 0}]}]}
```

順位依伺服器接收序；經典規則得主得 1 × 該題倍率分（buzz-answering D2；question-settings 語意補充）。`results[]` 另含 `multiplier`。`ranking[]` 另含 `correct`（經典為 `null`；只計對錯為老師判定），只計對錯的得主＝最早送出的正確答案，正確者各得 1 × 倍率分（game-mode-framework、question-settings）。`ended` 另含 `team_scores`。老師的 `board` 與學生的 `results` 由同一函式產生，內容一致（results-view D1）。

憑證缺、錯或已撤銷：

```json
{"role": "student", "phase": "preparing", "team": null, "team_valid": false}
```
