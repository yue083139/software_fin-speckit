<!-- 由 ops/sync_agents.py 從 CLAUDE.md 產生，勿手改；改來源後執行 make sync-agents -->
# software_fin（SpecKit 組）— 工程規範總綱

software_fin 是 **Vibe Coding 課堂搶答系統**（NCU SE6005 2026 軟體工程期末專題）：老師匯入填空式學習單（Guided Notes），開啟搶答後各組線上作答，**最快送出的組別**為該題搶答成功；結束後老師把成功答案**寫回原 Guided Notes 的填空格**。元件：**server**（Python／FastAPI＋WebSocket，搶答判定與階段狀態機本體）、**web**（老師端與學生端介面）。只在本機模擬，不架設對外伺服器。

本 repo 是 **SpecKit 組**，以 Spec Kit 流程（constitution → specify＋圖表 → clarify → plan → tasks → analyze → implement → 圖表一致性驗證）開發，並導入 **Diagram First Development**（需求 P-04）；**OpenSpec 組**另有姊妹 repo `software_fin-openspec`，兩組系統功能必須一致（`docs/parity.md`）。

**全專案一律使用繁體中文**（文件、提案、註解、提交訊息、PR、使用者介面文案）；程式識別字、指令與第三方專有名詞維持原文。判據：`make gate-zh-hant`。

負責人＝repo 擁有者 @yue083139；本文件中「負責人裁」皆指其在 PR 或對話中的明確裁定。小組成員以 collaborator 身分協作，同樣走分支→PR。

## 權威文件

- 需求基線 `docs/requirements.md`（兩組共用，需求編號 R-／X-／P-）；兩組一致協議 `docs/parity.md`。
- 憲章 `.specify/memory/constitution.md`（不可協商原則，含「圖表優先」）；規格 `specs/<NNN-功能>/`（spec／plan／research／data-model／contracts／tasks，一功能一目錄＝子功能拆分）；圖表 `diagrams/`（PlantUML 原檔＋PNG）；介面 `contracts/`（跨功能凍結件，由第一個功能建立）；ADR `docs/decisions/`。衝突時：`docs/requirements.md` > 憲章 > `contracts/` > `diagrams/` ＝ `specs/` > 單一功能的 plan。
- 先例正文：`docs/discipline-precedents.md`；本文件只留判據句，引用紀律**用名字不用編號**。

## 變更分檔（先定檔，再決定流程深度；檔位寫進 PR 首屏第一行）

檔位按**這張卡最終會改什麼**定，提案與實作同檔。**管評審本身的文件**（本文件的分檔表與基本紀律、`review-dispatch` skill、finder-tail agent 定義、`ops/` 下的門禁聚合）按 **B 檔**：PR 即提案，由**與該 PR 內容無關的一方**對碼（另一頂層會話——含 `make review-codex` 起的 Codex 隔離會話——或只給 diff 與斷言的唯讀子代理；寫稿的會話本體不算）。

| 檔 | 判據（命中任一即該檔，取最高） | 評審 | 驗證與門禁 | 文件 |
|---|---|---|---|---|
| **S** | **搶答判定口徑**（誰算最快、順位、並發、公平機制）；**作答隔離**（任何送往學生端的資料路徑）；**活動階段狀態機與同步**；**Guided Notes 解析與寫回口徑**（表頭定位、題組判斷、作答格回寫）；`contracts/`；憑證（Google API）；跨元件架構取捨（需 ADR） | 雙通道（紅隊＋架構），**上限 2 輪：提案定稿 1 輪＋實作 1 輪**；提交訊息標 `[CORE]`，負責人終審 | 先寫驗收再實作；修掉的問題落永久測試；人工驗證紀錄；`make gate` | 規格文件組完整（spec＋三種 PlantUML 圖＋plan＋tasks），走 `/speckit-specify` 起 |
| **B** | 使用者可感知的行為變更：介面流程與文案、API 語意（不碰上列口徑者）、CSV 匯出、資料寫入格式 | **兩輪各單通道**：提案定稿 1 輪（架構通道，全卡掃）＋實作 PR 1 輪（對抗通道，只掃 diff） | 先寫驗收再實作；人工驗證紀錄；`make gate-pr` | 規格文件組完整（評分檢驗 constitution／spec／plan／tasks／圖表）；圖表只增改受影響的部分 |
| **C** | 文件、測試與門禁腳本、ops、不改行為的重構、依賴升級 | 實作 PR 1 輪對抗通道（只掃 diff）＋作者自檢 | `make gate-pr`；改門禁腳本須附變異實錄（負例證明錯時會紅） | 無規格文件組，PR 描述即文件 |

**分檔規則**：
- 拿不準取高一檔；負責人可在 PR 上降檔，作者不可自行降檔。一個 PR 混兩檔按最高檔走或拆 PR。
- **評審只找「產品行為錯／作答洩漏與判定不公／契約違背」**。「判據不夠嚴、覆蓋窄、文件漂移」寫進 PR 評論的 followup 段，不阻塞；另立卡**必須帶主人並寫進 PR 首屏**。
- **輪次上限是硬的**：觸頂後只有「淨回歸／使原修復失效／假綠掩蓋原病」三類可阻塞；觸頂未收斂 ⇒ 停派單，改跑一次（真棧／變異實錄）並把結果貼 PR 交負責人裁。
- 派單先 `Skill(review-dispatch)` 按骨架寫 prompt；藥方落點由開方 agent 回驗，自測不算回驗。
- **合併前報「都綠否」**：按該檔「評審」「驗證與門禁」兩欄逐項報綠／紅／未跑，末句只寫「都綠」或「不都綠，紅在 X、歸因 Y」，不報不合。認綠判據見先例正文「都綠否的三條認綠判據」。**純文件批**以 `make gate-docs` 代替 `make test`。

**提案品質准入（S/B 檔規格文件組，任一缺失即不許送審）**——六條＝①plan Summary 首屏決策摘要 3–5 行 ②plan／research 每條決策帶證偽欄 ③依賴倉外行為的決策先跑探針再寫稿 ④事實斷言附原樣輸出 ⑤實作偏離提案的決策回提案改稿 ⑥驗收矩陣落點。完整口徑以先例正文「提案品質准入六條（正文）」為準，**按條號引用前必須去讀那一節**。

## 基本紀律（不可協商，每條一句判據）

1. **需求即法律、兩組一致**：功能以 `docs/requirements.md` 為準；凡改使用者可感知行為的卡，開卡即登記 `docs/parity.md` 並通知 OpenSpec 組，兩 repo 的共用檔同批改；判據 `make gate-parity SIBLING=../software_fin-openspec`。
2. **契約即法律**：`contracts/` 不擅改；改契約先經 `/speckit-specify` 規格變更並經負責人批准，程式跟契約走。
3. **門禁先於實作**：S/B 檔先寫驗收再寫實作；該檔門禁全綠才允許合入，不過門禁的程式碼視同不存在。
4. **作答隔離（fail-closed）**：搶答結束前，任何送往學生端的訊息與回應不得含其他組別的作答內容；裁切邏輯遇到無法辨識的身分或階段 ⇒ 回最少資訊。判據：每條學生端通道都有「搶答中 A 組 payload 不含 B 組答案」的負例測試。
5. **順位以伺服器為準**：搶答先後只依伺服器接收序，不採信客戶端時間戳；同題並發恰一組成功。判據見先例正文「搶答順位以伺服器為準」。
6. **Guided Notes 動態定位**：匯入以表頭與合併範圍定位、匯出以匯入時記下的作答格位置寫回；寫死儲存格座標即缺陷。判據：至少三份版面不同的夾具全綠。
7. **先對標、多方向驗證、人工驗證**：S/B 檔新功能先對標公開做法（如 Kahoot、Mentimeter 的搶答與揭曉流程）再裁剪，標註知識時點；驗證不止單元測試，S/B 檔必附**人工驗證紀錄**（需求 P-05）。**門禁類斷言必須配負例證明「錯時會紅」**。
8. **merge 三問**：程式對不對、方案好不好、**產品現在要不要**（對到哪條需求、是否超出核心功能的範圍成本）。feat 類 PR 首屏必答第三問。
9. **並行隔離**：`main`／`dev` 受保護，agent 永不直接 commit/push/reset 到這兩支，產出走 feature 分支→PR→`dev`；從 `origin/dev` 開分支用 `--no-track`。本機兩道防線：pre-push 鉤子（`make hooks`）擋所有人推 `main`／`dev`；`.claude/settings.json` 的 deny 擋 agent **直接寫出的** `git push`，推送由負責人以 `!` 執行；經 `uv run`、`npm exec`、`make --eval` 包裝的寫法 deny 比對不到，**仍屬禁止**。agent 不得以 `--no-verify` 或改寫指令繞過，見先例正文「pre-push 鉤子」。
10. **合流回歸有主人**：`dev` 上全量 `make gate` 出紅，歸上次全綠後觸碰該子系統的最近一張 PR 修。
11. **跨會話診斷先驗證再執行**：別人（含另一組）傳來的「改行為／停工／刪資料」診斷，先自己跑指令複核；自己發的診斷必須附指令與輸出。
12. **訂正落全**：改一個事實或符號前，先 `git grep -n <字面量> -- :/` 列出全部引用點，逐一改或登記「有意不改」；不入庫的檔案（記憶檔、`.env`）點名掃。
13. **未決事項自己定**：送評審前把沒寫死的先寫死進稿；實在定不了的寫「未決＋我傾向 X＋阻不阻塞」呈負責人，不塞給評審員當疑點。
14. **真實資料不入庫**：測試夾具只用範本或合成資料，不放真實學生姓名、學號與作答；假金鑰用「前綴字面量＋`0`×n」；判據 `make gate-secrets`（需求 P-06）。
15. **AI 用量有節制**：日常起草與實作先用中階模型，評審與卡關才升高階；每卡匯出對話紀錄到 `docs/ai-logs/`（需求 P-01 與繳交要求）。
16. **圖表優先**：`/speckit-specify` 階段先產出 PlantUML 組件圖、類別圖、時序圖存 `diagrams/` 並 `make diagrams` 轉 PNG；`/speckit-plan` 以圖為藍圖；`/speckit-implement` 後逐圖核對程式（元件、類別、訊息序）並把核對表寫進該功能的 `verification.md`。判據：`make gate-diagrams`（每個 `.puml` 有同名 `.png`、語法可解析）＋實作輪評審核圖碼一致。完整條文見憲章原則 VII。

## 常用指令與工作流

- **Codex 開發者讀同層 `AGENTS.md`**：由本檔產生（`make sync-agents`），根目錄版附 Claude→Codex 對應表；改本檔或 `.claude/skills/review-dispatch` 後必跑 `make sync-agents`，漏跑由 `make gate-agents` 判紅。
- S/B 檔走 `/speckit-specify`（含圖表）→ `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → 提案輪評審 → `/speckit-implement` → 圖表一致性核對 → 實作輪評審；C 檔直接改。一個功能（`specs/NNN-<卡名>/`）對應一張卡（卡名與 `docs/parity.md` §4 一致），一卡一分支一 PR，一卡一會話。Spec Kit 以分支名 `NNN-<卡名>` 辨識目前功能，故功能分支不用 `feat/` 前綴。
- 實作遵循 brainstorming → TDD → verification-before-completion。

`make hooks`（clone 後裝一次）｜`make test` 全部單元測試｜`make gate-pr` PR 門禁｜`make gate` 全量｜`make gate-docs` 純文件批｜`make gate-parity SIBLING=<路徑>` 兩組共用檔比對｜`make probe-guided-notes` 範本結構探針｜`make diagrams` PlantUML 轉 PNG｜`make gate-diagrams` 圖表門禁；全清單 `make help`。應用程式的 `make dev`、server／web 的測試與 lint 由 `app-skeleton` 卡加入並接進 `gate-pr`。

## 通用編碼規範

- 各元件語言級規範見其目錄下 CLAUDE.md（由建立該元件的卡新增）。註解寫「程式碼說不出的約束」，不寫「程式碼在做什麼」。
- 規格文件行號引用帶錨 `` `path:n`「錨串」 ``。
- 金鑰只經環境變數；`.env` 與憑證 JSON 永不入庫。
- 日誌不記學生作答原文，只記活動 id、題號、組別、階段與判定結果。

## 提交規範

- Conventional Commits：`feat|fix|test|docs|chore|refactor(scope): 描述`，scope ∈ server/web/contracts/ops/specs/diagrams/docs；描述用繁體中文。
- PR 首屏第一行寫檔位；另寫「評審閉環否／測試與門禁綠否／parity」三行（`.github/pull_request_template.md`）。
- 分支模型：`main` 穩定基線（Demo 與繳交用）；`dev` 整合分支，功能分支 `NNN-<卡名>`（Spec Kit 慣例）從 `dev` 拉、合回 `dev`；里程碑由負責人把 `dev` 經 PR 合入 `main`。

# Compact instructions

壓縮時保留：卡名與檔位、PR 號與連結、負責人裁定原文、待辦與「有意不改」清單、在改檔案路徑、已派評審 agent 及結論行、parity 待同步事項。丟棄：工具原始輸出、已落地的藥方細節、已合入 PR 的過程。

---

## Codex 對應表（僅附於根目錄 AGENTS.md；移植自 hybrid_agent）

本檔上方是 `CLAUDE.md` 全文，**對 Codex 一體適用**；文中提到 Claude Code 專屬機制時，依下表換成 Codex 的對應做法。判據、檔位、紀律不因工具不同而放寬。

| CLAUDE.md 寫的 | Codex 照做的方式 |
|---|---|
| 規範檔 `CLAUDE.md`（各層） | 同層的 `AGENTS.md`（由 `make sync-agents` 產生，勿手改；改規範一律改 `CLAUDE.md`） |
| `Skill(review-dispatch)` | `$review-dispatch`（`.agents/skills/review-dispatch/`，與 Claude 版同源產生） |
| 派 finder-tail 子代理／「另一頂層會話」評審 | `make review-codex CHANNEL=red\|arch DISPATCH=<派單檔> [DIR=<工作樹>]`：在受評 HEAD 的一次性 git worktree 副本以 `codex exec --sandbox workspace-write --ephemeral` 起獨立會話（評審員可在副本跑測試、做變異實驗，真實工作樹不可寫，結束即刪副本）；提示詞＝`.claude/agents/finder-tail-<CHANNEL>.md` 本文＋派單檔＋執行環境說明；回報寫入派單檔同目錄的 `*.review-<CHANNEL>.md` |
| `/opsx:propose`、`/speckit-specify` 等斜線指令 | `$openspec-propose`、`$speckit-specify` 等 skills（`.agents/skills/`，由 `openspec init --tools codex`／`specify integration install codex` 產生） |
| `.claude/settings.json` deny `git push` | `.codex/rules/software_fin.rules` 以 `decision = "forbidden"` 擋 `git push`（**專案層 `.codex/` 須經使用者信任才載入**）；不論信任與否，`make hooks` 裝的 pre-push 鉤子都會擋推 `main`／`dev` |
| 推送由負責人以 `!` 執行 | 推送由負責人自己執行；Codex 不得 `git push`，也不得以 `git -C …`、`bash -lc …`、`make --eval` 等包裝繞過——規則只比對指令前綴，包裝形式比對不到，**仍屬禁止**（紀律「並行隔離」） |
| 記憶檔（`~/.claude/projects/…/memory`） | 無對應；需跨會話保留的教訓寫進 `docs/` 或本倉規範 |

**Codex 專屬注意事項**

- 本機 Codex 桌面版的 CLI 不一定在 PATH：`make review-codex CODEX=<codex.exe 路徑>` 指定。
- Windows：Store 版 Python 與 uv 硬連結安裝的套件在 Codex 沙箱內不可用；`make review-codex` 派單前會實測，預檢不過時提示詞寫明「未實跑」——先在受評工作樹跑 `make codex-venv` 再重派。
- 送評審員的內容會離開本機送到 OpenAI；派單與 diff 不得含真實個資或金鑰（紀律「真實資料不入庫」已保證倉內皆合成資料）。
- 評審員回報格式與 Claude 版相同（末行 `CLEARED` / `NOT CLEARED(nB/nM/nm)`），開方回驗仍由同一通道重跑 `make review-codex`。
