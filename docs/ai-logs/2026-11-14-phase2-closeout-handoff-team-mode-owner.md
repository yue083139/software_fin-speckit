# 2026-11-14 第二期收尾＋組員交接＋第三期組隊（負責人會話）

- 來源：Claude Code `/export`（2026-11-15 02:04），涵蓋第二期收尾與刪分支、產品 TRD 與人工驗證手冊、第三期 `team-mode`（提案、雙通道評審、實作、合入）、第三期收尾；兩組同一會話完成，故兩個 repo 放同一份。
- 入庫前自檢（2026-11-15）：掃過電子郵件、GitHub／API 權杖、老師金鑰與組別憑證樣式，皆零命中（唯一的 `@` 命中是 `@pytest.fixture`）；本機路徑（暫存目錄、記憶檔、另一專案的 venv）帳號名皆為通用 `user`，另有 GitHub 帳號（已在 repo 內），無需遮蔽；不含真實學生資料。

~~~~text
 ▐▛███▛█   Claude Code v2.1.325
▝▜██████▀  Opus 5.5 · Claude Ultra
 ▝▝   ▝▝   C:\workspace\software_fin


❯ 檢查一下目前需要做的事情                                                      

  Read 1 file, ran 3 shell commands (ctrl+o to expand)

● 上次關 CLI 前留了一份待辦（11/12 存的）。我對了一下兩個 repo
  現在的狀態：之後沒有新的提交，六項都還沒做。期限是 2026-11-30，還有 16 天。

  要你決定或親手做的

  1. 刪第二期分支：整串已經合完，照先例可以刪，但要你同意。共六支，本地和遠端都
     還在：
     - OpenSpec：feat/game-mode-framework、feat/question-settings、feat/mode-tim
       ed-scoring
     - SpecKit：006-game-mode-framework、007-question-settings、008-mode-timed-s
       coring
     - 兩個 repo 目前都還停在 mode-timed-scoring
       這張卡的分支上，刪之前我會先切回 dev。
  2. 五處還沒明確批准。你上次說的「合」，我只當成同意合併。
     - 契約上補了三處語意：
       - 雙倍題的得主得「1 × 倍率」分。
       - 設定 API 的兩個欄位改成可選。
       - 時間計分在搶答進行中就判定。
     - 有兩處跟你原本的裁定字面不同：
       - 排行榜只公開名次，不公開他組分數。
       - 時間計分活動開始前不先發學習單。
  3. 人工驗證：第一期五張卡和第二期三張卡都還沒跑。步驟寫在各卡的
     verification.md。
  4. 對話紀錄：你上次匯出的檔案在 C:\workspace\software_fin\2026-11-12-234033-hy
     bridagentsoftwarefinp.txt，還不在任何一個 repo 裡。我會先遮掉 email、token
     這類個資，再放進兩組的 docs/ai-logs/。

  我可以直接做的

  5. 收尾 PR，兩組各開一個：
     - 在 docs/ops-log.md 記下第二期的合併。
     - 把 docs/parity.md 裡三張卡的狀態從「待合入」改成「已合入」。
     - 用 openspec archive 歸檔第二期的三個 change，這三個目前還放在
       openspec/changes/。
     - 第 4 項遮好的對話紀錄也一起放進這個 PR。

  可選

  6. 另開一張卡做「時間計分開題時顯示題目文字」，以及第三期的組隊模式（代表作答
     的方式你已經定了）。

  你回我兩件事就能開始：第 1 項刪不刪，第 2 項那五處批不批。第 4、5
  項我現在就可以先做。

✻ Brewed for 37s · done Saturday 6:36 PM

❯ 刪、批、第三期做，順便開一張卡把所有需要人工驗證的部分整理一起，我之後交給組  
  員做，剩下的全部歸檔                                                          

  Ran 3 shell commands (ctrl+o to expand)

● Precedent: last time remote branches were deleted via gh api after confirming
  content is in dev. Doing the same.

  Ran 2 shell commands (ctrl+o to expand)

❯ 順便做一個產品trd讓第一次看專案的人可以馬上知道專案特色                       

● Noted the product-overview request — I'll add it alongside the verification
  guide. Continuing with the close-out first.

  Ran 2 shell commands (ctrl+o to expand)

● Now scanning the exported transcript for secrets/PII before putting it into
  the repos.

  Ran 3 shell commands (ctrl+o to expand)

● Transcript is clean (only test placeholder keys and file hashes). Creating the
  close-out branch in OpenSpec and archiving.

  Ran 4 shell commands (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  17:## 契約語意補充（待負責人批准）
     23:狀態：**待負責人執行**。
  ⎿  Updated software_fin-openspec\openspec\specs\game-modes\spec.md (+1 
     -1)
      1  # game-modes Specification
      2  
      3  ## Purpose
      4 -TBD - created by archiving change game-mode-framework. Update Pu
        -rpose after archive.                                            
      4 +老師在準備階段選擇遊戲模式（經典搶答、只計對錯、時間計分），以及
        +需要判定的模式在揭曉前由老師逐筆判定正確／錯誤、參考答案只用於預
        +填建議且永不送往學生端的規則。                                  
      5  
      6  ## Requirements
      7  
  ⎿  Updated software_fin-openspec\openspec\specs\question-settings\spec.md
     (+1 -1)
      1  # question-settings Specification
      2  
      3  ## Purpose
      4 -TBD - created by archiving change question-settings. Update Purp
        -ose after archive.                                              
      4 +老師在準備階段對個別題目設定加成（雙倍分數），任何模式下該題得分
        +乘以倍率，且學生看得到哪些題是雙倍的規則。                      
      5  
      6  ## Requirements
      7  
  ⎿  Updated software_fin-openspec\openspec\specs\timed-scoring\spec.md (+1
     -1)
      1  # timed-scoring Specification
      2  
      3  ## Purpose
      4 -TBD - created by archiving change mode-timed-scoring. Update Pur
        -pose after archive.                                             
      4 +時間計分模式下老師逐題開放、伺服器計時並關閉題目、依伺服器量得的
        +作答時間計分，以及每題揭曉後學生只看得到本組分數與全部組別名次的
        +規則。                                                          
      5  
      6  ## Requirements
      7  

  Ran 1 shell command (ctrl+o to expand)

● 兩組的六支分支已刪除，OpenSpec 第二期三個 change 也歸檔完成。我正在改收尾 PR
  的文件，接下來記錄你批准的五處、更新 parity 狀態、補 ops-log 並放對話紀錄。 
  · summary

  Ran 1 shell command (ctrl+o to expand)

● Now applying the shared-file edits to both repos in one script.

● Bash(cd /c/workspace/software_fin; python - <<'EOF'
      from pathlib import Path…)
  ⎿  1:# TRD：多模式搶答（遊戲模式）
     11:- **本 TRD 不做**：遊戲幣與道具、自主步調（學生自己翻題）、跨活動的
     累積排行榜。
     parity-same
  ⎿  Updated software_fin-openspec\docs\parity.md (+5 -3)
      43  | `guided-notes-export` | R-05 | 只在結束後可匯出；每題得主答案
          寫回原檔作答格（佔位符取代、否則接在標籤後，一律存為文字）；無
          人搶答題不變；檔名 `<原檔名>-搶答結果.xlsx` | 已合入 | 已合入 |
      44  | `csv-export` | X-02 | 題號、組別、答案、搶答順位匯出 CSV | 未
          開 | 未開 |
      45  | `fair-ranking` | X-03 | 公平順位機制：已搶答成功的組別下一題
          延遲計入順位（併入模式框架，見 `docs/trd-game-modes.md`） | 未
          開 | 未開 |
      46 -| `game-mode-framework` | X-04 | 老師在準備階段選模式（經典搶答
         -／只計對錯）；只計對錯：全部題目同時開放、每組每題可送出一次， 
         -結束後進入**判定中**，老師逐筆標正確／錯誤（匯入檔若有參考答案 
         -欄則預填建議，老師可「採用全部建議」），全部判定完才能揭曉；正 
         -確得 1 分，得主＝最早送出的正確答案（匯出寫回它）；判定中學生只
         -看到自己組的送出；參考答案與判定建議永不送往學生端；經典搶答行 
         -為不變（TRD T-01～T-04、T-06、M3） | 已實作（待合入） | 已實作 
         -（待合入） |                                                   
      47 -| `question-settings` | X-04 | 準備階段老師可把任一題設為**雙倍
         -分數**（倍率 1 或 2），任何模式下該題得分 ×2；重新匯入即清除、 
         -重置活動保留；學生看得到哪些題是雙倍；分數欄名在全部倍率為 1 的
         -經典搶答顯示「得題數」，其餘顯示「得分」（TRD T-05 倍率） | 已 
         -實作（待合入） | 已實作（待合入） |                            
      46 +| `game-mode-framework` | X-04 | 老師在準備階段選模式（經典搶答
         +／只計對錯）；只計對錯：全部題目同時開放、每組每題可送出一次， 
         +結束後進入**判定中**，老師逐筆標正確／錯誤（匯入檔若有參考答案 
         +欄則預填建議，老師可「採用全部建議」），全部判定完才能揭曉；正 
         +確得 1 分，得主＝最早送出的正確答案（匯出寫回它）；判定中學生只
         +看到自己組的送出；參考答案與判定建議永不送往學生端；經典搶答行 
         +為不變（TRD T-01～T-04、T-06、M3） | 已合入 | 已合入 |         
      47 +| `question-settings` | X-04 | 準備階段老師可把任一題設為**雙倍
         +分數**（倍率 1 或 2），任何模式下該題得分 ×2；重新匯入即清除、 
         +重置活動保留；學生看得到哪些題是雙倍；分數欄名在全部倍率為 1 的
         +經典搶答顯示「得題數」，其餘顯示「得分」（TRD T-05 倍率） | 已 
         +合入 | 已合入 |                                                
      48  | `mode-buzz-fallback` | X-03、X-04 | 搶答＋錯誤遞補：最先送出
          者判錯則依順位遞補（TRD M1） | 未開 | 未開 |
      49 -| `mode-timed-scoring` | X-04 | **時間計分**模式：老師逐題開放 
         -，每題時限 5–120 秒（預設 20，準備階段設定），到時伺服器關閉該 
         -題、老師也可提早結束；只收開放中那一題；老師判定該題後揭曉；正 
         -確得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（以整數運算 `
         -(2001 × T − 作答毫秒) // (2 × T)` 實作，避免浮點誤差）（t ≤ 0.5
         - 秒得滿分，t 為伺服器量得的作答秒數）；揭曉後學生看到本組該題對
         -錯與得分、本組累積分數，以及全部組別的累積**名次**（不含他組分 
         -數，以免反推作答秒數）；他組答案、分數仍只在活動結束後才看得到 
         -（TRD M2、T-04、T-05 時限） | 已實作（待合入） | 已實作（待合入
         -） |                                                           
      49 +| `mode-timed-scoring` | X-04 | **時間計分**模式：老師逐題開放 
         +，每題時限 5–120 秒（預設 20，準備階段設定），到時伺服器關閉該 
         +題、老師也可提早結束；只收開放中那一題；老師判定該題後揭曉；正 
         +確得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（以整數運算 `
         +(2001 × T − 作答毫秒) // (2 × T)` 實作，避免浮點誤差）（t ≤ 0.5
         + 秒得滿分，t 為伺服器量得的作答秒數）；揭曉後學生看到本組該題對
         +錯與得分、本組累積分數，以及全部組別的累積**名次**（不含他組分 
         +數，以免反推作答秒數）；他組答案、分數仍只在活動結束後才看得到 
         +（TRD M2、T-04、T-05 時限） | 已合入 | 已合入 |                
      50  | `team-mode` | X-04 | **組隊模式**：一組多台裝置，組內任一人送
          出即代表全組（TRD M4，§6 裁定）；第三期 | 未開 | 未開 |
      51  
      52  狀態值：未開／提案中／實作中／已實作（待合入）／已合入。
     ...
      64  | 2026-11-11 | 核心五卡 | 兩組皆合入 `dev`（OpenSpec #2、#7；Sp
          ecKit #2、#4–#6），`dev` 上 server、web/src、contracts、需求與 
          parity、夾具 `diff -r` 無差異；人工驗證待負責人補驗 | 兩組 | 已
          確認 |
      65  | 2026-11-12 | 第二期三卡 | 負責人裁 TRD §6（老師判定＋參考答案
          預填、組隊＝代表作答、排行榜每題揭曉後公開）與第二期範圍；M3 移
          入 `game-mode-framework`、時限移入 `mode-timed-scoring`；三卡 §
          4 摘要寫入擬定行為 | 兩組（負責人裁定） | 同一會話兩組同批起稿 
          |
      66  | 2026-11-12 | 第二期三卡 | 提案輪評審（v1.1）：時間計分公式改
          以整數運算定義；學生端排行榜只公開名次（TRD §6 落實方式）；TRD 
          T-05 屬性名改為 `multiplier`、`time_limit` | 兩組 | 同一會話兩
          組同批修訂 |
      67 +| 2026-11-12 | 第二期三卡 | 兩組皆合入 `dev`（OpenSpec #9–#11；
         +SpecKit #8–#10），`dev` 上 server、web 逐字相同；人工驗證待補驗
         + | 兩組 | 已確認 |                                             
      68 +| 2026-11-14 | 第二期三卡 | 負責人批准契約語意補充三處（經典得 
         +主得 1×倍率分、`team_scores` 欄名看 `score_label`；設定 API 兩 
         +欄位可選；時間計分在 `answering` 內判定），並確認兩處落實方式（
         +學生端排行榜只公開名次；時間計分活動前不先發學習單） | 兩組（負
         +責人裁定） | 已確認 |                                          
  ⎿  Updated software_fin-openspec\docs\reviews\2026-11-12-phase2-review.md
     (+3 -1)
      17  | 架構 | 重要 | 主規格 results-view「結束前不得有結果」與時間計
          分揭曉後結果矛盾 | mode-timed-scoring `specs/results-view` MODI
          FIED |
      18  | 架構 | 重要 | 主規格「順位 1 為搶答成功者」未限定經典模式 | g
          ame-mode-framework `specs/buzz-answering` MODIFIED |
      19  | 架構 | 重要 | 第一期測試斷言經典規則忽略倍率，與雙倍題衝突，
          稿未提 | question-settings tasks 1.1 改寫該測試 |
      20 -| 架構 | 重要 | 雙倍題改了契約既有欄位的數值語意，未列為語意補 
         -充 | question-settings D3「契約語意補充」（**待負責人批准**） |
      20 +| 架構 | 重要 | 雙倍題改了契約既有欄位的數值語意，未列為語意補 
         +充 | question-settings D3「契約語意補充」（負責人 2026-11-14 批
         +准） |                                                         
      21  | 兩通道 | 次要 | TRD／parity 公式寫 `round`；view 缺 `mode.seq
          uential`；送出路徑未寫明只讀一次時鐘；設定 API 本體放寬未列語意
          補充；同名次可知對方分數；名次測試以數字子字串比對會假紅 | 各卡
           v1.1／v1.2 對應段落 |
      22  
      23  ## 實作期自查（變異實錄抓到的假綠）
     ...
      39  1. 契約語意補充三處（經典得主得 1×倍率、`team_scores` 欄名看 `s
          core_label`；設定 API 本體放寬；時間計分的判定在 `answering` 內
          ）——我傾向批准。
      40  2. 時間計分的紙本備答代價——我傾向接受，並在人工驗證／Demo 時不
          先發學習單。
      41  3. 三張卡的人工驗證（P-05），步驟在各卡 `verification.md`。
      42 +                                                               
      43 +**負責人裁定（2026-11-14）**：第 1、2 項批准；第 3 項人工驗證交
         +組員執行（見 `docs/manual-verification.md`）。                 
  ⎿  Updated software_fin-openspec\docs\trd-game-modes.md (+1 -1)
      60  
      61  第一列於第一期依「我傾向」執行；其餘三列由負責人於 2026-11-12 
          裁定，皆採「我傾向」。
      62  
      63 -**排行榜的落實方式**（第二期提案輪評審）：時間計分的每題分數是 
         -作答秒數的單調函數，若公開他組累積**分數**，學生把前後兩次排行 
         -榜相減即可反推他組作答秒數與答對先後；故依裁定原文「公開累積** 
         -排名**」，學生端排行榜只列各組名次，不列他組分數（本組分數照常 
         -顯示），老師端列分數。                                         
      63 +**排行榜的落實方式**（第二期提案輪評審）：時間計分的每題分數是 
         +作答秒數的單調函數，若公開他組累積**分數**，學生把前後兩次排行 
         +榜相減即可反推他組作答秒數與答對先後；故依裁定原文「公開累積** 
         +排名**」，學生端排行榜只列各組名次，不列他組分數（本組分數照常 
         +顯示），老師端列分數。負責人 2026-11-14 確認此落實方式，並確認 
         +時間計分活動前**不先發紙本學習單**（避免學生先備答，削弱計時的 
         +意義）。                                                       
      64  
      65  | 事項 | 裁定 | 原阻塞 |
      66  |---|---|---|
  ⎿  Updated software_fin-openspec\openspec\changes\archive\2026-11-14-ques
     tion-settings\verification.md (+1 -1)
      14  | D4 web | `web/src/pages/ImportPanel.tsx` `QuestionList`（勾選
          框）、`DoubleTag`；`AnswerForm.tsx`、`Results.tsx` 標記；`setti
          ngs.test.tsx` |
      15  | 第一期測試改寫 | `server/tests/test_scoring.py::test_judgment
          s_do_not_change_classic`（原 `test_reserved_inputs_do_not_chang
          e_classic`）；`test_api_import.py::test_upload_broadcasts_quest
          ions` 期望值加 `multiplier`（只增欄位） |
      16  
      17 -## 契約語意補充（待負責人批准）                                
      17 +## 契約語意補充（負責人 2026-11-14 批准）                      
      18  
      19  `contracts/api.md`：經典規則得主得「1 × 該題倍率」分；`team_sco
          res` 欄名見 `score_label`。欄位與型別不變，只有數值範圍變大（de
          sign D3）。
      20  

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin; python - <<'EOF'
      from pathlib import Path…)
  ⎿  All checks passed!
     All checks passed!
     198 passed, 1 warning in 37.82s
     … +7 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\docs\ops-log.md (+2 -0)
      11  | 2026-11-12 | dev | 負責人以 `!` 合併收尾 PR（OpenSpec #8、Spe
          cKit #7）；本機 dev 設定追蹤 origin/dev 並快轉 | dev 含第一期收
          尾文件 | 以 `rollback/01-pre-phase1` 開回復分支經 PR 還原 |
      12  | 2026-11-12 | 已合併的遠端功能分支 | 依負責人「清理分支」以 `g
          h api -X DELETE …/git/refs/heads/<分支>` 刪除兩 repo 共 8 支已
          合併遠端分支（OpenSpec 3 支、SpecKit 5 支；刪前以 `git rev-list
          ` 與 `git diff` 確認內容皆已在 dev），並刪除對應本機分支 | GitH
          ub 分支清單只剩 main、dev | 分支內容皆在 dev；需要時以已合併 PR
           頁面的 Restore branch 還原 |
      13  | 2026-11-12 | 本機 | 第二期三卡完成：疊層分支 feat/game-mode-f
          ramework → feat/question-settings → feat/mode-timed-scoring；本
          機打標籤 `rollback/02-pre-phase2`（指向第二期前的 dev 1f8302a）
          ，待負責人以 `!` 推送分支與標籤 | 僅本機 | 刪除本機分支與標籤 |
      14 +| 2026-11-12 | dev | 依負責人「合」依序合併第二期疊層 PR #9–#11
         +（每合一個前先把基底改為 dev，一般合併，整串合完前不刪分支）；d
         +ev 到 070ac4a | dev 含第二期三卡 | 以 `rollback/02-pre-phase2` 
         +開回復分支經 PR 還原 |                                         
      15 +| 2026-11-14 | 已合併的遠端功能分支 | 依負責人「刪」以 `gh api 
         +-X DELETE …/git/refs/heads/<分支>` 刪除第二期三支遠端分支（feat
         +/game-mode-framework、feat/question-settings、feat/mode-timed-s
         +coring；刪前以 `git rev-list --count origin/dev..<分支>` 確認皆
         +為 0），並刪除對應本機分支 | GitHub 分支清單只剩 main、dev | 以
         +已合併 PR 頁面的 Restore branch 還原 |                         
  ⎿  (timeout 10m)

  Ran 2 shell commands (ctrl+o to expand)

● Close-out committed in both repos. Next: the handoff-docs card (manual
  verification guide + product overview). Reading the existing manual steps.

  Ran 3 shell commands (ctrl+o to expand)

● Writing the two handoff docs (shared, identical in both repos), stacked on the
  close-out branch.

● Write(software_fin-openspec\docs\manual-verification.md)
  ⎿  Wrote 124 lines to software_fin-openspec\docs\manual-verification.md
       1 # 人工驗證手冊（交組員執行）
       2 
       3 > 需求 P-05：系統除 AI 自動驗證外**須人工驗證**。本檔把各卡 `ver
         ification.md` 的「人工驗證」段整理成可照做的場次，給組員一次跑完
         。
       4 > 本檔在兩個 repo 逐位元組相同。兩組 `server/`、`web/` 程式碼逐
         字相同，**在任一 repo 跑一次即可**，但要記下是哪個 repo 與 commi
         t。
       5 > 新卡合入時，把該卡的人工驗證步驟加成新場次（或併入既有場次），
         並在 §5 加一列。
     … +119 lines (ctrl+o to expand)
  ⎿  Loaded CLAUDE.md

● Checking the UI labels I cited actually exist in the web code.

  Ran 2 shell commands (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  ok
  ⎿  Updated software_fin-openspec\docs\manual-verification.md (+2 -2)
      18  
      19  3. 終端機會印出**老師頁網址**（含老師金鑰）。學生頁一律開 `http
          ://127.0.0.1:8000/`。
      20  4. 建議用一個瀏覽器視窗開老師頁，另開**無痕視窗**或不同瀏覽器開
          學生分頁（同一組只能一台裝置；分頁被拒時改用另一個瀏覽器設定檔
          ）。
      21 -5. 每個場次開始前：老師頁按「重置活動」，或在終端機 `Ctrl+C` 後
         -重新 `make dev`（伺服器重啟即清空活動）。                      
      21 +5. 每個場次開始前：老師頁按「重置活動」（只在「已結束」時可按；
         +會保留題目與設定、清空作答），或在終端機 `Ctrl+C` 後重新 `make 
         +dev`（伺服器重啟即清空活動，學生分頁要重新選組）。             
      22  6. 夾具都在 `tests/fixtures/guided-notes/`：`single.xlsx`（6 單
          題）、`group.xlsx`（4 題，第 1、2 題為題組）、`variant.xlsx`（
          版面不同的 5 題）、`reference.xlsx`（含參考答案欄）。
      23  7. 「從連結匯入」與「匯回 Google 試算表」兩步需要 Google 帳號：
          把 `group.xlsx` 上傳到自己的 Google 雲端硬碟並以 Google 試算表
          開啟，共用設為「知道連結者可檢視」。
      24  
     ...
      41  1. 開三個分頁：老師頁、學生「第1組」、學生「第2組」。
      42  2. 再開一個分頁也選「第1組」⇒ 應顯示「此組已有裝置加入」。
      43  3. 老師頁看到第1組、第2組「已加入」；按第2組的「釋放」⇒ 第2組分
          頁顯示「尚未加入組別或組別已被老師釋放」。第2組重新加入。
      44 -4. 尚未匯入題目時「開始搶答」應無法開始（須先匯入）。          
      44 +4. 尚未匯入題目時按「開始搶答」⇒ 顯示「尚未匯入題目，不能開始搶
         +答」，階段仍為「準備中」。                                     
      45  
      46  **A2 匯入（guided-notes-import）**
      47  

● Now the product TRD for newcomers.
● Write(software_fin-openspec\docs\product-trd.md)
  ⎿  Wrote 99 lines to software_fin-openspec\docs\product-trd.md
      1 # 產品 TRD：Vibe Coding 課堂搶答系統
      2 
      3 > 給第一次看這個專案的人：5 分鐘讀完就知道它做什麼、哪裡和一般搶
        答系統不同、要往哪裡看。
      4 > 本檔在兩個 repo 逐位元組相同。細節以 `docs/requirements.md`（需
        求）、`contracts/api.md`（介面）、各組規格為準；本檔衝突時以它們
        為準。
      5 > 知識時點：2026-11-14（第一、二期已合入 `dev`，第三期進行中）。
      6 
      7 ## 1. 一句話
     … +92 lines (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin; for r in software_fin-openspec
      software_fin-speckit; do (cd $r; git switch -q -c docs/team-handoff);
      done; cp software_fin-openspe…)
  ⎿  **Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
     **Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
     **Status**: Merged（人工驗證待執行，見 `docs/manual-verification.md`）
     … +15 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\README.md (+2 -0)
       6  
       7  | 文件 | 內容 |
       8  |---|---|
       9 +| [`docs/product-trd.md`](docs/product-trd.md) | **第一次看專案
         +先讀這份**：產品一句話、功能一覽、專案特色、架構與閱讀路線 |   
      10  | [`docs/requirements.md`](docs/requirements.md) | 需求基線（兩
          組共用，編號 R-／X-／P-） |
      11  | [`docs/parity.md`](docs/parity.md) | 兩組功能一致協議、共用技
          術選型、功能清單與未決事項 |
      12  | [`docs/trd-game-modes.md`](docs/trd-game-modes.md)、[`docs/re
          search/competitors.md`](docs/research/competitors.md) | 多模式
          搶答 TRD（時間計分、雙倍分數、組隊等）與競品探索 |
      13  | [`CLAUDE.md`](CLAUDE.md)／`AGENTS.md` | AI 代理工程規範（Clau
          de Code／Codex） |
      14  | [`docs/workflow.md`](docs/workflow.md) | 開發工作流導讀 |
      15 +| [`docs/manual-verification.md`](docs/manual-verification.md) 
         +| 人工驗證手冊（需求 P-05）：給組員照做的場次與結果表 |        
      16  | [`openspec/`](openspec/) | 專案脈絡、行為規格與變更卡（評分檢
          驗 proposal／spec／design／tasks） |
      17  
      18  ## 快速開始

● Bash(cd /c/workspace/software_fin; for r in software_fin-openspec
      software_fin-speckit; do (cd $r; files=$(git grep -l
      "狀態：\*\*待負責人執行\*\*" -- 'openspec/changes/archi…)
  ⎿  software_fin-openspec: 8 files
     gate-zh-hant: 0 處簡體字
     gate-secrets: 0 findings
     … +10 lines (ctrl+o to expand)
  ⎿  Updated software_fin-speckit\specs\001-app-skeleton\verification.md
     (+1 -1)
      51  
      52  ## 人工驗證（需求 P-05）
      53  
      54 -狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/ar
         -chive/2026-11-12-app-skeleton/verification.md`：               
      54 +狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應
         +場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/
         +archive/2026-11-12-app-skeleton/verification.md`：             
      55  
      56  1. `make web-install` 後 `make dev`，記下終端機印出的老師頁網址
          。
      57  2. 三個分頁：老師頁、首頁選第1組、首頁選第2組；第四個分頁再選第
          1組應顯示「此組已有裝置加入」。
  ⎿  Updated
     software_fin-speckit\specs\002-guided-notes-import\verification.md (+1
     -1)
      44  
      45  ## 人工驗證（需求 P-05）
      46  
      47 -狀態：**待負責人執行**。步驟：                                 
      47 +狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應
         +場次執行，結果回填本段）。步驟：                               
      48  
      49  1. `make dev`，開老師頁。
      50  2. 依序上傳 `tests/fixtures/guided-notes/single.xlsx`、`group.x
          lsx`、`variant.xlsx`，題目清單分別為 6 題、4 題（第 1、2 題為 2
           子題）、5 題（第 2 題 3 子題、第 4 題 2 子題）。
  ⎿  Updated software_fin-speckit\specs\003-buzz-answering\verification.md
     (+1 -1)
      47  
      48  ## 人工驗證（需求 P-05）
      49  
      50 -狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/ar
         -chive/2026-11-12-buzz-answering/verification.md`：兩組搶同一題 
         -、題組只填一格無法送出、第2組畫面與開發者工具的 WebSocket 訊息 
         -看不到第1組答案、重複送出被拒、結束後才看到結果。              
      50 +狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應
         +場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/
         +archive/2026-11-12-buzz-answering/verification.md`：兩組搶同一 
         +題、題組只填一格無法送出、第2組畫面與開發者工具的 WebSocket 訊 
         +息看不到第1組答案、重複送出被拒、結束後才看到結果。            
      51  
      52  結果：＿＿＿（執行人／日期／看到什麼）
  ⎿  Updated software_fin-speckit\specs\004-results-view\verification.md
     (+1 -1)
      33  
      34  ## 人工驗證（需求 P-05）
      35  
      36 -狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/ar
         -chive/2026-11-12-results-view/verification.md`：三組各搶不同題 
         -，老師表即時更新、得主格變色；搶答中學生頁無結果；結束後三個學 
         -生頁與老師表一致。                                             
      36 +狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應
         +場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/
         +archive/2026-11-12-results-view/verification.md`：三組各搶不同 
         +題，老師表即時更新、得主格變色；搶答中學生頁無結果；結束後三個 
         +學生頁與老師表一致。                                           
      37  
      38  結果：＿＿＿（執行人／日期／看到什麼）
  ⎿  Updated
     software_fin-speckit\specs\005-guided-notes-export\verification.md (+1
     -1)
      121  
      122  ## 人工驗證（需求 P-05）
      123  
      124 -狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/a
          -rchive/2026-11-12-guided-notes-export/verification.md`：匯出檔
          -名、Excel 開啟確認作答格與框線、上傳回 Google 試算表確認答案在
          -原填空格。                                                    
      124 +狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對 
          +應場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/chang
          +es/archive/2026-11-12-guided-notes-export/verification.md`：匯
          +出檔名、Excel 開啟確認作答格與框線、上傳回 Google 試算表確認答
          +案在原填空格。                                                
      125  
      126  結果：＿＿＿（執行人／日期／看到什麼）
  ⎿  … 3 more files changed
  ⎿  (timeout 5m)

  Ran 1 shell command (ctrl+o to expand)

● Both docs branches committed and gates green. Next, the C-tier review requires
  an independent adversarial pass on the diff — let me check the dispatch
  skeleton.

  Ran 1 shell command (ctrl+o to expand)

● finder-tail-red(C-tier adversarial review docs PRs)
  ⎿  Initializing…
  ⎿  Error: Agent type 'finder-tail-red' not found. Available agents: claude, 
     claude-code-guide, Explore, general-purpose, Plan, statusline-setup, 
     web-fetch

● Agent(C-tier adversarial review docs PRs)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● While that review runs, starting phase 3 (team-mode, S tier). Reading the
  server's identity/join code first.

  Ran 5 shell commands (ctrl+o to expand)

● Design is forming. Checking frontend pieces, existing proposal formats, and
  PlantUML tooling before drafting the team-mode proposal.

  Ran 6 shell commands (ctrl+o to expand)

● 目前進度：收尾 PR 和交接文件（產品 TRD、人工驗證手冊）在兩組都已經
  commit，對抗評審正在背景跑。現在在寫第三期組隊模式的 OpenSpec 提案。

  Ran 1 shell command (ctrl+o to expand)

● Write(software_fin-openspec\openspec\changes\team-mode\proposal.md)
  ⎿  Wrote 40 lines to
     software_fin-openspec\openspec\changes\team-mode\proposal.md
      1 # team-mode — 組隊模式：一組多台裝置、代表作答（v1.0）
      2 
      3 檔位：**S**（作答隔離：新增送往學生端的組內草稿通道；`contracts/`
         增端點與欄位；組別憑證口徑改變）｜主人：@yue083139｜parity：`doc
        s/parity.md` §4 `team-mode`｜需求：X-04（TRD M4、§6 裁定「代表作
        答」）｜依賴：`game-mode-framework`
      4 
      5 ## 首屏決策摘要
      6 
      7 1. **組隊是與模式正交的活動設定，不是第四種模式**：選了 `team_pla
     … +34 lines (~2 KB) (ctrl+o to expand)

● Write(software_fin-openspec\openspec\changes\team-mode\design.md)
  ⎿  Wrote 63 lines to
     software_fin-openspec\openspec\changes\team-mode\design.md
      1 # team-mode — design（v1.0）
      2 
      3 知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，20
        26-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論時間
        」，隊員分數平均；Quizlet Live 隨機分隊，每位隊員只看到部分選項。
        本卡依 TRD §6 裁定只取「一隊多人、一人代表作答」，不採分數平均與
        討論時間。
      4 
      5 倉外行為探針：無。本卡的決策只依賴本倉既有的鎖、序號與依身分裁切
        的 view（`server/quiz_server/activity.py`、`views.py`），不依賴第
     … +59 lines (~4 KB) (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; sed -i
      's/`test_api_skeleton.py::test_second_device_rejected`
      等既有測試/`test_api_skeleton.py::test_join_once_pe…)
  ⎿  """作答隔離負例（buzz-answering
     D3、D6；docs/discipline-precedents.md「
     作答隔離」）。
     … +119 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\design.md (+1
     -1)
      60  
      61  `contracts/api.md` 增 `POST /api/teacher/team-play`（`{enabled}
          ` ⇒ `{team_play}`；401／409 非 preparing／422）、`POST /api/stu
          dent/draft`（D4）；`POST /api/student/join` 本體 `{team, code?}
          `，增 403 邀請碼不正確、409 此組裝置已滿；`/api/public/info` 增
           `team_play`；老師與學生 view 增 D5 欄位。全部是**新增**，既有
          欄位語意不變（`team_play=False` 時行為與第一期相同）。
      62  
      63 -- 證偽欄｜可證偽：`make test` 中第一期 `test_api_skeleton.py::t
         -est_second_device_rejected` 等既有測試不改仍綠。               
      63 +- 證偽欄｜可證偽：`make test` 中第一期 `test_api_skeleton.py::t
         +est_join_once_per_team`、`test_phases.py::test_concurrent_join_
         +same_team_once` 等既有測試不改仍綠。                           

● Bash(cd /c/workspace/software_fin/software_fin-openspec; sed -i
      's/②第1組更新草稿時第2組連線 1
      秒內收不到任何訊息/②第1組更新草稿時第2組連線收不到任何訊息（同既有
      `test_other_team_submit_sends_nothing` 的 seq…)
  ⎿  1
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\design.md (+1
     -1)
      46  - 學生無效憑證仍只回最少資訊（不含 `team_play`、`invite_code`）
          。
      47  - 推播：草稿更新只讓本組 view 改變；他組 view 不變 ⇒ 他組連線不
          送訊息（app-skeleton v1.1 D4 的「只在本連線的 view 改變時才送」
          ）。
      48  
      49 -- 證偽欄｜可證偽：`test_isolation.py` 新增三則：①搶答中第1組草 
         -稿「甲組草稿祕密」與第1組邀請碼不出現在第2組 WebSocket、REST 成
         -功與錯誤回應、公開資訊；②第1組更新草稿時第2組連線 1 秒內收不到 
         -任何訊息；③判定中、已結束的學生 view 不含 `drafts` 鍵。        
      49 +- 證偽欄｜可證偽：`test_isolation.py` 新增三則：①搶答中第1組草 
         +稿「甲組草稿祕密」與第1組邀請碼不出現在第2組 WebSocket、REST 成
         +功與錯誤回應、公開資訊；②第1組更新草稿時第2組連線收不到任何訊息
         +（同既有 `test_other_team_submit_sends_nothing` 的 seq 不跳號判
         +據）；③判定中、已結束的學生 view 不含 `drafts` 鍵。            
      50  
      51  ### D6 web
      52  

● Write(software_fin-openspec\openspec\changes\team-mode\specs\team-mode\spec.md
       )
  ⎿  Wrote 69 lines to software_fin-openspec\openspec\changes\team-mode\spe
     cs\team-mode\spec.md
      1 ## ADDED Requirements
      2 
      3 ### Requirement: 老師可在準備階段開啟組隊
      4 
      5 老師 MUST 能在 `preparing` 階段開啟或關閉「組隊（一組多台裝置）」
        ；其他階段 MUST 回 409。開關的值改變時，伺服器 MUST 撤銷所有組別
        憑證與邀請碼。重置活動 MUST 保留開關。組隊 MUST NOT 改變任何模式
        的作答規則、計分與揭曉時機。
      6 
      7 #### Scenario: 開啟組隊
     … +62 lines (ctrl+o to expand)

● Write(software_fin-openspec\openspec\changes\team-mode\specs\activity-lifecycl
       e\spec.md)
  ⎿  Wrote 21 lines to software_fin-openspec\openspec\changes\team-mode\spe
     cs\activity-lifecycle\spec.md
      1 ## MODIFIED Requirements
      2 
      3 ### Requirement: 系統必須區分老師與學生兩種身分
      4 
      5 系統 MUST 提供老師與學生兩種身分進場。老師 MUST 以伺服器啟動時產
        生的老師金鑰驗證；學生 MUST 選定一個組別並取得伺服器發出的組別憑
        證，之後的連線與操作 MUST 以憑證辨識組別，MUST NOT 採信客戶端自報
        的組別名稱。組隊關閉時每組 MUST 只有一台裝置；組隊開啟時同組可有
        多台裝置，第二台起 MUST 以該組邀請碼加入（team-mode）。
      6 
     … +15 lines (ctrl+o to expand)

● 組隊模式的 OpenSpec 規格寫完了。接著寫 tasks，然後驗證提案格式。

● Bash(cd /c/workspace/software_fin/software_fin-openspec; rmdir
      openspec/changes/team-mode/specs/buzz-answering; printf 'schema:
      spec-driven\ncreated: 2026-11-14\n' >…)
  ⎿  Change 'team-mode' is valid
  ⎿  Created
     software_fin-openspec\openspec\changes\team-mode\.openspec.yaml (+2 
     -0)
      1 +schema: spec-driven                                             
      2 +created: 2026-11-14                                             
  ⎿  Created software_fin-openspec\openspec\changes\team-mode\tasks.md (+16
     -0)
       1 +# team-mode — tasks（v1.0）                                    
       2 +                                                               
       3 +## 1. 驗收先行                                                 
       4 +- [ ] 1.1 `server/tests/test_team_mode.py`（D1–D4：開關、邀請碼
         +、上限與並發加入、釋放與切換撤銷、同組並發送出、組員看得到送出 
         +、草稿規則與清除、組隊不改計分）                               
       5 +- [ ] 1.2 `server/tests/test_isolation.py` 新增組隊負例三則（D5
         +）                                                             
       6 +- [ ] 1.3 `eval/acceptance/matrix.yaml` M-017～M-019           
       7 +- [ ] 1.4 web：`web/src/pages/team.test.tsx`（D6）             
       8 +                                                               
       9 +## 2. 實作                                                     
      10 +- [ ] 2.1 `activity.py`：`team_play`、`set_team_play`、`join(te
         +am, code)`、邀請碼、`MAX_DEVICES`、`devices`、`drafts` 與清除  
      11 +- [ ] 2.2 `app.py`：`/api/teacher/team-play`、`/api/student/dra
         +ft`、join 本體 `code`、403；`views.py` D5 欄位；`contracts/api.
         +md`（D7）                                                      
      12 +- [ ] 2.3 web：老師組隊開關與台數／邀請碼、首頁邀請碼欄、學生頁
         +邀請碼與組內草稿                                               
      13 +                                                               
      14 +## 3. 驗證                                                     
      15 +- [ ] 3.1 `make gate` 原樣輸出、變異實錄、人工驗證步驟寫入 `ver
         +ification.md` 與 `docs/manual-verification.md` 場次 E          
      16 +- [ ] 3.2 `docs/parity.md` 狀態更新、`make gate-parity` 綠     

● Now registering the card in parity and writing the SpecKit side (spec + plan +
  diagrams). Checking SpecKit's format.

  Ran 3 shell commands (ctrl+o to expand)

● Writing the SpecKit 009 feature folder and three diagrams.

  Ran 1 shell command (ctrl+o to expand)

› Message from general-purpose
  一句話結論：沒有阻斷，有 2 個重要問題，都在人工驗證手冊：兩個步驟的預期畫面按
  現行程式根本做不出來，組員照做一定會誤報不符，A-1 被證偽。A-2 到 A-5
  我自己跑過，沒找到反例；A-6 從 repo 內無法驗證（見最後一段）。

  發現 1｜重要
    哪兒：docs/manual-verification.md:42（場次 A1 第 2 步）
    什麼錯：手冊說新開分頁再選第1組會看到「此組已有裝置加入」，但首頁在載入時就
  把已加入的組按鈕停用並顯示「第1組（已加入）」，按不下去，所以那句訊息不會出現
  。
    會怎樣：組員看不到這句訊息，會把 A1 打成不符。
    怎麼修：預期改成「第1組按鈕停用並顯示（已加入）」；或改成先開好首頁再讓另一
  分頁加入，然後才按。
    證據：git show ea58d35:web/src/pages/Home.tsx →
  `disabled={joined.includes(t)}`，`joined` 只在載入時取一次。

  發現 2｜重要
    哪兒：docs/manual-verification.md:96（場次 D 第 4 步）
    什麼錯：手冊說題目關閉後第2組送出會被拒；但題目一關，作答表單就從畫面上移除
  ，介面上沒有地方可以送出，這一步無法執行。
    會怎樣：組員做不出這一步，只能打不符或跳過。
    怎麼修：改成「第2組畫面已沒有輸入欄」；伺服器拒收這件事改引用探針紀錄
  probes/results/2026-11-12-timed-flow.txt，那裡有「關閉後送出 409」。
    證據：Student.tsx 的 TimedPanel 只在 `round?.state === "open"`
  時渲染作答表單。

  發現 3｜次要
    哪兒：manual-verification.md:68、:83、:97
    什麼錯：有三處預期寫錯或寫得不清楚：
    - 第 68 行：用連結匯入時，匯出檔名其實固定是「Google
  試算表-搶答結果.xlsx」，不是「<試算表名稱>-搶答結果.xlsx」（app.py:175 寫死
  `"Google 試算表.xlsx"`）。
    - 第 83 行：重置會保留模式，場次 B
  之後仍是「只計對錯」，「（經典搶答）」沒有寫明要把模式切回去。
    - 第 97 行：要拿到「+9xx 分」，必須在 2.01
  秒內答完一個兩格的題組（`(20010−ms)//20`），實際操作多半是 8xx。
    會怎樣：組員可能在這三處誤報不符。
    怎麼修：第 68 行改寫實際檔名；第 83 行寫明「模式選回經典搶答」；第 97
  行改成「+8xx–9xx 分」。

  發現 4｜次要
    哪兒：docs/product-trd.md:17；SpecKit 那邊 specs/006、007、008 的
  verification.md
    什麼錯：
    - TRD 寫「搶答結束前任何一組都看不到別組是否已送出」，但時間計分每題揭曉後公
  開的名次，等於透露了他組有沒有答對；這是負責人已批准的例外，這句卻沒提。
    - SpecKit 這三份 verification.md 仍引用
  `openspec/changes/<卡名>/verification.md`，三張卡歸檔後這些路徑已經不存在。
    會怎樣：新人讀 TRD 會被絕對化的說法誤導；從 SpecKit 點過去的連結是壞的。
    怎麼修：TRD 那句補上「時間計分已揭曉題的名次除外」；三份引用路徑改成
  `archive/2026-11-14-<卡名>`。

  外包檢查：A-6 只能確認五處文字確實寫了，無法確認負責人真的批了這五處。負責人
  2026-11-14 的原話不在 repo 裡，對話紀錄只到 2026-11-12。另外 phase2-review
  末段只記「第 1、2
  項批准」，而「學生端排行榜只公開名次」不在該段「呈負責人」三項之內；parity §5
  和 trd §6 卻把它寫成負責人確認，需要派單方拿原話來對。

  A-2 到 A-5 我跑了什麼：
  - A-3：歸檔三張卡的 MODIFIED、ADDED 標題在 openspec/specs
  各出現一次，沒有重複；game-modes 已是三種模式的版本。
  - A-4：對話紀錄裡 email 只命中 `@pytest`；權杖正則零命中；`teacher?key=`
  後面只有 `{key}`、`…`、`<老師金鑰>`。試算表 id 1PXXwWiBKJNpPkLR 在 dev
  已入庫，不是這輪新增。
  - A-5：六個共用檔兩 repo 的 sha1 相同；server/quiz_server、web/src、contracts
  兩 repo 的 tree 雜湊相同。

  我查閱的檔案：兩 repo 的 `git diff` 基線..team-handoff；ea58d35 版的
  manual-verification.md、product-trd.md、web/src/pages 六個檔與
  types.ts、api.ts、App.tsx，server/quiz_server 的
  activity.py、views.py、results.py、scoring.py、app.py；server/tests 的
  test_guided_notes_parse.py、test_judging.py；openspec/specs 與歸檔的
  delta；對話紀錄只做正則掃描。
  NOT CLEARED(0B/2M/2m)
● Agent "C-tier adversarial review docs PRs" finished · 4m 27s

  Ran 1 shell command (ctrl+o to expand)

● Review: 0 blocking, 2 important + 2 minor, all in the docs. Fixing on the
  handoff branch first (the SpecKit 009 heredoc failed to parse, so nothing was
  written — I'll redo it after).

  Ran 4 shell commands (ctrl+o to expand)
  ⎿  Resuming agent a046b9f

● Now writing the SpecKit 009 files with the Write tool.

  Ran 1 shell command (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\spec.md)
  ⎿  Wrote 85 lines to software_fin-speckit\specs\009-team-mode\spec.md
       1 # Feature Specification: 組隊模式——一組多台裝置、代表作答
       2 
       3 **Feature Branch**: `009-team-mode`
       4 **Created**: 2026-11-14
       5 **Status**: Draft（v1.0）
       6 **Input**: User description: "第三期做組隊模式"（負責人 2026-11-
         14）；TRD §6 裁定「代表作答：組內任一人送出即代表全組，其餘組員
         看得到組內草稿；不採分數平均」（2026-11-12）
       7 **需求編號**：X-04（`docs/trd-game-modes.md` M4）｜**parity**：`
         docs/parity.md` §4 `team-mode`｜**檔位**：S（作答隔離：新增送往
     … +79 lines (~3 KB) (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\research.md)
  ⎿  Wrote 38 lines to software_fin-speckit\specs\009-team-mode\research.md
       1 # Research: 009 team-mode
       2 
       3 知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，2
         026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論時
         間」，隊員分數平均；Quizlet Live 隨機分隊、每位隊員只看到部分選
         項。依 TRD §6 裁定只取「一隊多人、一人代表作答」。
       4 
       5 倉外行為探針：無。決策只依賴本倉既有的鎖、序號與依身分裁切的 vie
         w，不依賴第三方函式庫新行為、外部服務或瀏覽器新行為。
       6 
     … +32 lines (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\plan.md)
  ⎿  Wrote 52 lines to software_fin-speckit\specs\009-team-mode\plan.md
       1 # Implementation Plan: 組隊模式——一組多台裝置、代表作答
       2 
       3 **Branch**: `009-team-mode` | **Date**: 2026-11-14 | **Spec**: [
         spec.md](spec.md)
       4 **藍圖**：`diagrams/009-team-mode-{component,class,sequence}.pum
         l`
       5 
       6 ## Summary
       7 
       8 1. **組隊是與模式正交的活動設定**（`team_play`）／代價：與 TRD 
     … +45 lines (~2 KB) (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\data-model.md)
  ⎿  Wrote 13 lines to
     software_fin-speckit\specs\009-team-mode\data-model.md
       1 # Data Model: 009 team-mode
       2 
       3 對照 `diagrams/009-team-mode-class.puml`。
       4 
       5 | 實體 | 欄位 | 說明 |
       6 |---|---|---|
       7 | `Activity`（增） | `team_play: bool = False` | 只在 preparing 
         改；改變時撤銷憑證與邀請碼；重置保留 |
       8 | `Activity`（增） | `_codes: dict[組別, str]` | 6 碼邀請碼；第
         一台加入時產生；釋放、改組數、切換組隊時刪除 |
     … +5 lines (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\contracts\README.md)
  ⎿  Wrote 3 lines to
     software_fin-speckit\specs\009-team-mode\contracts\README.md
      1 # 009 team-mode 介面契約
      2 
      3 於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /a
        pi/teacher/team-play`（`{enabled}` ⇒ `{team_play}`；401／409 非 p
        reparing／422）、`POST /api/student/draft`（`{question, answers}`
         ⇒ `{question}`；403／404／409／422，見 research R4）；`POST /api
        /student/join` 本體 `{team, code?}`，增 403 邀請碼不正確、409 此
        組裝置已滿；`/api/public/info` 增 `team_play`；老師 view 增 `team
        _play`、`devices`、`invite_codes`；學生 view 增 `team_play`、`inv
        ite_code`、`drafts`。全部只增不改。

● Write(software_fin-speckit\specs\009-team-mode\tasks.md)
  ⎿  Wrote 33 lines to software_fin-speckit\specs\009-team-mode\tasks.md
       1 # Tasks: 組隊模式——一組多台裝置、代表作答
       2 
       3 **Input**: `specs/009-team-mode/` 與 `diagrams/009-team-mode-*.p
         uml`
       4 
       5 ## Phase 1: User Story 1 - 組隊開關與邀請碼加入 (P1) 🎯
       6 
       7 ### Tests
       8 
       9 - [ ] T001 [P] [US1] `server/tests/test_team_mode.py`：開關 409
     … +25 lines (~1 KB) (ctrl+o to expand)

› Message from general-purpose
  一句話結論：四處修正都已落到兩個新頂端（OpenSpec 7bcbba0、SpecKit
  8139937），沒有淨回歸，全部清除。
  - 發現 1 已改好：manual-verification.md 場次 A1 第 2
  步改成按鈕停用並顯示「（已加入）」，並註明首頁比第1組加入早開時才會看到 409
  訊息，與 Home.tsx 行為一致。
  - 發現 2 已改好：場次 D 第 4 步改成畫面已沒有輸入欄；引用的探針紀錄
  probes/results/2026-11-12-timed-flow.txt:13 確有「關閉後送出 409
  這一題目前沒有開放作答」；test_timed_mode.py 有截止後送出被拒（約第 79
  行）與關閉、送出並發（第 186 行）的測試，算是守到。
  - 發現 3 已改好：連結匯入的檔名改成固定「Google 試算表-搶答結果.xlsx」，與
  app.py:175 一致；場次 C 寫明模式要選回經典搶答；分數公式我驗算過，2 秒得
  900、3 秒得 850。
  - 發現 4 已改好：product-trd.md §2 補上時間計分名次的例外；SpecKit 006–008
  的三條歸檔路徑在 OpenSpec 7bcbba0 都存在，兩 repo 去掉 ai-logs 後 `git grep`
  舊路徑零命中。
  - 共用檔 product-trd.md、manual-verification.md、parity.md 兩 repo
  仍逐位元組相同；藥方 commit 只改了文件。
  我查閱的檔案：`git diff ea58d35 7bcbba0`、`git diff 7c50313
  8139937`、test_timed_mode.py、timed-flow.txt。
  CLEARED

● Agent "C-tier adversarial review docs PRs" finished · 37s
  ⎿  Loaded CLAUDE.md

● Docs cards are CLEARED after re-verification. Now the three PlantUML diagrams
  for 009.

● Write(software_fin-speckit\diagrams\009-team-mode-component.puml)
  ⎿  Wrote 26 lines to
     software_fin-speckit\diagrams\009-team-mode-component.puml
       1 @startuml 009-team-mode-component
       2 title 009 team-mode：組件圖
       3 
       4 package "web" {
       5   [TeamSettings\n組隊勾選（preparing）・台數・邀請碼] as TSet
       6   [Home\n邀請碼輸入欄] as Home
       7   [StudentPanel\n本組邀請碼] as SPanel
       8   [AnswerForm\n草稿 400 ms 送出・組內草稿「套用」] as Form
       9   [api.ts\nteacherPost(team-play)・joinTeam(team, code)・student
         Draft] as Api
     … +17 lines (ctrl+o to expand)

● Write(software_fin-speckit\diagrams\009-team-mode-class.puml)
  ⎿  Wrote 31 lines to
     software_fin-speckit\diagrams\009-team-mode-class.puml
       1 @startuml 009-team-mode-class
       2 title 009 team-mode：類別圖
       3 
       4 class Activity {
       5   + team_play : bool = False
       6   - _tokens : dict[str, str]  ' 憑證 → 組別，組隊時多對一
       7   - _codes : dict[str, str]  ' 組別 → 6 碼邀請碼
       8   + drafts : dict[str, dict[int, tuple[str, ...]]]
       9   + set_team_play(enabled)  ' 只在 preparing；值改變時撤銷憑證與
         邀請碼
     … +22 lines (ctrl+o to expand)

● Write(software_fin-speckit\diagrams\009-team-mode-sequence.puml)
  ⎿  Wrote 39 lines to
     software_fin-speckit\diagrams\009-team-mode-sequence.puml
       1 @startuml 009-team-mode-sequence
       2 title 009 team-mode：時序圖（組員加入、組內草稿、代表作答）
       3 
       4 actor "老師" as T
       5 actor "第1組 A 裝置" as A
       6 actor "第1組 B 裝置" as B
       7 actor "第2組" as C
       8 participant "app.py" as App
       9 participant "Activity" as Act
      10 participant "views" as V
     … +29 lines (ctrl+o to expand)

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-speckit; python -c "
      from pathlib import Path…)
  ⎿  20:class AnswerError <<ValueError>>  ' 沿用 003
     29:Activity ..> AnswerError : 422（草稿格式，訊息固定）
     INFO: Created user preferences directory.
     … +10 lines (ctrl+o to expand)
  ⎿  Updated software_fin-speckit\diagrams\009-team-mode-class.puml (+2 -2)
      17  
      18  class InviteCodeError <<Exception>>
      19  class TeamTakenError <<Exception>>
      20 -class DraftError <<ValueError>>                                
      20 +class AnswerError <<ValueError>>  ' 沿用 003                   
      21  
      22  class views_module <<module>> {
      23    + teacher_view(a)  ' team_play、devices、invite_codes
     ...
      26  
      27  Activity ..> InviteCodeError : 403
      28  Activity ..> TeamTakenError : 409（非組隊已有裝置／已滿）
      29 -Activity ..> DraftError : 422                                  
      29 +Activity ..> AnswerError : 422（草稿格式，訊息固定）           
      30  views_module ..> Activity
      31  @enduml
  ⎿  … 3 more files changed
  ⎿  (timeout 10m)

● Bash(cd /c/workspace/software_fin/software_fin-speckit; python -c "
      from pathlib import Path…)
  ⎿  uv run --group dev python ops/diagrams.py render .
     warning: `VIRTUAL_ENV=C:\workspace\linux2026_va2pa\.venv` does not mat
     ch the project environment path `.venv` and will be ignored; use `--ac
     … +10 lines (ctrl+o to expand)
  ⎿  Updated software_fin-speckit\diagrams\009-team-mode-class.puml (+1 -1)
      17  
      18  class InviteCodeError <<Exception>>
      19  class TeamTakenError <<Exception>>
      20 -class AnswerError <<ValueError>>  ' 沿用 003                   
      20 +class AnswerError <<ValueError>>                               
      21  
      22  class views_module <<module>> {
      23    + teacher_view(a)  ' team_play、devices、invite_codes
  ⎿  … 1 more file changed
  ⎿  (timeout 10m)

● Let me look at the rendered sequence diagram to make sure it reads correctly.

  Read 1 file, ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-speckit; python -c "
      from pathlib import Path…)
  ⎿  diagrams: 28 個圖檔已轉 PNG
     gate-diagrams: 28 個圖檔，0 處問題
  ⎿  Updated software_fin-speckit\diagrams\009-team-mode-sequence.puml (+3 
     -3)
      12  T -> App : POST /api/teacher/team-play {enabled: true}
      13  App -> Act : set_team_play(True)（preparing；撤銷所有憑證與邀請
          碼）
      14  A -> App : POST /api/student/join {team: 第1組}
      15 -App -> Act : join(第1組)：無裝置 ⇒ 發憑證、產生邀請碼          
      15 +App -> Act : join(第1組)：無裝置 → 發憑證、產生邀請碼          
      16  App --> A : {team, token}
      17  App -> V : student_view(第1組) 含 invite_code
      18  B -> App : POST /api/student/join {team: 第1組}（未帶碼）
     ...
      20  Act --> App : InviteCodeError
      21  App --> B : 403 邀請碼不正確
      22  B -> App : POST /api/student/join {team: 第1組, code}
      23 -App -> Act : join：compare_digest 相符、未滿 6 台 ⇒ 發憑證     
      23 +App -> Act : join：compare_digest 相符、未滿 6 台 → 發憑證     
      24  App --> B : {team, token}
      25  
      26  == 搶答中 ==
     ...
      29  App --> A : {question: 3}
      30  App -> V : 每條連線重算 view；只有第1組的 view 改變
      31  App --> B : 推播 drafts（第 3 題）
      32 -note right of C : 第2組 view 不變 ⇒ 不推送                     
      32 +note right of C : 第2組 view 不變 → 不推送                     
      33  B -> App : POST /api/student/submit {question: 3, answers}
      34  App -> Act : submit(第1組, 3)（同 003 的鎖與序號）；清第1組第 3
           題草稿
      35  App --> B : {question: 3, answers}
  ⎿  … 1 more file changed
  ⎿  (timeout 10m)

● Diagrams render cleanly. Now registering the card in parity (both repos) and
  committing the v1.0 proposals.
● Bash(cd /c/workspace/software_fin; python - <<'EOF'
      from pathlib import Path…)
  ⎿  04b77d3 docs(openspec): team-mode 提案 v1.0 [CORE]
     6865239 docs(specs): 009-team-mode 規格與圖表 v1.0 [CORE]
     gate-zh-hant: 0 處簡體字
     … +9 lines (ctrl+o to expand)
  ⎿  Updated software_fin-speckit\docs\parity.md (+2 -1)
      47  | `question-settings` | X-04 | 準備階段老師可把任一題設為**雙倍
          分數**（倍率 1 或 2），任何模式下該題得分 ×2；重新匯入即清除、
          重置活動保留；學生看得到哪些題是雙倍；分數欄名在全部倍率為 1 的
          經典搶答顯示「得題數」，其餘顯示「得分」（TRD T-05 倍率） | 已
          合入 | 已合入 |
      48  | `mode-buzz-fallback` | X-03、X-04 | 搶答＋錯誤遞補：最先送出
          者判錯則依順位遞補（TRD M1） | 未開 | 未開 |
      49  | `mode-timed-scoring` | X-04 | **時間計分**模式：老師逐題開放
          ，每題時限 5–120 秒（預設 20，準備階段設定），到時伺服器關閉該
          題、老師也可提早結束；只收開放中那一題；老師判定該題後揭曉；正
          確得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（以整數運算 `
          (2001 × T − 作答毫秒) // (2 × T)` 實作，避免浮點誤差）（t ≤ 0.5
           秒得滿分，t 為伺服器量得的作答秒數）；揭曉後學生看到本組該題對
          錯與得分、本組累積分數，以及全部組別的累積**名次**（不含他組分
          數，以免反推作答秒數）；他組答案、分數仍只在活動結束後才看得到
          （TRD M2、T-04、T-05 時限） | 已合入 | 已合入 |
      50 -| `team-mode` | X-04 | **組隊模式**：一組多台裝置，組內任一人送
         -出即代表全組（TRD M4，§6 裁定）；第三期 | 未開 | 未開 |        
      50 +| `team-mode` | X-04 | **組隊**（活動設定，可與任一模式搭配，只
         +在準備階段切換）：一組最多 6 台裝置，同組第二台起須輸入該組 6  
         +碼邀請碼（只顯示在本組與老師畫面）；組內任一人送出即代表全組， 
         +每組每題仍只送出一次；搶答中組員看得到本組草稿（不計分、不匯出 
         +，老師與他組看不到）；切換組隊、改組數、釋放某組都撤銷相關裝置 
         +（TRD M4，§6 裁定）；第三期 | 提案中 | 提案中 |                
      51  
      52  狀態值：未開／提案中／實作中／已實作（待合入）／已合入。
      53  
     ...
      66  | 2026-11-12 | 第二期三卡 | 提案輪評審（v1.1）：時間計分公式改
          以整數運算定義；學生端排行榜只公開名次（TRD §6 落實方式）；TRD 
          T-05 屬性名改為 `multiplier`、`time_limit` | 兩組 | 同一會話兩
          組同批修訂 |
      67  | 2026-11-12 | 第二期三卡 | 兩組皆合入 `dev`（OpenSpec #9–#11；
          SpecKit #8–#10），`dev` 上 server、web 逐字相同；人工驗證待補驗
           | 兩組 | 已確認 |
      68  | 2026-11-14 | 第二期三卡 | 負責人批准契約語意補充三處（經典得
          主得 1×倍率分、`team_scores` 欄名看 `score_label`；設定 API 兩
          欄位可選；時間計分在 `answering` 內判定），並確認兩處落實方式（
          學生端排行榜只公開名次；時間計分活動前不先發學習單） | 兩組（負
          責人裁定） | 已確認 |
      69 +| 2026-11-14 | `team-mode` | 負責人指示第三期做組隊；開卡 v1.0 
         +：組隊做成與模式正交的活動設定（非第四種模式），同組第二台起憑 
         +邀請碼加入，組內草稿只給本組 | 兩組（負責人指示） | 同一會話兩 
         +組同批起稿 |                                                   
  ⎿  Updated software_fin-speckit\docs\trd-game-modes.md (+2 -0)
      54  
      55  **排程（負責人 2026-11-12 裁）**：第二期做 `game-mode-framework
          ` → `question-settings` → `mode-timed-scoring` 三張；`mode-buzz
          -fallback`、`fair-ranking`、`team-mode` 列第三期，視 2026-11-30
           前的餘裕再開。
      56  
      57 +**範圍調整（2026-11-14）**：`team-mode` 做成與模式正交的活動設 
         +定（組隊開關），不是第四種模式——代表作答不改「誰能作答、何時鎖 
         +題、如何計分、何時揭曉」任何一項，做成模式就無法與時間計分等模 
         +式並用。                                                       
      58 +                                                               
      59  **範圍調整（2026-11-12）**：M3 從 `mode-timed-scoring` 移到 `ga
          me-mode-framework`——框架若沒有任何需判定的模式，判定階段只是無
          人使用的程式；時限從 `question-settings` 移到 `mode-timed-scori
          ng`——只有時間計分用得到。
      60  
      61  ## 6. 裁定
  ⎿  (timeout 5m)

● Proposals committed, gates green. Dispatching the proposal-round dual-channel
  review (red team + architecture) in parallel.

● 2 background agents launched (↓ to manage)
   ├ Red-team proposal review team-mode
   └ Architecture proposal review team-mode

● While the two reviewers run, updating the saved to-do memory so progress
  survives if the CLI closes.

● Write(~\.claude\projects\C--workspace\memory\software-fin-todo.md)
  ⎿  Error writing file

  Read 1 file (ctrl+o to expand)

● Write(~\.claude\projects\C--workspace\memory\software-fin-todo.md)
  ⎿  Added 8 lines, removed 12 lines
       1  ---
       2  name: software-fin-todo
       3 -description: Pending to-do list for software_fin after phase 2 
         -merged (2026-11-12) — remind the user at the start of the next 
         -session                                                        
       3 +description: Pending to-do list for software_fin (updated 2026-
         +11-14) — remind the user at the start of the next session      
       4  metadata:
       5 -  node_type: memory                                            
       5    type: project
       7 -  originSessionId: b7ad21d0-f75f-48d1-a643-28be6230e195        
       8 -  modified: 2026-11-12T15:41:24.419Z                           
       6  ---
       7  
      11 -User closed the CLI on 2026-11-12 and explicitly asked: "記起來
         -，下次要做的時候提醒我". At the next software_fin session, remi
         -nd them (in Traditional Chinese) of these open items before sta
         -rting other work:                                              
       8 +Updated 2026-11-14. Owner said on 2026-11-14: delete phase-2 br
         +anches, approve the five pending points, do phase 3 (team-mode)
         +, open a card that collects all manual verification for teammat
         +es, archive the rest, and add a product TRD for newcomers.     
       9  
      13 -1. **刪第二期分支**（整串已合完，先例允許；需使用者同意才刪）：
         -openspec `feat/game-mode-framework` `feat/question-settings` `f
         -eat/mode-timed-scoring`；speckit `006-game-mode-framework` `007
         --question-settings` `008-mode-timed-scoring`（本地＋遠端）。   
      14 -2. **使用者尚未明確批准**：契約語意補充三處（雙倍題得主得 1×倍 
         -率分／`team_scores` 欄名看 `score_label`；設定 API 兩欄位可選；
         -時間計分在 answering 內判定）；以及兩處與裁定字面不同（排行榜只
         -公開名次不公開他組分數；時間計分前不先發紙本學習單）。「合」只 
         -算合併批准。                                                   
      15 -3. **人工驗證 P-05**：第一期五卡＋第二期三卡皆未跑，步驟在各卡 
         -`verification.md`（openspec `openspec/changes/<name>/`、speckit
         - `specs/00N-*/`）。                                            
      16 -4. **`/export` 對話紀錄**：使用者 2026-11-12 已匯出到 `C:\works
         -pace\software_fin\2026-11-12-234033-hybridagentsoftwarefinp.txt
         -`（不在任一 repo 內）。待辦：先掃描個資／秘密（使用者 email、to
         -ken、路徑中的帳號名等）並遮蔽，再放進兩組 `docs/ai-logs/` 隨收 
         -尾 PR 提交。                                                   
      17 -5. **收尾 PR**（我做）：兩組 `docs/ops-log.md` 記第二期合併；`d
         -ocs/parity.md` 三卡「已實作（待合入）」改「已合入」；OpenSpec  
         -歸檔第二期三個 change（`openspec archive`）。                  
      18 -6. 可選：時間計分「開題時顯示題目文字」另立卡；第三期組隊模式（
         -代表作答，已裁定）。                                           
      10 +Done 2026-11-14: phase-2 branches deleted (local+remote via gh 
         +api); approvals recorded; OpenSpec phase-2 changes archived; AI
         + log 2026-11-12 added to docs/ai-logs.                         
      11  
      20 -Deadline 2026-11-30. Remove items from this file as they get do
         -ne; delete the file when empty. Related: [[software-fin-project
         -]]                                                             
      12 +Local stacked branches waiting for the owner to push with `!` (
         +pushing is agent-denied):                                      
      13 +- both repos: `docs/phase2-closeout` → `docs/team-handoff` (pro
         +duct-trd.md + manual-verification.md; C-tier review CLEARED aft
         +er one fix round)                                              
      14 +- OpenSpec `feat/team-mode`, SpecKit `009-team-mode` stacked on
         + docs/team-handoff: proposal v1.0 committed; proposal-round dua
         +l review dispatched, then implement → impl review → PRs.       
      15 +                                                               
      16 +Still open: manual verification P-05 (teammates use docs/manual
         +-verification.md; scene E added when team-mode lands); /export 
         +of the 2026-11-14 session into docs/ai-logs; optional card "sho
         +w question text in timed mode". Deadline 2026-11-30. Related: [
         +[software-fin-project]]                                        

● Meanwhile, starting acceptance tests (test-first) — reading existing
  concurrency test patterns.

  Ran 2 shell commands (ctrl+o to expand)

● Writing the acceptance tests (they'll fail until implementation lands).

● Write(software_fin-openspec\server\tests\test_team_mode.py)
  ⎿  Wrote 334 lines to
     software_fin-openspec\server\tests\test_team_mode.py
      1 """組隊：開關、邀請碼加入、代表作答、組內草稿（team-mode D1–D5）
        。"""
      2 import asyncio
      3 
      4 import pytest
      5 
      6 from quiz_server import results
      7 from quiz_server.activity import MAX_DEVICES, Activity, AlreadySu
        bmittedError, InviteCodeError, TeamTakenError
      8 from quiz_server.phases import PhaseError
     … +326 lines (ctrl+o to expand)
  ⎿  Loaded server\CLAUDE.md

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; cat >>
      server/tests/test_isolation.py <<'EOF'…)
  ⎿  ERROR tests/test_team_mode.py
     !!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!
     !!!!!!!!!
     1 error in 0.79s
  ⎿  Updated software_fin-openspec\server\tests\test_isolation.py (+73 -0)
      156              assert ref not in raw, (ref, raw[:200])
      157      teacher = client.get("/api/teacher/state", headers=teacher
           _headers).text
      158      assert "CPU" in teacher and "二進位" in teacher
      159 +                                                              
      160 +                                                              
      161 +# ---- 組隊（team-mode D5）：草稿與邀請碼只給本組 ----        
      162 +SECRET_DRAFT = "甲組草稿祕密"                                 
      163 +                                                              
      164 +                                                              
      165 +@pytest.fixture                                               
      166 +def team_play(loaded_client, teacher_headers):                
      167 +    c = loaded_client                                         
      168 +    assert c.post("/api/teacher/team-play", json={"enabled": T
          +rue}, headers=teacher_headers).status_code == 200             
      169 +    ta, tb = join(c, "第1組"), join(c, "第2組")               
      170 +    code_a = c.get("/api/teacher/state", headers=teacher_heade
          +rs).json()["invite_codes"]["第1組"]                           
      171 +    c.post("/api/teacher/start", headers=teacher_headers)     
      172 +    return c, ta, tb, code_a                                  
      173 +                                                              
      174 +                                                              
      175 +def draft(client, token: str, question: int, answers: list[str
          +]):                                                           
      176 +    return client.post("/api/student/draft", json={"question":
          + question, "answers": answers},                               
      177 +                       headers={"X-Team-Token": token})       
      178 +                                                              
      179 +                                                              
      180 +def test_team_draft_isolated(team_play, teacher_headers):     
      181 +    c, ta, tb, code_a = team_play                             
      182 +    seen = []                                                 
      183 +    with c.websocket_connect(f"/ws?role=student&token={tb}") a
          +s wb:                                                         
      184 +        seen.append(wb.receive_text())                        
      185 +        assert draft(c, ta, 3, [SECRET_DRAFT]).status_code == 
          +200                                                           
      186 +        # B 組自己的各種回應：成功、格式錯、已送出、憑證錯    
      187 +        seen.append(draft(c, tb, 3, ["乙組草稿"]).text)       
      188 +        seen.append(draft(c, tb, 1, [SECRET_DRAFT]).text)     
      189 +        seen.append(draft(c, "forged", 3, [SECRET_DRAFT]).text
          +)                                                             
      190 +        seen.append(wb.receive_text())  # B 自己的草稿改變 B  
          +的 view                                                       
      191 +        seen.append(submit(c, tb, 3, ["乙組答案"]).text)      
      192 +        seen.append(wb.receive_text())                        
      193 +        seen.append(c.get("/api/public/info").text)           
      194 +        seen.append(c.post("/api/student/join", json={"team": 
          +"第1組"}).text)  # 無碼加入 A 組被拒                          
      195 +    for raw in seen:                                          
     … 36 more lines (ctrl+o to expand)

● Tests are red as expected (missing symbols). Implementing the server side now.

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  345:    def own_submissions(self, team: str) -> list[Submission]:
  ⎿  Updated software_fin-openspec\server\quiz_server\activity.py (+87 -4)
      25      """該組已有裝置持有組別憑證；API 層轉成 409。"""
      26  
      27  
      28 +class InviteCodeError(Exception):                              
      29 +    """組隊時加入已有裝置的組別但邀請碼不符；API 層轉成 403（te
         +am-mode D2）。"""                                              
      30 +                                                               
      31 +                                                               
      32  class AlreadySubmittedError(Exception):
      33      """本組本題已送出，不可修改；API 層轉成 409。"""
      34  
     ...
      38  
      39  
      40  MULTIPLIERS = (1, 2)
      41 +MAX_DEVICES = 6  # 組隊時每組裝置上限（team-mode D2）          
      42 +CODE_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"  # 去掉易混 
         +淆的 I、O、0、1                                                
      43 +CODE_LENGTH = 6                                                
      44  TIME_LIMIT_RANGE = (5, 120)
      45  
      46  
     ...
       79      return tuple(cleaned)
       80  
       81  
       82 +def clean_draft(answers: list[str], expected: int) -> tuple[st
          +r, ...]:                                                      
       83 +    """草稿可空白（組員清掉）；其餘限制同送出，訊息固定不回顯 
          +（team-mode D4）。"""                                         
       84 +    if len(answers) != expected:                              
       85 +        raise AnswerError(f"此題有 {expected} 個子題")        
       86 +    cleaned = []                                              
       87 +    for a in answers:                                         
       88 +        if not isinstance(a, str):                            
       89 +            raise AnswerError("草稿格式不正確")               
       90 +        if len(a) > MAX_ANSWER_CHARS:                         
       91 +            raise AnswerError(f"每個答案最多 {MAX_ANSWER_CHARS
          +} 字")                                                        
       92 +        if any(unicodedata.category(ch) == "Cc" for ch in a): 
       93 +            raise AnswerError("答案含有不允許的控制字元")     
       94 +        cleaned.append(a)                                     
       95 +    return tuple(cleaned)                                     
       96 +                                                              
       97 +                                                              
       98 +def normalize_code(code: str | None) -> str:                  
       99 +    return "".join((code or "").split()).upper()              
     … 115 more lines (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  warning: `VIRTUAL_ENV=C:\workspace\linux2026_va2pa\.venv` does not mat
     ch the project environment path `.venv` and will be ignored; use `--ac
     tive` to target the active environment instead
     … +14 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\quiz_server\app.py (+39 -4)
      25  from pydantic import BaseModel
      26  
      27  from . import results
      28 -from .activity import Activity, AlreadySubmittedError, TeamTake
         -nError                                                         
      28 +from .activity import Activity, AlreadySubmittedError, InviteCo
         +deError, TeamTakenError                                        
      29  from .guided_notes import GuidedNotesError, write_answers
      30  from .phases import Phase, PhaseError
      31  from .sources import MAX_BYTES, SourceError, check_upload, down
          load_sheet
     ...
      44      team: str
      45  
      46  
      47 +class JoinBody(BaseModel):                                     
      48 +    team: str                                                  
      49 +    code: str | None = None  # 組隊時加入已有裝置的組別須帶邀請
         +碼（team-mode D2）                                             
      50 +                                                               
      51 +                                                               
      52 +class TeamPlayBody(BaseModel):                                 
      53 +    enabled: bool                                              
      54 +                                                               
      55 +                                                               
      56 +class DraftBody(BaseModel):                                    
      57 +    question: int                                              
      58 +    answers: list[str]                                         
      59 +                                                               
      60 +                                                               
      61  class UrlBody(BaseModel):
      62      url: str
      63  
     ...
      121      async def _conflict(_: Request, exc: Exception) -> JSONRes
           ponse:
      122          return JSONResponse({"detail": str(exc)}, status_code=
           409)
      123  
      124 +    @app.exception_handler(InviteCodeError)                   
      125 +    async def _bad_code(_: Request, exc: InviteCodeError) -> J
          +SONResponse:                                                  
      126 +        return JSONResponse({"detail": str(exc)}, status_code=
          +403)                                                          
      127 +                                                              
      128      @app.exception_handler(RequestValidationError)
      129      async def _invalid_body(_: Request, exc: RequestValidation
           Error) -> JSONResponse:
      130          # FastAPI 預設會把請求本體原樣放進錯誤回應；本體可能含
           答案，一律不回顯（作答隔離）
     ...
      145  
      146      @app.get("/api/public/info")
     … 35 more lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\quiz_server\views.py (+10 -0)
      46          "phase": a.phase.value,
      47          "teams": list(a.teams),
      48          "joined": a.joined_teams(),
      49 +        "team_play": a.team_play,                              
      50 +        "devices": {t: a.devices(t) for t in a.teams},         
      51 +        "invite_codes": {t: c for t in a.teams if (c := a.invit
         +e_code(t))},  # 老師看得到邀請碼，看不到草稿                   
      52          "source": a.source_name,
      53          "questions": question_outline(a),
      54          "mode": mode_info(a, teacher=True),
     ...
      78          "mode": mode_info(a, teacher=False),
      79          "round": round_view(a),
      80          "score_label": score_label(a),
      81 +        "team_play": a.team_play,                              
      82          # 只含本組；不含順位、序號與他組是否送出（buzz-answerin
          g D3）
      83          "my_submissions": [
      84              {"question": s.question, "answers": list(s.answers)
          } for s in a.own_submissions(team)
      85          ],
      86      }
      87 +    if a.team_play:                                            
      88 +        view["invite_code"] = a.invite_code(team)              
      89 +        # 組內草稿只在搶答中、只含本組（team-mode D5）；其餘階 
         +段不帶，fail-closed                                            
      90 +        if a.phase is Phase.ANSWERING:                         
      91 +            view["drafts"] = [{"question": n, "answers": list(a
         +ns)}                                                           
      92 +                              for n, ans in sorted(a.drafts.get
         +(team, {}).items())]                                           
      93      # 時間計分的例外（負責人 2026-11-12 裁定）：已揭曉題只給本
          組結果與各組名次，不給他組答案與分數
      94      if a.mode.sequential and a.phase is not Phase.ENDED:
      95          mine = results.own_revealed(a, team)

● All 36 pass. Making the timed-mode scoring comparison robust to wall-clock
  jitter, then running the full suite.

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  224 passed, 1 warning in 38.00s
     41 passed in 6.35s
      Test Files  6 passed (6)
     … +4 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\tests\test_team_mode.py (+6 -6)
      114          rows = results.build(a)
      115          if a._timer is not None:
      116              a._timer.cancel()
      117 -        # 作答毫秒取決於真實時鐘，計分以外的欄位不比          
      118 -        return ([[(r["team"], r["rank"], r["score"], r.get("co
          -rrect")) for r in q["ranking"]] for q in rows],               
      119 -                results.team_scores(a))                       
      117 +        # 時間計分的分數取決於真實時鐘的作答毫秒，只比順位與判
          +定；其餘模式連分數一起比                                      
      118 +        timed = key == "timed"                                
      119 +        return ([[(r["team"], r["rank"], None if timed else r[
          +"score"], r.get("correct"))                                   
      120 +                  for r in q["ranking"]] for q in rows],      
      121 +                None if timed else results.team_scores(a))    
      122  
      121 -    assert run(play(False))[1] == run(play(True))[1]          
      122 -    if key != "timed":                                        
      123 -        assert run(play(False)) == run(play(True))            
      123 +    assert run(play(False)) == run(play(True))                
      124  
      125  
      126  # ---- D2 邀請碼 ----
  ⎿  (another command ran in this repository at the same time; a change 
     made by either may show under either result)
  ⎿  (timeout 5m)

› Message from general-purpose
  一句話結論：有 2 個真問題，0 阻斷、1 重要、1
  次要。最重的是：老師把冒用者踢出去的唯一手段是釋放整組，但釋放後下一台加入時不
  需要邀請碼。冒用者只要搶先重新加入，就又佔住該組，新邀請碼還會顯示在他自己的畫
  面上。兩組規格寫的「舊邀請碼不能再用來加入」與設計本身矛盾。

  發現 1｜重要
    哪兒：OpenSpec design.md:19、:21 與 specs/team-mode/spec.md:21、:37；SpecKit
  spec.md:27、research.md:16
    什麼錯：釋放某組會刪掉該組邀請碼，讓該組回到「尚無裝置」的狀態。設計規定尚無
  裝置時加入不檢查邀請碼，所以釋放後任何人不帶碼、或帶舊碼，都能以「第一台」身分
  加入。規格驗收情境「舊邀請碼 MUST 不能再用來加入」在釋放後到有人重新加入之前一
  定不成立，這個情境無法照字面寫成測試。
    會怎樣：搶答中某組被別組學生冒用（例如看過組員螢幕上常駐顯示的邀請碼），老師
  釋放該組想把他踢掉。冒用者可以盯著公開資訊裡的已加入清單（`joined`），在該組消
  失的瞬間重新加入。他拿到新邀請碼，真組員反而被擋在 403
  外，冒用者還能代表該組先送出亂答。老師也不能只踢一台，只能整組重來再搶一次。

  怎麼修：釋放時立刻產生新邀請碼，只顯示在老師畫面，之後連第一台加入也要帶這個碼
  ；或者把規格情境改成「新組員須帶新碼」，並把「釋放後不需要碼的空窗」列為代價。
    證據：`git show 04b77d3:openspec/changes/team-mode/design.md | grep -n
  尚無裝置` → 19 行「該組尚無裝置：發憑證，並產生該組邀請碼」；21
  行「release(team)：…刪除邀請碼（下一台加入時重新產生）」；spec.md 37
  行「舊邀請碼 MUST 不能再用來加入」。

  發現 2｜次要
    哪兒：OpenSpec design.md:20；SpecKit research.md:16
    什麼錯：設計要求把輸入轉大寫、去空白後，直接用 `secrets.compare_digest`
  比對字串。這個函式遇到含非 ASCII 字元的字串會丟 TypeError。現有的 ValueError
  處理器接不到它，結果是 500 錯誤，而不是 403。轉大寫也不會把全形字母轉成半形。
    會怎樣：學生用注音輸入法，在全形狀態下打出「ＡＢＣ２３４」，加入時伺服器回
  500，前端只顯示「請求失敗（500）」。就算實作者照第一期 `team_of`
  的寫法先轉成位元組，正確的碼打成全形也永遠是 403，組員以為碼錯了。
    怎麼修：比對前先做全形轉半形的 Unicode
  正規化（NFKC），再轉大寫、轉成位元組比對；非 ASCII 一律回
  403，並加一則全形輸入的測試。
    證據：`python -c "import secrets;
  secrets.compare_digest('ABCDEF','ＡＢＣＤＥＦ')"` → `TypeError comparing
  strings with non-ASCII characters is not supported`；`'ａｂｃ'.upper()` →
  `ＡＢＣ`。

  外包檢查：
  - A-5 說「改組數清草稿」，稿內沒有落點：design D1 寫改組數「另清除邀請碼」，D4
  的清除清單也不含改組數。不過準備階段的草稿在重置時已經清空（D4
  寫明重置會清），所以不構成行為錯，只是斷言沒有落點。
  - A-2 的「足以擋住」是判斷，不是可證偽的判據；10⁹ 這個數字本身正確（32⁶ ≈
  1.07×10⁹）。

  其餘斷言我查過、沒找到能證偽的洞：
  - A-1：送出、計分、揭曉都只認組別，不認裝置。
  - A-3：「本組已送出」的檢查和序號都在同一把鎖內。
  - A-4：學生畫面裡沒有任何隨全域變動的欄位，例如全域版本號；WebSocket
  只在本連線畫面改變時才推送；老師畫面不含草稿；公開資訊只多一個 `team_play`。
  - A-6：格式錯誤的回應固定是「請求格式不正確」，不回顯本體。
  - 切換組隊與加入、加入第 6、7 台的並發都在鎖內。

  followup：
  - 草稿寫入的「本組尚未送出」檢查，稿內沒寫明要和送出在同一把鎖內做完（測試可補
  並發草稿＋送出的情境）。
  - 首頁只在載入時讀一次公開資訊，老師切換組隊後學生首頁不會更新。

  我查閱的檔案：
  - OpenSpec 04b77d3：openspec/changes/team-mode/{proposal,design,tasks}.md、spe
  cs/team-mode/spec.md、specs/activity-lifecycle/spec.md，以及
  docs/parity.md、docs/trd-game-modes.md 的差異。
  - SpecKit
  6865239：specs/009-team-mode/{spec,plan,research,data-model,tasks}.md、contrac
  ts/README.md、diagrams/009-team-mode-{component,class,sequence}.puml。
  - 基線 7bcbba0：server/quiz_server/{activity,views,app}.py、server/tests/test_
  isolation.py、web/src/pages/{Home,Student,AnswerForm}.tsx、web/src/api.ts。

  NOT CLEARED(0B/1M/1m)

● Agent "Red-team proposal review team-mode" finished · 3m 11s

● Red team: 0 blocking, 1 important (release lets anyone rejoin as "first
  device" without a code), 1 minor (full-width input → 500). Both are real;
  fixing in design and code. First, the lint error:

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  161:        for known, team in self._tokens.items():
     162:            if secrets.compare_digest(known.encode(), token.encode
     ()):
     … +10 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\quiz_server\activity.py (+19 -9)
       95      return tuple(cleaned)
       96  
       97  
       98 -def normalize_code(code: str | None) -> str:                  
       99 -    return "".join((code or "").split()).upper()              
       98 +def normalize_code(code: str | None) -> bytes:                
       99 +    """全形轉半形（NFKC）、去空白、轉大寫；比對一律用位元組， 
          +非 ASCII 只會比對失敗不會拋例外。"""                          
      100 +    return "".join(unicodedata.normalize("NFKC", code or "").s
          +plit()).upper().encode()                                      
      101  
      102  
      103  def team_names(n: int) -> list[str]:
     ...
      172      def invite_code(self, team: str) -> str | None:
      173          return self._codes.get(team)
      174  
      175 +    @staticmethod                                             
      176 +    def _new_code() -> str:                                   
      177 +        return "".join(secrets.choice(CODE_ALPHABET) for _ in 
          +range(CODE_LENGTH))                                           
      178 +                                                              
      179      def _revoke_all(self) -> None:
      180          self._tokens.clear()
      181          self._codes.clear()
     ...
      188              count = self.devices(team)
      189              if count and not self.team_play:
      190                  raise TeamTakenError("此組已有裝置加入，請老師
           釋放後再加入")
      186 -            if count:                                         
      187 -                # 先比對邀請碼再檢查上限：沒有正確邀請碼的人不
          -該知道該組有幾台（team-mode D2）                              
      188 -                given, known = normalize_code(code), self._cod
          -es.get(team, "")                                              
      189 -                if not known or not secrets.compare_digest(giv
          -en.encode(), known.encode()):                                 
      191 +            known = self._codes.get(team) if self.team_play el
          +se None                                                       
      192 +            if count and known is None:                       
      193 +                raise InviteCodeError("邀請碼不正確")  # 防禦 
          +：組隊時有裝置的組必有邀請碼                                  
      194 +            if known is not None:                             
      195 +                # 該組有邀請碼（已有裝置，或被老師釋放過）就必
          +須帶碼；先比對邀請碼再檢查上限：                              
      196 +                # 沒有正確邀請碼的人不該知道該組有幾台（team-m
          +ode v1.1 D2）                                                 
      197 +                if not secrets.compare_digest(normalize_code(c
          +ode), known.encode()):                                        
      198                      raise InviteCodeError("邀請碼不正確")
      199                  if count >= MAX_DEVICES:
      200                      raise TeamTakenError(f"此組裝置已滿（最多 
           {MAX_DEVICES} 台）")
      201              await self._checkpoint()  # 讓出點必須夾在「檢查」
           與「寫入」之間，拿掉鎖時並發測試才會紅
      202              token = secrets.token_urlsafe(16)
     … 18 more lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\tests\test_isolation.py (+2 -1)
      165  @pytest.fixture
      166  def team_play(loaded_client, teacher_headers):
      167      c = loaded_client
      168 -    assert c.post("/api/teacher/team-play", json={"enabled": T
          -rue}, headers=teacher_headers).status_code == 200             
      168 +    r = c.post("/api/teacher/team-play", json={"enabled": True
          +}, headers=teacher_headers)                                   
      169 +    assert r.status_code == 200                               
      170      ta, tb = join(c, "第1組"), join(c, "第2組")
      171      code_a = c.get("/api/teacher/state", headers=teacher_heade
           rs).json()["invite_codes"]["第1組"]
      172      c.post("/api/teacher/start", headers=teacher_headers)

● Updating tests to the v1.1 semantics (release → new teacher-only code
  required; full-width input accepted).

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  =========================== short test summary info ==================
     =========
     FAILED tests/test_team_mode.py::test_draft_cleared_on_release_and_rese
     … +5 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\tests\test_team_mode.py (+22 -8)
      199      c = loaded_client
      200      team_on(c, teacher_headers)
      201      tokens = [join(c, "第1組").json()["token"]]
      202 -    code = state(c, teacher_headers)["invite_codes"]["第1組"] 
      203 -    tokens += [join(c, "第1組", code).json()["token"] for _ in
          - range(2)]                                                    
      202 +    old = state(c, teacher_headers)["invite_codes"]["第1組"]  
      203 +    tokens += [join(c, "第1組", old).json()["token"] for _ in 
          +range(2)]                                                     
      204      assert c.post("/api/teacher/release", json={"team": "第1組
           "}, headers=teacher_headers).status_code == 200
      205      act = c.app.state.activity
      206      assert all(act.team_of(t) is None for t in tokens)
      207      s = state(c, teacher_headers)
      208 -    assert s["devices"]["第1組"] == 0 and "第1組" not in s["in
          -vite_codes"]                                                  
      209 -    assert "第1組" not in s["joined"]                         
      210 -    # 舊碼失效：下一台成為新的第一台並拿到新碼                
      211 -    assert join(c, "第1組", code).status_code == 200          
      212 -    new = state(c, teacher_headers)["invite_codes"]["第1組"]  
      213 -    assert join(c, "第1組", code).status_code == 403 or new ==
          - code                                                         
      208 +    assert s["devices"]["第1組"] == 0 and "第1組" not in s["jo
          +ined"]                                                        
      209 +    new = s["invite_codes"]["第1組"]  # 釋放即換新碼，只在老師
          +畫面                                                          
      210 +    assert new != old or len(new) == 6                        
      211 +    # 被踢的人不能搶先以「第一台」重新佔住：不帶碼、帶舊碼都 4
          +03                                                            
      212 +    assert join(c, "第1組").status_code == 403                
      213 +    if new != old:                                            
      214 +        assert join(c, "第1組", old).status_code == 403       
      215 +    assert join(c, "第1組", new).status_code == 200           
      216 +    assert state(c, teacher_headers)["invite_codes"]["第1組"] 
          +== new                                                        
      217 +                                                              
      218 +                                                              
      219 +def test_fullwidth_code_accepted(loaded_client, teacher_header
          +s):                                                           
      220 +    c = loaded_client                                         
      221 +    team_on(c, teacher_headers)                               
      222 +    join(c, "第1組")                                          
      223 +    code = state(c, teacher_headers)["invite_codes"]["第1組"] 
      224 +    wide = "".join(chr(ord(ch) + 0xFEE0) for ch in code)  # 半
          +形轉全形                                                      
      225 +    assert join(c, "第1組", wide).status_code == 200          
      226 +    r = join(c, "第1組", "邀請碼錯")                          
      227 +    assert r.status_code == 403                               
      228  
      229  
      230  # ---- D3 代表作答 ----

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  37 passed, 1 warning in 4.91s
     All checks passed!
  ⎿  Updated software_fin-openspec\server\quiz_server\activity.py (+2 -1)
      211              if team not in self.teams:
      212                  raise KeyError(team)
      213              self._tokens = {k: v for k, v in self._tokens.item
           s() if v != team}
      214 -            # 組隊時釋放即換新碼（只顯示在老師畫面）：被踢的冒
          -用者不能搶先以「第一台」重新佔住該組（team-mode v1.1 D2）     
      214 +            # 組隊時釋放即換新碼（只顯示在老師畫面）：被踢的冒
          +用者不能搶先以「第一台」                                      
      215 +            # 重新佔住該組（team-mode v1.1 D2）               
      216              if self.team_play:
      217                  self._codes[team] = self._new_code()
      218              self.drafts.pop(team, None)
  ⎿  Updated software_fin-openspec\server\tests\test_team_mode.py (+1 -1)
      310      assert act.drafts.get("第1組")
      311      c.post("/api/teacher/release", json={"team": "第1組"}, hea
           ders=teacher_headers)
      312      assert not act.drafts.get("第1組")
      313 -    ta = join(c, "第1組").json()["token"]                     
      313 +    ta = join(c, "第1組", state(c, teacher_headers)["invite_co
          +des"]["第1組"]).json()["token"]                               
      314      draft(c, ta, 3, ["草稿"])
      315      c.post("/api/teacher/end", headers=teacher_headers)
      316      c.post("/api/teacher/reset", headers=teacher_headers)
  ⎿  (another command ran in this repository at the same time; a change 
     made by either may show under either result)

● Server green (37 team/isolation tests, lint clean). Now the web side while the
  architecture reviewer finishes.

  Ran 1 shell command (ctrl+o to expand)
● Write(software_fin-openspec\web\src\pages\team.test.tsx)
  ⎿  Wrote 110 lines to software_fin-openspec\web\src\pages\team.test.tsx
       1 import { act, fireEvent, render, screen } from "@testing-library
         /react";
       2 import { vi } from "vitest";
       3 import { TeamPicker } from "./Home";
       4 import { TeacherPanel } from "./Teacher";
       5 import { StudentPanel } from "./Student";
       6 import { AnswerForm } from "./AnswerForm";
       7 import type { StudentView, TeacherView } from "../types";
       8 
       9 const teacher: TeacherView = {
     … +101 lines (ctrl+o to expand)
  ⎿  Loaded ..\CLAUDE.md

● Now the web implementation (types, api, Home, Teacher, Student, AnswerForm).

● Bash(cd /c/workspace/software_fin/software_fin-openspec/web/src; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  ok
  ⎿  Updated software_fin-openspec\web\src\api.ts (+17 -4)
      62    URL.revokeObjectURL(url);
      63  }
      64  
      65 -export async function publicInfo(): Promise<{ phase: string; te
         -ams: string[]; joined: string[] }> {                           
      66 -  return (await parse(await fetch("/api/public/info"))) as { ph
         -ase: string; teams: string[]; joined: string[] };              
      65 +export interface PublicInfo {                                  
      66 +  phase: string;                                               
      67 +  teams: string[];                                             
      68 +  joined: string[];                                            
      69 +  team_play?: boolean;                                         
      70  }
      71  
      69 -export async function joinTeam(team: string): Promise<{ team: s
         -tring; token: string }> {                                      
      70 -  return (await parse(await fetch("/api/student/join", jsonInit
         -({}, { team })))) as { team: string; token: string };          
      72 +export async function publicInfo(): Promise<PublicInfo> {      
      73 +  return (await parse(await fetch("/api/public/info"))) as Publ
         +icInfo;                                                        
      74 +}                                                              
      75 +                                                               
      76 +// 組隊時加入已有組員的組別要帶邀請碼（team-mode D2）          
      77 +export async function joinTeam(team: string, code?: string): Pr
         +omise<{ team: string; token: string }> {                       
      78 +  const body = code ? { team, code } : { team };               
      79 +  return (await parse(await fetch("/api/student/join", jsonInit
         +({}, body)))) as { team: string; token: string };              
      80 +}                                                              
      81 +                                                               
      82 +export async function studentDraft(token: string, question: num
         +ber, answers: string[]): Promise<unknown> {                    
      83 +  return parse(await fetch("/api/student/draft", jsonInit({ "X-
         +Team-Token": token }, { question, answers })));                
      84  }
      85  
      86  // 組別憑證只放 sessionStorage：同分頁重新整理不必重新加入，關
          閉分頁即失效（app-skeleton D6）
  ⎿  Updated software_fin-openspec\web\src\types.ts (+11 -0)
      45    pending_judgments?: number;
      46    round?: RoundInfo | null;
      47    leaderboard?: LeaderRow[];
      48 +  team_play?: boolean; // team-mode：組隊開關                  
      49 +  devices?: Record<string, number>;                            
      50 +  invite_codes?: Record<string, string>;                       
      51 +}                                                              
      52 +                                                               
      53 +export interface Draft {                                       
      54 +  question: number;                                            
      55 +  answers: string[];                                           
      56  }
      57  
      58  export interface StudentView {
     ...
      70    revealed?: { question: number; submitted: boolean; correct: b
          oolean | null; score: number }[];
      71    my_total?: number;
      72    leaderboard?: LeaderRow[];
      73 +  team_play?: boolean;                                         
      74 +  invite_code?: string | null; // 只有本組                     
      75 +  drafts?: Draft[]; // 組內草稿：只在搶答中、只含本組          
      76  }
      77  
      78  export interface RankedAnswer {

● Write(software_fin-openspec\web\src\pages\Home.tsx)
  ⎿  Added 39 lines, removed 11 lines
       1  import { useEffect, useState } from "react";
       2  import { joinTeam, publicInfo, saveToken } from "../api";
       3  
       4 +// 選組：組隊時已加入的組別仍可按，第二台起要輸入該組邀請碼（te
         +am-mode D6）                                                   
       5 +export function TeamPicker({                                   
       6 +  teams,                                                       
       7 +  joined,                                                      
       8 +  teamPlay,                                                    
       9 +  onPick,                                                      
      10 +}: {                                                           
      11 +  teams: string[];                                             
      12 +  joined: string[];                                            
      13 +  teamPlay: boolean;                                           
      14 +  onPick: (team: string, code: string) => void;                
      15 +}) {                                                           
      16 +  const [code, setCode] = useState("");                        
      17 +  return (                                                     
      18 +    <>                                                         
      19 +      <p>{teamPlay ? "選擇你的組別（組隊：同組可多台裝置，加入 
         +已有組員的組別要輸入邀請碼）：" : "選擇你的組別（每組一台裝置）
         +："}</p>                                                       
      20 +      {teamPlay && (                                           
      21 +        <label>                                                
      22 +          邀請碼（向組員或老師索取）                           
      23 +          <input value={code} onChange={(e) => setCode(e.target
         +.value)} aria-label="邀請碼" maxLength={12} />                 
      24 +        </label>                                               
      25 +      )}                                                       
      26 +      <div className="team-grid">                              
      27 +        {teams.map((t) => (                                    
      28 +          <button key={t} disabled={!teamPlay && joined.include
         +s(t)} onClick={() => onPick(t, code)}>                         
      29 +            {t}                                                
      30 +            {joined.includes(t) && "（已加入）"}               
      31 +          </button>                                            
      32 +        ))}                                                    
      33 +      </div>                                                   
      34 +    </>                                                        
      35 +  );                                                           
      36 +}                                                              
      37 +                                                               
      38  // 首頁：學生選組別取得組別憑證；老師輸入金鑰進場（app-skeleton
           spec「系統必須區分老師與學生兩種身分」）
      39  export default function Home() {
      40    const [teams, setTeams] = useState<string[]>([]);
      41    const [joined, setJoined] = useState<string[]>([]);
      42 +  const [teamPlay, setTeamPlay] = useState(false);             
      43    const [key, setKey] = useState("");
      44    const [error, setError] = useState("");
      45    useEffect(() => {
     ...
      47        .then((i) => {
      48          setTeams(i.teams);
      49          setJoined(i.joined);
      50 +        setTeamPlay(!!i.team_play);                            
      51        })
      52        .catch(() => setError("連不上伺服器"));
      53    }, []);
      18 -  const pick = (team: string) => {                             
      54 +  const pick = (team: string, code: string) => {               
      55      setError("");
      20 -    joinTeam(team)                                             
      56 +    joinTeam(team, code.trim() || undefined)                   
      57        .then((r) => {
      58          saveToken(r.token);
      59          location.hash = "#/student";
     ...
      66        {error && <p className="error">{error}</p>}
      67        <section className="card">
      68          <h2>我是學生</h2>
      33 -        <p>選擇你的組別（每組一台裝置）：</p>                  
      34 -        <div className="team-grid">                            
      35 -          {teams.map((t) => (                                  
      36 -            <button key={t} disabled={joined.includes(t)} onCli
         -ck={() => pick(t)}>                                            
      37 -              {t}                                              
      38 -              {joined.includes(t) && "（已加入）"}             
      39 -            </button>                                          
      40 -          ))}                                                  
      41 -        </div>                                                 
      69 +        <TeamPicker teams={teams} joined={joined} teamPlay={tea
         +mPlay} onPick={pick} />                                        
      70        </section>
      71        <section className="card">
      72          <h2>我是老師</h2>

› Message from general-purpose
  一句話結論：沒有阻斷項，有 2 個重要、2 個次要。最重的一個：邀請碼在整場活動中
  都常駐顯示在組員螢幕上，而且搶答中也能加入。他組學生只要瞄到這 6
  碼，就能在搶答中加入第1組，即時讀到該組草稿並代該組送出。這正是提案摘要第 2
  條自稱要擋的冒用。

  發現 1｜重要
    哪兒：openspec design.md:43（D5，學生 view 的 invite_code
  不分階段）、design.md:55（D6，學生頁常駐顯示「本組邀請碼」）；speckit
  research.md:32、37；現行 server/quiz_server/activity.py:138-148（join
  不檢查階段）
    什麼錯：學生 view 在任何階段都帶本組邀請碼，學生頁也一直顯示，加入又不限階段
  ，所以搶答中任何看過那 6 碼的人都能加入該組。
    會怎樣：教室裡各組座位相鄰。第2組的人看一眼第1組的手機，就能在搶答中帶碼加入
  第1組，即時收到第1組的組內草稿（這是作答洩漏），還能搶先替第1組送出錯答案，而
  該組每題只能送一次。邀請碼這道防線在最需要的時段形同虛設。
    怎麼修：學生 view 只在 preparing 帶 invite_code（學生頁同步只在準備階段顯示
  ），搶答中改由老師畫面提供；或者規定非第一台裝置只能在 preparing
  加入。兩組要同批修，並補一則「搶答中學生 view 不含 invite_code」的負例。
    證據：git show 04b77d3:openspec/changes/team-mode/design.md 第 43、55
  行沒有階段限制；git show 04b77d3:server/quiz_server/activity.py 第 138-148
  行，join 沒有 _require。

  發現 2｜重要
    哪兒：design.md:61（D7 寫「全部是新增，既有欄位語意不變」）；speckit
  contracts/README.md:3（「全部只增不改」）；contracts/api.md:3、11、28、32；doc
  s/product-trd.md:23
    什麼錯：提案自己的檔位行（proposal.md:3）承認「組別憑證口徑改變」，但 D7
  和契約 README 把它說成純新增，也沒列出要改契約的哪幾行。這幾行是：身分表「一組
  一台裝置」、join 的 409
  在組隊時改指「已滿」、release「撤銷該組憑證」改為撤銷全部台數。product-trd 第
  23 行「每組一台裝置」也沒在 tasks 裡。
    會怎樣：照 D7 實作的人只會加新列，契約（凍結件，兩組共用）留著「一組一台裝置
  」，和伺服器實際行為相反。契約檔頭規定改語意要經負責人批准；這次是被標成「新增
  」而繞過了批准，對照 parity 歷史 2026-11-14 那筆語意補充有過負責人批准。
    怎麼修：D7 和 contracts/README.md 逐條列出上述語意補充，tasks
  加上改契約身分表與 product-trd 第 23
  行，並把這幾條語意補充列入「未決呈裁」交負責人批准。
    證據：git show 04b77d3:contracts/api.md 第 3
  行「改語意須經規格變更與負責人批准」；第 11 行「（一組一台裝置）」。

  發現 3｜次要
    哪兒：design.md:20（D2）；speckit research.md:16
    什麼錯：設計寫「轉大寫、去空白後用 secrets.compare_digest 比對
  str」。只要輸入含非 ASCII 字元，這個函式就拋 TypeError；TypeError 不屬於
  ValueError，現有錯誤處理接不住，結果回 500。
    會怎樣：學生用注音或全形輸入法打邀請碼（台灣很常見），首頁顯示「請求失敗（50
  0）」，而不是 403「邀請碼不正確」。這也違反契約「錯誤一律為中文 detail」。
    怎麼修：先比對格式（只接受字母表裡的 6 個字），格式不符直接 403；或照現行
  team_of 的寫法 .encode() 後再比對。
    證據：python -c "import
  secrets;secrets.compare_digest('ABC234','ＡＢＣ２３４'.upper())" → TypeError:
  comparing strings with non-ASCII characters is not supported

  發現 4｜次要
    哪兒：design.md:22（devices＝憑證數）、design.md:21（release
  只能整組釋放）；speckit spec.md:25-27
    什麼錯：憑證存在
  sessionStorage，關分頁就丟了，但伺服器上的憑證還在，照樣佔上限 6
  台的名額。老師畫面的「n
  台」數的是憑證，不是在線裝置；而且只能整組釋放，不能單獨釋放一台。
    會怎樣：一組 6 人時，只要有一人關掉分頁再重開，就會被
  409「已滿」擋住。老師唯一的辦法是在搶答中釋放整組，全組被踢掉、草稿清空，還要
  用新產生的邀請碼重新加入。
    怎麼修：台數改算在線連線數，或者老師可以單獨釋放某一台；至少在 design
  明寫這是取捨並說明理由。
    證據：git show 04b77d3:web/src/api.ts 第 73-90 行（憑證只放
  sessionStorage）。

  followup（判據不夠嚴或覆蓋窄，都不擋本輪）：
  - D4 沒寫 set_draft 要在鎖內、檢查與寫入之間要有讓出點，也沒有「草稿與送出並發
  」的測試。依模組慣例應該是隱含的，但判據沒有落到稿上。
  - 前端草稿防抖 400 毫秒，送出後計時器才觸發會收到 409。D6
  沒規定草稿錯誤要靜默或在送出時取消計時器，送出的人可能看到一句假錯誤。
  - 每次草稿更新都會讓所有連線（含老師 board）重算一次
  view，負載量級沒有探針，design 卻寫「倉外行為探針：無」。
  - 邀請碼不得寫進日誌沒有判據：D4 只規定草稿不記日誌。
  - 老師 view 的 devices 與 invite_codes
  在組隊關閉時鍵存不存在，兩組都沒寫；OpenSpec 寫「只含已有裝置的組」，SpecKit
  沒寫。草稿 409 的訊息文字只有 OpenSpec 有。
  - D3 寫「submit
  不改」，同一段又要送出後清除草稿，類別圖也是同樣寫法，字面上自相矛盾。

  外包檢查：
  - A-4 的「已自對碼＝由同一稿改寫」不是核對證據，等於把一致性核對外包給評審員。
  - A-5 說矩陣 M-017～M-019 與測試名稱一一對應，但 proposal、tasks、SpecKit plan
  都沒給出哪一行由哪個測試守，這項斷言在稿內沒有落點。新增矩陣行留到實作時做，
  與前三卡的先例一致，所以不另記發現。
  - A-1 和 A-3 我核了，成立：Mode 介面不必改；MODIFIED
  的需求標題與原文一致，其餘情境照原文；buzz-answering
  的隔離需求只管他組，不必改。

  我查閱的檔案：.claude/agents/finder-tail-arch.md；OpenSpec 04b77d3 的 openspec
  /changes/team-mode/{proposal,design,tasks}.md、specs/{team-mode,activity-lifec
  ycle}/spec.md、openspec/specs/{activity-lifecycle,buzz-answering}/spec.md、con
  tracts/api.md、docs/{trd-game-modes,parity,requirements,product-trd,discipline
  -precedents,manual-verification}.md、eval/acceptance/matrix.yaml、server/quiz_
  server/{activity,views,app}.py、web/src/{api.ts,pages/Home.tsx}、server/tests
  定點 grep；SpecKit 6865239 的
  specs/009-team-mode/{spec,plan,research,data-model,tasks}.md、contracts/README
  .md、diagrams/009-team-mode-{component,class,sequence}.puml；兩邊共用檔 diff
  結果是逐字相同。
  NOT CLEARED(0B/2M/2m)

● Agent "Architecture proposal review team-mode" finished · 4m 50s

● The architecture review found no blocking issues and two important ones, which
  I'm folding into v1.1 alongside the red team's findings: students see the
  invite code only during preparing, codes rotate when answering starts, and the
  identity, join and release wording changes need the owner's approval. I'm
  finishing the web code first and then applying these. · summary

● Bash(cd /c/workspace/software_fin/software_fin-openspec/web/src; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  ok
  ⎿  Updated software_fin-openspec\web\src\pages\Student.tsx (+46 -8)
       1 -import { studentSubmit } from "../api";                        
       1 +import { studentDraft, studentSubmit } from "../api";          
       2  import { useLiveView } from "../live";
       3  import { PHASE_LABEL, type StudentView } from "../types";
       4 -import { AnswerForm, type Submit } from "./AnswerForm";        
       4 +import { AnswerForm, type Draft, type Submit } from "./AnswerFo
         +rm";                                                           
       5  import { QuestionList } from "./ImportPanel";
       6  import { StudentResults } from "./Results";
       7  import { MODE_HINT } from "./Teacher";
       8  import { Leaderboard, RoundStatus } from "./Round";
       9  
      10 -export function StudentPanel({ view, onSubmit = async () => {} 
         -}: { view: StudentView; onSubmit?: Submit }) {                 
      10 +export function StudentPanel({                                 
      11 +  view,                                                        
      12 +  onSubmit = async () => {},                                   
      13 +  onDraft,                                                     
      14 +}: {                                                           
      15 +  view: StudentView;                                           
      16 +  onSubmit?: Submit;                                           
      17 +  onDraft?: Draft;                                             
      18 +}) {                                                           
      19    if (!view.team_valid)
      20      return (
      21        <p className="error">
     ...
      33          <p className="phase">
      34            目前階段：<strong>{PHASE_LABEL[view.phase]}</strong>
      35          </p>
      36 +        {view.team_play && (                                   
      37 +          <p className="muted">                                
      38 +            組隊：組內任一人送出即代表全組，每題只能送出一次。 
      39 +            {view.invite_code ? (                              
      40 +              <>                                               
      41 +                {" "}本組邀請碼：<strong>{view.invite_code}</st
         +rong>（給組員加入用）                                          
      42 +              </>                                              
      43 +            ) : (                                              
      44 +              " 開始搶答後邀請碼會換新，組員要加入請向老師索取 
         +。"                                                            
      45 +            )}                                                 
      46 +          </p>                                                 
      47 +        )}                                                     
      48          {view.mode && (
     … 58 more lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\web\src\pages\Teacher.tsx (+26 -1)
      124    return (
      125      <section className="card">
      126        <h2>組別</h2>
      127 +      <label>                                                 
      128 +        <input                                                
      129 +          type="checkbox"                                     
      130 +          checked={!!view.team_play}                          
      131 +          disabled={view.phase !== "preparing"}               
      132 +          onChange={(e) => act("team-play", { enabled: e.targe
          +t.checked })}                                                 
      133 +          aria-label="組隊（一組多台裝置）"                   
      134 +        />                                                    
      135 +        組隊（一組多台裝置）                                  
      136 +      </label>                                                
      137 +      {view.team_play && (                                    
      138 +        <p className="muted">                                 
      139 +          同組第二台起要輸入該組邀請碼；開始搶答時邀請碼會換新
          +，搶答中要加入的組員請向老師索取。切換組隊會讓所有裝置重新加入
          +。                                                            
      140 +        </p>                                                  
      141 +      )}                                                      
      142        <ul className="team-list">
      143          {view.teams.map((t) => (
      144            <li key={t}>
      130 -            {t}：{view.joined.includes(t) ? "已加入" : <span c
          -lassName="muted">未加入</span>}                               
      145 +            {t}：                                             
      146 +            {view.joined.includes(t) ? (                      
      147 +              view.team_play ? `已加入（${view.devices?.[t] ??
          + 0} 台）` : "已加入"                                          
      148 +            ) : (                                             
      149 +              <span className="muted">未加入</span>           
      150 +            )}                                                
      151 +            {view.team_play && view.invite_codes?.[t] && (    
      152 +              <>                                              
      153 +                {" "}邀請碼 <code>{view.invite_codes[t]}</code
          +>                                                             
      154 +              </>                                             
      155 +            )}                                                
      156              {view.joined.includes(t) && (
      157                <button className="small" onClick={() => act("re
           lease", { team: t })}>
      158                  釋放

● Write(software_fin-openspec\web\src\pages\AnswerForm.tsx)
  ⎿  Added 48 lines, removed 4 lines
       1 -import { useState } from "react";                              
       2 -import type { QuestionOutline } from "../types";               
       1 +import { useEffect, useRef, useState } from "react";           
       2 +import type { Draft as DraftRow, QuestionOutline } from "../typ
         +es";                                                           
       3  import { DoubleTag } from "./ImportPanel";
       4  
       5  export type Submit = (question: number, answers: string[]) => P
          romise<unknown>;
       6 +export type Draft = (question: number, answers: string[]) => vo
         +id;                                                            
       7  
       8 +const DRAFT_DELAY_MS = 400;                                    
       9 +                                                               
      10  // 學生作答：題組一次送出全部子題；送出後鎖定（buzz-answering D
          1、D4）。
      11  // 畫面只顯示本組資料，伺服器在搶答結束前不會送任何他組資訊。
      12 +// 組隊時（onDraft 有值）輸入會防抖送出組內草稿，並顯示伺服器推
         +來的本組草稿（team-mode D6）。                                 
      13  export function AnswerForm({
      14    questions,
      15    submitted,
      16    onSubmit,
      17 +  drafts,                                                      
      18 +  onDraft,                                                     
      19  }: {
      20    questions: QuestionOutline[];
      21    submitted: { question: number; answers: string[] }[];
      22    onSubmit: Submit;
      23 +  drafts?: DraftRow[];                                         
      24 +  onDraft?: Draft;                                             
      25  }) {
      26    return (
      27      <div>
      28        {questions.map((q) => {
      29          const mine = submitted.find((s) => s.question === q.num
          ber);
      30          return (
      23 -          <QuestionCard key={q.number} question={q} submitted={
         -mine?.answers} onSubmit={onSubmit} />                          
      31 +          <QuestionCard                                        
      32 +            key={q.number}                                     
      33 +            question={q}                                       
      34 +            submitted={mine?.answers}                          
      35 +            onSubmit={onSubmit}                                
      36 +            teamDraft={drafts?.find((d) => d.question === q.num
         +ber)?.answers}                                                 
      37 +            onDraft={onDraft}                                  
      38 +          />                                                   
      39          );
      40        })}
      41      </div>
     ...
      46    question,
      47    submitted,
      48    onSubmit,
      49 +  teamDraft,                                                   
      50 +  onDraft,                                                     
      51  }: {
      52    question: QuestionOutline;
      53    submitted?: string[];
      54    onSubmit: Submit;
      55 +  teamDraft?: string[];                                        
      56 +  onDraft?: Draft;                                             
      57  }) {
      58    const [values, setValues] = useState<string[]>(() => question
          .labels.map(() => ""));
      59    const [error, setError] = useState("");
      60    const [busy, setBusy] = useState(false);
      61 +  const timer = useRef<ReturnType<typeof setTimeout> | null>(nu
         +ll);                                                           
      62 +  const cancelDraft = () => {                                  
      63 +    if (timer.current) clearTimeout(timer.current);            
      64 +    timer.current = null;                                      
      65 +  };                                                           
      66 +  useEffect(() => cancelDraft, []);                            
      67    const ready = values.every((v) => v.trim() !== "");
      68 +  const change = (next: string[]) => {                         
      69 +    setValues(next);                                           
      70 +    if (!onDraft) return;                                      
      71 +    cancelDraft();                                             
      72 +    timer.current = setTimeout(() => {                         
      73 +      timer.current = null;                                    
      74 +      onDraft(question.number, next);                          
      75 +    }, DRAFT_DELAY_MS);                                        
      76 +  };                                                           
      77    const send = () => {
      78 +    cancelDraft(); // 送出後不再補送草稿                       
      79      setBusy(true);
      80      setError("");
      81      onSubmit(question.number, values)
      82        .catch((e: Error) => setError(e.message))
      83        .finally(() => setBusy(false));
      84    };
      85 +  const showDraft = onDraft && teamDraft && teamDraft.some((v) 
         +=> v !== "") && teamDraft.join("\u0000") !== values.join("\u000
         +0");                                                           
      86    return (
      87      <section className="card">
      88        <h3>
     ...
      102                  aria-label={`第 ${question.number} 題 ${label 
           || "答案"}`}
      103                  value={values[i]}
      104                  maxLength={200}
       69 -                onChange={(e) => setValues(values.map((v, j) =
          -> (j === i ? e.target.value : v)))}                           
      105 +                onChange={(e) => change(values.map((v, j) => (
          +j === i ? e.target.value : v)))}                              
      106                />
      107              </label>
      108            ))}
      109 +          {showDraft && (                                     
      110 +            <p className="muted">                             
      111 +              組內草稿：{teamDraft.map((a, i) => `${question.l
          +abels[i] ?? ""}${a}`).join(" ／ ")}{" "}                      
      112 +              <button className="small" onClick={() => setValu
          +es([...teamDraft])}>                                          
      113 +                套用                                          
      114 +              </button>                                       
      115 +            </p>                                              
      116 +          )}                                                  
      117            <button disabled={!ready || busy} onClick={send}>
      118              搶答送出
      119            </button>

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  warning: `VIRTUAL_ENV=C:\workspace\linux2026_va2pa\.venv` does not mat
     ch the project environment path `.venv` and will be ignored; use `--ac
     tive` to target the active environment instead
     Found 1 error.
  ⎿  Updated software_fin-openspec\server\quiz_server\activity.py (+3 -0)
      368                  raise PhaseError("尚未匯入題目，不能開始搶答")
      369              await self._transition(Phase.ANSWERING)
      370              self._started_at = self._clock()
      371 +            # 開始搶答即換新邀請碼：準備階段被瞄到的碼在搶答中
          +失效，搶答中加入只能向老師索取（team-mode v1.1 D2）           
      372 +            for team in self._codes:                          
      373 +                self._codes[team] = self._new_code()          
      374              await self._bump()
      375  
      376      async def end(self) -> None:
  ⎿  Updated software_fin-openspec\server\quiz_server\views.py (+3 -1)
      85          ],
      86      }
      87      if a.team_play:
      88 -        view["invite_code"] = a.invite_code(team)              
      88 +        # 邀請碼只在準備階段給學生；搶答中只有老師畫面有（team-
         +mode v1.1 D5）                                                 
      89 +        if a.phase is Phase.PREPARING:                         
      90 +            view["invite_code"] = a.invite_code(team)          
      91          # 組內草稿只在搶答中、只含本組（team-mode D5）；其餘階
          段不帶，fail-closed
      92          if a.phase is Phase.ANSWERING:
      93              view["drafts"] = [{"question": n, "answers": list(a
          ns)}
  ⎿  Updated software_fin-openspec\web\src\pages\team.test.tsx (+1 -1)
      70    };
      71  
      72    it("顯示本組邀請碼與組內草稿", () => {
      73 -    render(<StudentPanel view={view} />);                      
      73 +    render(<StudentPanel view={view} onDraft={() => {}} />);   
      74      expect(screen.getByText("ABC234")).toBeInTheDocument();
      75      expect(screen.getByText(/組內草稿：組員的草稿/)).toBeInTheD
          ocument();
      76    });

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  warning: `VIRTUAL_ENV=C:\workspace\linux2026_va2pa\.venv` does not mat
     ch the project environment path `.venv` and will be ignored; use `--ac
     tive` to target the active environment instead
     … +8 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\quiz_server\activity.py (+2 -1)
      368                  raise PhaseError("尚未匯入題目，不能開始搶答")
      369              await self._transition(Phase.ANSWERING)
      370              self._started_at = self._clock()
      371 -            # 開始搶答即換新邀請碼：準備階段被瞄到的碼在搶答中
          -失效，搶答中加入只能向老師索取（team-mode v1.1 D2）           
      371 +            # 開始搶答即換新邀請碼：準備階段被瞄到的碼在搶答中
          +失效，                                                        
      372 +            # 搶答中加入只能向老師索取（team-mode v1.1 D2）   
      373              for team in self._codes:
      374                  self._codes[team] = self._new_code()
      375              await self._bump()
  ⎿  Updated software_fin-openspec\server\tests\test_isolation.py (+8 -0)
      230      view = json.loads(raw)["view"]
      231      assert set(view) == {"role", "phase", "team", "team_valid"
           }
      232      assert code_a not in raw
      233 +                                                              
      234 +                                                              
      235 +def test_invite_code_not_sent_to_students_while_answering(team
          +_play, teacher_headers):                                      
      236 +    c, ta, _, _ = team_play                                   
      237 +    code_now = c.get("/api/teacher/state", headers=teacher_hea
          +ders).json()["invite_codes"]["第1組"]                         
      238 +    with c.websocket_connect(f"/ws?role=student&token={ta}") a
          +s wa:                                                         
      239 +        raw = wa.receive_text()                               
      240 +    assert code_now not in raw and "invite_code" not in json.l
          +oads(raw)["view"]                                             
  ⎿  Updated software_fin-openspec\server\tests\test_team_mode.py (+18 -0)
      346      c.post("/api/teacher/start", headers=teacher_headers)
      347      draft(c, ta, 3, ["老師不該看到的草稿"])
      348      assert "老師不該看到的草稿" not in c.get("/api/teacher/sta
           te", headers=teacher_headers).text
      349 +                                                              
      350 +                                                              
      351 +# ---- v1.1：邀請碼只在準備階段給學生，開始搶答即換新 ----    
      352 +def test_code_rotates_on_start_and_hidden_from_students(loaded
          +_client, teacher_headers):                                    
      353 +    from quiz_server.views import student_view                
      354 +    c = loaded_client                                         
      355 +    team_on(c, teacher_headers)                               
      356 +    join(c, "第1組")                                          
      357 +    act = c.app.state.activity                                
      358 +    old = state(c, teacher_headers)["invite_codes"]["第1組"]  
      359 +    assert student_view(act, "第1組")["invite_code"] == old   
      360 +    c.post("/api/teacher/start", headers=teacher_headers)     
      361 +    new = state(c, teacher_headers)["invite_codes"]["第1組"]  
      362 +    view = student_view(act, "第1組")                         
      363 +    assert "invite_code" not in view and new not in str(view) 
          +and old not in str(view)                                      
      364 +    if new != old:                                            
      365 +        assert join(c, "第1組", old).status_code == 403  # 準 
          +備階段被瞄到的碼失效                                          
      366 +    assert join(c, "第1組", new).status_code == 200  # 搶答中 
          +向老師索取的新碼可用                                          
  ⎿  (timeout 5m)

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  227 passed, 1 warning in 31.14s
     41 passed in 4.02s
      ❯ src/pages/team.test.tsx (7 tests | 1 failed) 108ms
     … +8 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\tests\test_isolation.py (+2 -1)
      168      r = c.post("/api/teacher/team-play", json={"enabled": True
           }, headers=teacher_headers)
      169      assert r.status_code == 200
      170      ta, tb = join(c, "第1組"), join(c, "第2組")
      171 -    code_a = c.get("/api/teacher/state", headers=teacher_heade
          -rs).json()["invite_codes"]["第1組"]                           
      171      c.post("/api/teacher/start", headers=teacher_headers)
      172 +    # 開始搶答會換新邀請碼；取搶答中有效的那一個              
      173 +    code_a = c.get("/api/teacher/state", headers=teacher_heade
          +rs).json()["invite_codes"]["第1組"]                           
      174      return c, ta, tb, code_a
      175  
      176  
  ⎿  (timeout 5m)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; sed -i 's/
      screen.getByText("套用").click();/
      fireEvent.click(screen.getByText("套用"));/' web/src/pages/t…)
  ⎿        Tests  33 passed (33)
     > quiz-web@0.1.0 lint
     > eslint .
     … +3 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\web\src\pages\team.test.tsx (+1 -1)
      93      expect(drafts).toEqual([]);
      94      act(() => vi.advanceTimersByTime(400));
      95      expect(drafts).toEqual([[3, ["我的"]]]);
      96 -    screen.getByText("套用").click();                          
      96 +    fireEvent.click(screen.getByText("套用"));                 
      97      expect(input).toHaveValue("組員的草稿");
      98      vi.useRealTimers();
      99    });
  ⎿  (timeout 5m)

● Server 227 / web 33 tests green, lint and typecheck clean. Now updating the
  docs to v1.1 — starting with the contract.

  Ran 1 shell command (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  8
  ⎿  Updated software_fin-openspec\contracts\api.md (+10 -6)
       8  | 身分 | 憑據 | REST | WebSocket |
       9  |---|---|---|---|
      10  | 老師 | 伺服器啟動時產生的老師金鑰 | 標頭 `X-Teacher-Key` | 查
          詢參數 `role=teacher&key=<金鑰>` |
      11 -| 學生 | `POST /api/student/join` 取得的組別憑證（一組一台裝置 
         -） | 標頭 `X-Team-Token` | 查詢參數 `role=student&token=<憑證>`
         - |                                                             
      11 +| 學生 | `POST /api/student/join` 取得的組別憑證（一組一台裝置 
         +；組隊時一組最多 6 台，第二台起憑邀請碼加入——team-mode 語意補充
         +） | 標頭 `X-Team-Token` | 查詢參數 `role=student&token=<憑證>`
         + |                                                             
      12  
      13  伺服器一律由憑證反查組別，不採信客戶端自報的組別名稱。
      14  
     ...
      24  
      25  | 方法與路徑 | 身分 | 本體 | 成功回應 | 錯誤 |
      26  |---|---|---|---|---|
      27 -| `GET /api/public/info` | 任何人 | — | `{phase, teams: [組名],
         - joined: [已加入組名]}` | — |                                  
      28 -| `POST /api/student/join` | 任何人 | `{team}` | `{team, token}
         -` | 404 組別不存在；409 該組已有裝置 |                         
      27 +| `GET /api/public/info` | 任何人 | — | `{phase, teams: [組名],
         + joined: [已加入組名], team_play}`（不含台數與邀請碼；team-mode
         +） | — |                                                       
      28 +| `POST /api/student/join` | 任何人 | `{team, code?}`（組隊時：
         +該組已有邀請碼就必須帶，不分大小寫與全半形、忽略空白） | `{team
         +, token}` | 403 邀請碼不正確（組隊）；404 組別不存在；409 該組 
         +已有裝置（非組隊）或此組裝置已滿（組隊，最多 6 台；先比對邀請碼
         +再檢查上限）——team-mode 語意補充 |                             
      29 +| `POST /api/student/draft` | 學生（`X-Team-Token`） | `{questi
         +on, answers: [每個子題一個字串，可空白]}` | `{question}`（不回 
         +顯內容） | 403 憑證無效；404 題號不存在；409 非組隊（「只有組隊
         +模式可以共用草稿」）、非 answering、本組已送出此題、時間計分非 
         +開放中題；422 子題數不符、超過 200 字、含控制字元、格式錯誤（te
         +am-mode） |                                                    
      30  | `POST /api/student/submit` | 學生（`X-Team-Token`） | `{quest
          ion, answers: [每個子題一個字串]}` | `{question, answers}`（只
          回本組這筆，不含順位） | 403 憑證無效；404 題號不存在；409 非 a
          nswering 或本組已送出此題，時間計分另有「這一題目前沒有開放作答
          」「本題作答時間已到」；422 子題數不符、空白、超過 200 字、含控
          制字元、格式錯誤 |
      31  | `GET /api/teacher/state` | 老師 | — | 老師 view（同 WebSocket
          ） | 401 |
      31 -| `POST /api/teacher/teams` | 老師 | `{count}`（2–12） | `{team
         -s}`；撤銷所有組別憑證 | 401；409 非 preparing；422 超出範圍 |  
      32 -| `POST /api/teacher/release` | 老師 | `{team}` | `{released}` 
         -；撤銷該組憑證 | 401；404 |                                    
      32 +| `POST /api/teacher/teams` | 老師 | `{count}`（2–12） | `{team
         +s}`；撤銷所有組別憑證，組隊時另清除邀請碼與草稿 | 401；409 非 p
         +reparing；422 超出範圍 |                                       
      33 +| `POST /api/teacher/release` | 老師 | `{team}` | `{released}` 
         +；撤銷該組憑證（組隊時撤銷該組全部裝置、清草稿，並換新邀請碼—— 
         +新碼只在老師 view；team-mode 語意補充） | 401；404 |           
      34 +| `POST /api/teacher/team-play` | 老師 | `{enabled}` | `{team_p
         +lay}`；值改變時撤銷所有組別憑證、邀請碼與草稿，值不變不動；重置
         +保留（team-mode） | 401；409 非 preparing；422 格式錯誤 |      
      35  | `POST /api/teacher/import` | 老師 | `multipart/form-data`，欄
          位 `file`（.xlsx，≤5 MB） | `{source, count}`；取代題目並清空作
          答 | 400 檔案或格式不符；401；409 非 preparing |
      36  | `POST /api/teacher/import-url` | 老師 | `{url}`（`https://doc
          s.google.com/spreadsheets/d/<id>/…`，知道連結者可檢視） | `{sou
          rce, count}` | 400 連結或下載不符；401；409 非 preparing |
      37  | `GET /api/teacher/export` | 老師 | — | xlsx 檔（原 Guided Not
          es，得主答案寫入作答格、一律為文字）；`Content-Disposition` 含 
          `filename*=UTF-8''<原檔名>-搶答結果.xlsx` | 401；409 非 ended 
          或尚未匯入 |
     ...
      67  
      68  老師 view 另含（game-mode-framework）：`mode: {key, label, judg
          ed}`、`modes: [{key, label}]`、`score_label`（經典模式且全部倍
          率為 1 時「得題數」，其餘「得分」）、`pending_judgments`（未判
          定筆數）；`board[]` 另含 `reference: [每個子題的參考答案或 null
          ]`，`board[].ranking[]` 另含 `suggestion`（`true`／`false`／`nu
          ll`）。參考答案與建議**只在老師 view**。
      69  
      70 +老師 view 另含（team-mode）：`team_play`、`devices: {組名: 已發
         +出的憑證數}`、`invite_codes: {組名: 邀請碼}`（只列有邀請碼的組 
         +，含被釋放後待重新加入者）。老師 view 不含組內草稿。開始搶答時 
         +所有邀請碼換新。                                               
      71 +                                                               
      72  老師 view 另含（results-view）：`board`（格式同學生 view 的 `re
          sults`，任何階段即時更新）與 `team_scores`（`{組名: 分數}`；欄
          名見 `score_label`，經典模式且全部倍率為 1 時等於得題數——questi
          on-settings 語意補充）。
      73  
      74  ### 學生 view
     ...
      78   "questions": [{"number": 1, "labels": ["（1）", "（2）"]}, {"n
          umber": 3, "labels": [""]}]}
      79  ```
      80  
      77 -所有階段都含 `mode: {key, label, sequential}`、`score_label`、`
         -round` 與 `my_submissions`（只有本組：`[{question, answers}]`，
         -不含順位、序號、他組是否送出）。`judging` 與 `answering` 相同，
         -不含判定結果。時間計分模式在 `ended` 前另含 `revealed: [{questi
         -on, submitted, correct, score}]`（只有本組、只列已揭曉題）、`my
         -_total`（本組累積）與 `leaderboard: [{team, rank}]`（依已揭曉題
         -累積分數的名次，同分同名次；**不含他組分數**——分數可反推作答秒 
         -數）。只有 `ended` 階段另含 `results`：                        
      81 +所有階段都含 `mode: {key, label, sequential}`、`score_label`、`
         +round` 與 `my_submissions`（只有本組：`[{question, answers}]`，
         +不含順位、序號、他組是否送出）。`judging` 與 `answering` 相同，
         +不含判定結果。另含 `team_play`；組隊時 `preparing` 另含 `invite
         +_code`（本組邀請碼），`answering` 另含 `drafts: [{question, ans
         +wers}]`（只有本組、最後寫入者為準，送出即清除）；其餘階段兩者皆
         +不帶（team-mode）。時間計分模式在 `ended` 前另含 `revealed: [{q
         +uestion, submitted, correct, score}]`（只有本組、只列已揭曉題）
         +、`my_total`（本組累積）與 `leaderboard: [{team, rank}]`（依已 
         +揭曉題累積分數的名次，同分同名次；**不含他組分數**——分數可反推 
         +作答秒數）。只有 `ended` 階段另含 `results`：                  
      82  
     … 2 more lines (ctrl+o to expand)

● Contract updated. Now rewriting the OpenSpec design to v1.1 with both
  channels' fixes.

● Write(software_fin-openspec\openspec\changes\team-mode\design.md)
  ⎿  Error writing file

  Read 1 file (ctrl+o to expand)

● Write(software_fin-openspec\openspec\changes\team-mode\design.md)
  ⎿  Added 41 lines, removed 28 lines
       1 -# team-mode — design（v1.0）                                   
       1 +# team-mode — design（v1.1）                                   
       2  
       3  知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，
          2026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論
          時間」，隊員分數平均；Quizlet Live 隨機分隊，每位隊員只看到部分
          選項。本卡依 TRD §6 裁定只取「一隊多人、一人代表作答」，不採分
          數平均與討論時間。
       4  
       5 -倉外行為探針：無。本卡的決策只依賴本倉既有的鎖、序號與依身分裁 
         -切的 view（`server/quiz_server/activity.py`、`views.py`），不依
         -賴第三方函式庫的新行為、外部服務或瀏覽器新行為；前端草稿的防抖 
         -用 `setTimeout`，不影響伺服器端判據。                          
       5 +倉外行為探針：無。本卡的決策只依賴本倉既有的鎖、序號與依身分裁 
         +切的 view（`server/quiz_server/activity.py`、`views.py`），不依
         +賴第三方函式庫的新行為、外部服務或瀏覽器新行為；前端草稿的防抖 
         +用 `setTimeout`，不影響伺服器端判據。草稿更新會讓每條連線重算一
         +次 view，與既有「任何狀態改變都重算」相同，量級為（組數 × 6 台 
         +＋老師）≤ 73 條連線、每台每 400 毫秒至多一次，本機模擬不另跑效 
         +能探針（屬取捨）。                                             
       6  
       7 +**v1.1（提案輪評審）**：紅隊——釋放後下一台不需邀請碼即可搶佔（ 
         +改為釋放即換新碼、只顯示在老師畫面，之後連第一台也要帶碼）；全 
         +形輸入使 `compare_digest` 拋例外（改 NFKC 正規化後以位元組比對 
         +）。架構——邀請碼常駐學生畫面且搶答中可加入（改為學生只在準備階 
         +段看得到、開始搶答即換新碼）；契約身分表、join、release 屬語意 
         +補充而非純新增（D7 逐條列出、呈負責人批准）；台數算憑證數、關分
         +頁不釋放名額（列為取捨）。                                     
       8 +                                                               
       9  ## 決策
      10  
      11  ### D1 組隊是活動設定，不是模式
      12  
      11 -`Activity.team_play: bool = False`。`set_team_play(enabled)`： 
         -鎖內、`preparing`（其他階段 409）；值改變時撤銷**所有**組別憑證
         -與邀請碼，`_bump()`；值不變時什麼都不做（不撤銷）。`reset` 保留
         -；`configure_teams` 照舊撤銷所有憑證，另清除邀請碼。           
      13 +`Activity.team_play: bool = False`。`set_team_play(enabled)`： 
         +鎖內、`preparing`（其他階段 409）；值改變時撤銷**所有**組別憑證
         +、邀請碼與草稿（`_revoke_all`），`_bump()`；值不變時什麼都不做 
         +。`reset` 保留；`configure_teams` 也走 `_revoke_all`（撤銷憑證 
         +、清邀請碼與草稿）。                                           
      14  
      13 -- 證偽欄｜屬取捨，理由：見 proposal 摘要第 1 條。可證偽部分：`t
         -est_team_mode.py::test_team_play_does_not_change_scoring`（三種
         -模式各跑一組同樣的送出，組隊開／關的 `results.build` 與 `team_s
         -cores` 相同）；第一期與第二期全部測試在 `team_play=False`（預設
         -）下照舊綠。                                                   
      15 +- 證偽欄｜屬取捨，理由：代表作答不改 TRD T-01 的四個面向（誰能 
         +作答、何時鎖題、如何計分、何時揭曉），做成模式就無法與時間計分 
         +等模式並用。可證偽部分：`test_team_mode.py::test_team_play_does
         +_not_change_scoring`（三種模式各跑同樣的送出，組隊開／關的順位 
         +、判定與分數相同；時間計分的分數取決於真實時鐘，只比順位與判定 
         +）、`test_toggle_only_when_preparing`、`test_toggle_revokes_onl
         +y_on_change`、`test_configure_teams_clears_codes`；第一、二期全
         +部測試在預設 `team_play=False` 下照舊綠。                      
      16  
      17  ### D2 憑證與邀請碼
      18  
      17 -- `_tokens: dict[str, str]`（憑證 → 組別）本來就允許多對一；改 
         -的是 `join` 的檢查：                                           
      18 -  - `team_play=False`：同第一期，該組已有憑證 ⇒ `TeamTakenError
         -`（409「此組已有裝置加入，請老師釋放後再加入」）。             
      19 -  - `team_play=True` 且該組尚無裝置：發憑證，並產生該組邀請碼 `
         -_codes[team]`（6 碼，字母表 `ABCDEFGHJKLMNPQRSTUVWXYZ23456789` 
         -共 32 字，`secrets.choice`；約 10⁹ 種，本機模擬不設嘗試次數限制
         -）。                                                           
      20 -  - `team_play=True` 且該組已有裝置：本體 `code` 必須以 `secret
         -s.compare_digest` 比對相符（大小寫不敏感：先轉大寫、去空白）， 
         -否則 `InviteCodeError` ⇒ **403**「邀請碼不正確」；裝置數已達 `M
         -AX_DEVICES = 6` ⇒ 409「此組裝置已滿（最多 6 台）」。順序：先比 
         -對邀請碼、再檢查上限——沒有正確邀請碼的人不該知道該組有幾台。   
      21 -- `release(team)`：撤銷該組全部憑證並刪除邀請碼（下一台加入時重
         -新產生）。                                                     
      22 -- `devices(team) = 該組憑證數`。                               
      23 -- 讓出點仍夾在「檢查」與「寫入」之間（app-skeleton v1.1 D2）， 
         -並發加入第 6、7 台時恰一台成功。                               
      19 +- `_tokens: dict[str, str]`（憑證 → 組別）多對一；`_codes: dict
         +[str, str]`（組別 → 邀請碼）。邀請碼 6 碼，字母表 `ABCDEFGHJKLM
         +NPQRSTUVWXYZ23456789`（32 字，`secrets.choice`；約 10⁹ 種，本機
         +模擬不設嘗試次數限制，屬取捨）。                               
      20 +- `join(team, code)`，全部在鎖內，讓出點夾在檢查與寫入之間：   
      21 +  1. 組隊關閉：同第一期，該組已有憑證 ⇒ `TeamTakenError` 409「 
         +此組已有裝置加入，請老師釋放後再加入」。                       
      22 +  2. 組隊開啟且該組**有邀請碼**（已有裝置，或曾被老師釋放）：輸
         +入經 NFKC 正規化（全形轉半形）、去空白、轉大寫後**以位元組** `s
         +ecrets.compare_digest` 比對，不符 ⇒ `InviteCodeError` **403**「
         +邀請碼不正確」（非 ASCII 輸入只會比對失敗，不會拋例外）；相符但
         +已有 `MAX_DEVICES = 6` 台 ⇒ 409「此組裝置已滿（最多 6 台）」。 
         +先比對邀請碼再檢查上限：沒有正確邀請碼的人不該知道該組有幾台。 
      23 +  3. 組隊開啟且該組**沒有邀請碼**（從未有人加入）：發憑證並產生
         +邀請碼。                                                       
      24 +- **開始搶答即換新所有邀請碼**（`start`）：準備階段被他組瞄到的
         +碼在搶答中失效；搶答中要加入的組員只能向老師索取（老師 view 永 
         +遠有現行碼）。                                                 
      25 +- `release(team)`：撤銷該組全部憑證、清該組草稿；組隊時**換新邀
         +請碼**（只在老師 view）。被踢的冒用者不能搶先以「第一台」重新佔
         +住該組。                                                       
      26 +- `devices(team)`＝該組已發出的憑證數。憑證存在分頁的 sessionSt
         +orage，關分頁不會釋放名額；名額不夠時老師只能釋放整組、組員以新
         +碼重新加入（屬取捨：單台釋放需要裝置識別與在線偵測，超出本卡範 
         +圍；6 台高於一般分組人數）。                                   
      27  
      25 -- 證偽欄｜可證偽：`test_team_mode.py::test_join_requires_code` 
         -（無碼、錯碼 403 且憑證數不變；正確碼 200；小寫與前後空白可）、
         -`test_device_limit`、`test_concurrent_join_at_limit`（6 台後並 
         -發 5 次恰 0 成功；5 台後並發 5 次恰 1 成功）、`test_release_rev
         -okes_all_devices_and_code`、`test_toggle_revokes`。            
      28 +- 證偽欄｜可證偽：`test_team_mode.py::test_join_requires_code` 
         +（無碼、錯碼、截短碼 403 且不發憑證；小寫與前後空白可）、`test_
         +fullwidth_code_accepted`、`test_single_device_without_team_play
         +_unchanged`、`test_device_limit`（滿後錯碼仍 403）、`test_concu
         +rrent_join_at_limit`（6 台後並發 5 次恰 0 成功；5 台後恰 1 成功
         +）、`test_concurrent_first_join_one_code`、`test_release_revoke
         +s_all_devices_and_code`（釋放後無碼、舊碼 403，新碼可加入）、`t
         +est_code_rotates_on_start_and_hidden_from_students`。          
      29  
      30  ### D3 送出：代表作答
      31  
      29 -`submit` 不改：同組任一憑證都反查到同一組別，「本組已送出這一題
         -」的檢查、序號與時間計分的截止都在同一把鎖內。送出成功後清除該 
         -組該題的草稿（D4）。                                           
      32 +送出的判定口徑不變：同組任一憑證都反查到同一組別，「本組已送出 
         +這一題」的檢查、序號與時間計分的截止都在同一把鎖內。`submit` 唯
         +一的新增是送出成功後清除該組該題的草稿（D4）。                 
      33  
      31 -- 證偽欄｜可證偽：`test_team_mode.py::test_concurrent_submit_sa
         -me_team`（同組 3 台裝置並發送出同一題 20 次，每次恰 1 筆成功、 
         -其餘 409「本組已送出這一題，不可修改」、序號無重號）；`test_mem
         -ber_sees_team_submission`（A 裝置送出後 B 裝置的 `my_submission
         -s` 含該筆）。                                                  
      34 +- 證偽欄｜可證偽：`test_team_mode.py::test_concurrent_submit_sa
         +me_team`（同組 3 台裝置、每題並發 20 次，每次恰 1 筆成功、其餘 
         +`AlreadySubmittedError`、序號無重號）；`test_member_sees_team_s
         +ubmission`（A 裝置送出後 B 裝置收到含該筆的推播；B 再送 409「本
         +組已送出這一題，不可修改」）。                                 
      35  
      36  ### D4 組內草稿
      37  
      35 -- `POST /api/student/draft`，`X-Team-Token`，本體 `{question, a
         -nswers}`，回 `{question}`（不回顯內容）。條件：憑證有效（403） 
         -；`team_play=True`（409「只有組隊模式可以共用草稿」）；`answeri
         -ng`（409）；題號存在（404）；本組尚未送出該題（409）；時間計分 
         -只收開放中那一題（409「這一題目前沒有開放作答」）；`answers` 長
         -度＝子題數、每格 ≤200 字、不含控制字元（422，訊息固定、不回顯）
         -；**空白允許**（組員清掉草稿）。                               
      36 -- `Activity.drafts: dict[str, dict[int, tuple[str, ...]]]`（組 
         -別 → 題號 → 子題草稿），最後寫入者為準；`_clear_answers`（匯入 
         -、重置）、`release`、切換組隊時清除；送出成功清除該組該題。    
      37 -- 不寫日誌內容（`CLAUDE.md`「日誌不記學生作答原文」）。        
      38 +- `POST /api/student/draft`，`X-Team-Token`，本體 `{question, a
         +nswers}`，回 `{question}`（不回顯內容）。`set_draft` 在鎖內依序
         +檢查：組隊（409「只有組隊模式可以共用草稿」）、`answering`（409
         +）、題號（404）、時間計分只收開放中那一題（409「這一題目前沒有 
         +開放作答」）、本組尚未送出該題（409「本組已送出這一題，不可修改
         +」）、`answers` 長度＝子題數且每格 ≤200 字、不含控制字元（422，
         +訊息固定、不回顯）；**空白允許**。檢查與寫入同在一把鎖內，與送 
         +出不會交錯成「送出後又寫入草稿」。                             
      39 +- `Activity.drafts: dict[str, dict[int, tuple[str, ...]]]`，最 
         +後寫入者為準；清除時機：該題送出成功、`_clear_answers`（匯入、 
         +重置）、`release`、`_revoke_all`（切換組隊、改組數）。         
      40 +- 草稿與邀請碼都不寫日誌（`CLAUDE.md`「日誌不記學生作答原文」；
         +join 只記組別）。                                              
      41 +- 前端：送出時取消尚未送出的草稿計時器；草稿請求失敗一律靜默（ 
         +例如組員剛好送出），畫面以伺服器推來的狀態為準。               
      42  
      39 -- 證偽欄｜可證偽：`test_team_mode.py::test_draft_rules`（各錯誤
         -碼；草稿在本組 view、送出後消失）；`test_isolation.py::test_tea
         -m_draft_isolated`、`test_other_team_draft_sends_nothing`。     
      43 +- 證偽欄｜可證偽：`test_team_mode.py::test_draft_rules`（各錯誤
         +碼；最後寫入者為準；送出後消失）、`test_draft_cleared_on_releas
         +e_and_reset`、`test_draft_timed_only_open_question`、`test_teac
         +her_view_has_no_drafts`。                                      
      44  
      45  ### D5 view 與作答隔離
      46  
      43 -- 學生 view（只在 `team_valid`）：`team_play`；`invite_code`（`
         -team_play` 時為本組邀請碼）；`drafts: [{question, answers}]`——*
         -*只在 `answering` 階段**且只含本組。其餘階段不帶 `drafts`（fail
         --closed：判定中、已結束沒有理由再送草稿）。                    
      44 -- 老師 view：`team_play`、`devices: {組名: 台數}`、`invite_code
         -s: {組名: 碼}`（只含已有裝置的組）。老師 view 不含草稿。       
      47 +- 學生 view（只在 `team_valid`）：`team_play`；`invite_code`——*
         +*只在 `preparing`**；`drafts: [{question, answers}]`——**只在 `a
         +nswering`** 且只含本組。其餘階段兩者都不帶（fail-closed）。    
      48 +- 老師 view：`team_play`、`devices: {組名: 台數}`（每組都列）、
         +`invite_codes: {組名: 碼}`（只列有邀請碼的組，含被釋放後待重新 
         +加入者）。老師 view 不含草稿。                                 
      49  - 公開資訊 `GET /api/public/info` 增 `team_play`；**不含**台數
          與邀請碼。
      46 -- 學生無效憑證仍只回最少資訊（不含 `team_play`、`invite_code`）
         -。                                                             
      50 +- 學生無效憑證仍只回最少資訊（`role`、`phase`、`team`、`team_va
         +lid` 四鍵）。                                                  
      51  - 推播：草稿更新只讓本組 view 改變；他組 view 不變 ⇒ 他組連線不
          送訊息（app-skeleton v1.1 D4 的「只在本連線的 view 改變時才送」
          ）。
      52  
      49 -- 證偽欄｜可證偽：`test_isolation.py` 新增三則：①搶答中第1組草 
         -稿「甲組草稿祕密」與第1組邀請碼不出現在第2組 WebSocket、REST 成
         -功與錯誤回應、公開資訊；②第1組更新草稿時第2組連線收不到任何訊息
         -（同既有 `test_other_team_submit_sends_nothing` 的 seq 不跳號判
         -據）；③判定中、已結束的學生 view 不含 `drafts` 鍵。            
      53 +- 證偽欄｜可證偽：`test_isolation.py` 新增五則：`test_team_draf
         +t_isolated`（第1組草稿「甲組草稿祕密」與搶答中邀請碼不出現在第2
         +組 WebSocket、REST 成功與錯誤回應、公開資訊、無碼加入的 403；老
         +師看得到碼、看不到草稿）、`test_other_team_draft_sends_nothing`
         +（第2組 seq 不跳號）、`test_drafts_only_in_answering`（準備、判
         +定、結束三階段學生 view 無 `drafts`）、`test_invalid_token_gets
         +_no_team_fields`、`test_invite_code_not_sent_to_students_while_
         +answering`。                                                   
      54  
      55  ### D6 web
      56  
      53 -- 老師「組別」區塊：「組隊（一組多台裝置）」勾選框（只在準備階 
         -段可按，呼叫 `team-play`）；組隊時每組顯示「已加入（n 台）」與 
         -邀請碼。                                                       
      54 -- 首頁：組隊時已加入的組別按鈕不停用，旁邊多一個「邀請碼」輸入 
         -欄；加入失敗顯示伺服器訊息。                                   
      55 -- 學生頁：組隊時顯示「本組邀請碼：XXXXXX（給組員加入用）」；作 
         -答卡輸入後 400 毫秒送草稿；伺服器推來的組內草稿與本機輸入不同時
         -，顯示「組內草稿：…」與「套用」按鈕（不直接覆蓋正在輸入的內容）
         -。                                                             
      57 +- 老師「組別」區塊：「組隊（一組多台裝置）」勾選框（只在準備階 
         +段可按，呼叫 `team-play`）；組隊時每組顯示「已加入（n 台）」與 
         +邀請碼，並提示「開始搶答時邀請碼會換新，搶答中要加入的組員請向 
         +老師索取」。                                                   
      58 +- 首頁（`TeamPicker`）：組隊時已加入的組別按鈕不停用，多一個「 
         +邀請碼」輸入欄；加入失敗顯示伺服器訊息。首頁只在載入時讀一次公 
         +開資訊（同第一期）。                                           
      59 +- 學生頁：組隊時顯示「組內任一人送出即代表全組」；準備階段顯示 
         +本組邀請碼，搶答中改提示向老師索取。作答卡輸入後 400 毫秒送草稿
         +（D4 前端規則）；組內草稿非空且與本機輸入不同時，顯示「組內草稿
         +：…」與「套用」按鈕（不直接覆蓋正在輸入的內容）。              
      60  
      57 -- 證偽欄｜可證偽：`web/src/pages/team.test.tsx`。              
      61 +- 證偽欄｜可證偽：`web/src/pages/team.test.tsx`（老師勾選呼叫 A
         +PI、非準備階段停用、台數與邀請碼；首頁組隊時已加入可按並帶碼、 
         +非組隊時停用且無碼欄；學生頁邀請碼與草稿；防抖只送最後一次、「 
         +套用」帶入；非組隊不送草稿）。                                 
      62  
      63  ### D7 契約
      64  
      61 -`contracts/api.md` 增 `POST /api/teacher/team-play`（`{enabled}
         -` ⇒ `{team_play}`；401／409 非 preparing／422）、`POST /api/stu
         -dent/draft`（D4）；`POST /api/student/join` 本體 `{team, code?}
         -`，增 403 邀請碼不正確、409 此組裝置已滿；`/api/public/info` 增
         - `team_play`；老師與學生 view 增 D5 欄位。全部是**新增**，既有 
         -欄位語意不變（`team_play=False` 時行為與第一期相同）。         
      65 +**新增**：`POST /api/teacher/team-play`（`{enabled}` ⇒ `{team_p
         +lay}`；401／409 非 preparing／422）、`POST /api/student/draft` 
         +（D4）；`/api/public/info` 增 `team_play`；老師 view 增 `team_p
         +lay`、`devices`、`invite_codes`；學生 view 增 `team_play`、`inv
         +ite_code`、`drafts`。                                          
      66  
      63 -- 證偽欄｜可證偽：`make test` 中第一期 `test_api_skeleton.py::t
         -est_join_once_per_team`、`test_phases.py::test_concurrent_join_
         -same_team_once` 等既有測試不改仍綠。                           
      67 +**語意補充（v1.1，呈負責人批准）**——`contracts/api.md` 以下既有
         +字句在組隊時語意改變（組隊關閉時與第一期相同）：               
      68 +                                                               
      69 +1. 身分表「組別憑證（一組一台裝置）」⇒ 補「組隊時一組最多 6 台 
         +，第二台起憑邀請碼加入」。                                     
      70 +2. `POST /api/student/join` 本體 `{team}` ⇒ `{team, code?}`；錯
         +誤增 403「邀請碼不正確」；409 在組隊時改指「此組裝置已滿」。   
      71 +3. `POST /api/teacher/release`「撤銷該組憑證」⇒ 組隊時撤銷該組 
         +全部裝置、清草稿並換新邀請碼。                                 
      72 +4. `POST /api/teacher/teams` 另清除邀請碼與草稿。              
      73 +                                                               
      74 +`docs/product-trd.md` §3「每組一台裝置」同批補「組隊時最多 6 台
         +」。                                                           
      75 +                                                               
      76 +- 證偽欄｜可證偽：`make test` 中第一期 `test_api_skeleton.py::t
         +est_join_once_per_team`、`test_phases.py::test_concurrent_join_
         +same_team_once` 等既有測試不改仍綠；`test_team_mode.py::test_si
         +ngle_device_without_team_play_unchanged`。                     

● Now proposal, spec, tasks, matrix, product-trd, manual-verification scene E,
  parity row (OpenSpec side).

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  4:- [x] 1.1
     `server/tests/test_team_mode.py`（D1–D4：開關、邀請碼、上限
     與並發加入、釋放與切換撤銷、同組並發送出、組員看得到送出、草稿規則與清
     除、組隊不改計分）
     … +14 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\proposal.md
     (+11 -3)
       1 -# team-mode — 組隊模式：一組多台裝置、代表作答（v1.0）         
       1 +# team-mode — 組隊模式：一組多台裝置、代表作答（v1.1）         
       2  
       3  檔位：**S**（作答隔離：新增送往學生端的組內草稿通道；`contracts
          /` 增端點與欄位；組別憑證口徑改變）｜主人：@yue083139｜parity：
          `docs/parity.md` §4 `team-mode`｜需求：X-04（TRD M4、§6 裁定「
          代表作答」）｜依賴：`game-mode-framework`
       4  
       5  ## 首屏決策摘要
       6  
       7  1. **組隊是與模式正交的活動設定，不是第四種模式**：選了 `team_p
          lay` 開關（任何模式都可開）／代價：TRD §3 把 M4 列在模式表，名
          稱上不一致／可被「三種模式 × 組隊開關的計分與第一期全部測試結果
          不變」證偽；屬取捨，理由：代表作答不改「誰能作答、何時鎖題、如
          何計分、何時揭曉」任何一項（TRD T-01 的四個面向），做成模式就得
          和經典／只計對錯／時間計分各組合一次。
       8 -2. **同組第二台起的裝置要輸入該組的邀請碼**：第一台加入時伺服器
         -產生 6 碼邀請碼，只出現在該組自己的畫面與老師畫面／代價：組員要
         -多輸入一次／可被「沒有邀請碼加入已有裝置的組別 ⇒ 403，且拿不到 
         -任何組別憑證」的負例證偽。不設邀請碼時，任何人選一個已有人的組 
         -別就能讀到該組草稿與送出——第一期「一組一台裝置」擋掉的冒用，在 
         -組隊下會重新打開。                                             
       8 +2. **同組第二台起的裝置要輸入該組的邀請碼**：第一台加入時伺服器
         +產生 6 碼邀請碼；學生只在準備階段看得到，開始搶答即換新、釋放某
         +組也換新，搶答中只有老師畫面有現行碼／代價：組員多輸入一次，搶 
         +答中加入要問老師／可被「無碼、錯碼、準備階段的舊碼、釋放前的舊 
         +碼加入 ⇒ 403 且拿不到憑證」的負例證偽。不設邀請碼時，任何人選一
         +個已有人的組別就能讀到該組草稿與送出——第一期「一組一台裝置」擋 
         +掉的冒用，在組隊下會重新打開。                                 
       9  3. **每組每題仍只能送出一次，組內任一人送出即代表全組**：送出判
          定與順位完全沿用 `buzz-answering`（同一把鎖、同一個序號）／可被
          「同組兩台裝置並發送出同一題 N 次，每次恰一筆成功」證偽。
      10  4. **組內草稿只在 `answering` 階段送給本組裝置**：最後寫入者為
          準，不進結果、不匯出、老師看不到／可被「他組草稿更新時本組連線
          不收到任何訊息，且本組 payload 不含他組草稿字串」證偽。
      11 -5. **切換組隊開關、改組數、釋放某組都撤銷相關憑證與邀請碼**：代
         -價：準備階段切換後所有裝置要重新加入／屬取捨，理由：撤銷是唯一 
         -不必處理「多台變一台時留哪台」的做法，且只在準備階段可切換。   
      11 +5. **切換組隊開關、改組數、釋放某組都撤銷相關憑證**：代價：準備
         +階段切換後所有裝置要重新加入；台數算的是已發出的憑證，關分頁不 
         +釋放名額，只能整組釋放／屬取捨，理由：撤銷是唯一不必處理「多台 
         +變一台時留哪台」的做法；單台釋放需要裝置識別與在線偵測，超出本 
         +卡範圍。                                                       
      12 +                                                               
      13 +**v1.1（提案輪評審）**：釋放後與搶答中的邀請碼口徑收緊（摘要第 
         +2 條）；全形輸入正規化；契約身分表、join、release 四處屬**語意 
         +補充**，見 design D7，**呈負責人批准**。                       
      14  
      15  **矩陣落點**：新增 M-017（組隊加入與邀請碼）、M-018（組內任一人
          送出即代表全組）、M-019（組內草稿隔離）。
      16  
     ...
      37  | 4 | `npm --prefix web test` | 組隊開關呼叫 API、首頁帶邀請碼
          加入、學生頁顯示組內草稿並可套用；passed |
      38  | 5 | 人工驗證 | `docs/manual-verification.md` 場次 E |
      39  
      40 +## 未決呈裁                                                    
      41 +                                                               
      42 +| 事項 | 我傾向 | 阻塞否 |                                     
      43 +|---|---|---|                                                  
      44 +| `contracts/api.md` 四處語意補充（design D7：身分表一組多台、j
         +oin 帶 `code` 與 403／409 新語意、release 換新碼、改組數清碼與 
         +草稿） | 批准：組隊關閉時行為與第一期完全相同，既有測試不改仍綠
         + | 阻塞合入，不阻塞實作 |                                      
      45 +                                                               
      46  ## 實錄結果
      47  
      48  見 `verification.md`。
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\specs\team-mo
     de\spec.md (+6 -2)
      18  
      19  ### Requirement: 組隊時同組第二台起須輸入邀請碼
      20  
      21 -組隊時，某組第一台裝置加入 MUST 取得組別憑證並使伺服器產生該組 
         -6 碼邀請碼；之後加入同組的裝置 MUST 提供相符的邀請碼（不分大小 
         -寫、忽略前後空白），否則 MUST 回 403 且 MUST NOT 發出憑證。每組
         -最多 6 台；已滿 MUST 回 409。邀請碼 MUST 只出現在該組自己的學生
         -畫面與老師畫面。老師釋放某組 MUST 撤銷該組全部裝置的憑證並作廢 
         -邀請碼。                                                       
      21 +組隊時，某組第一台裝置加入 MUST 取得組別憑證並使伺服器產生該組 
         +6 碼邀請碼；該組有邀請碼之後，加入的裝置 MUST 提供相符的邀請碼 
         +（不分大小寫與全半形、忽略空白），否則 MUST 回 403 且 MUST NOT 
         +發出憑證。每組最多 6 台；已滿 MUST 回 409，且 MUST 先比對邀請碼
         +再檢查上限。學生畫面 MUST 只在 `preparing` 階段含本組邀請碼；老
         +師畫面 MUST 一直含各組現行邀請碼。開始搶答時 MUST 換新所有邀請 
         +碼。老師釋放某組 MUST 撤銷該組全部裝置的憑證並換新邀請碼（新碼 
         +只在老師畫面）。                                               
      22  
      23  #### Scenario: 沒有邀請碼不能加入已有組員的組別
      24  - **WHEN** 組隊時第1組已有一台裝置，另一台裝置選第1組但未帶或帶
          錯邀請碼
     ...
      34  
      35  #### Scenario: 釋放整組
      36  - **WHEN** 老師釋放第1組
      37 -- **THEN** 第1組所有裝置的憑證 MUST 失效，舊邀請碼 MUST 不能再 
         -用來加入                                                       
      37 +- **THEN** 第1組所有裝置的憑證 MUST 失效；之後不帶碼或帶舊邀請 
         +碼加入第1組 MUST 回 403，帶老師畫面上的新邀請碼 MUST 可加入    
      38 +                                                               
      39 +#### Scenario: 開始搶答換新邀請碼                              
      40 +- **WHEN** 老師開始搶答                                        
      41 +- **THEN** 準備階段的邀請碼 MUST 失效，學生畫面 MUST NOT 再含邀
         +請碼，帶老師畫面上的新邀請碼 MUST 可加入                       
      42  
      43  ### Requirement: 組內任一人送出即代表全組
      44  
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\tasks.md (+8 
     -8)
       1 -# team-mode — tasks（v1.0）                                    
       1 +# team-mode — tasks（v1.1）                                    
       2  
       3  ## 1. 驗收先行
       4 -- [ ] 1.1 `server/tests/test_team_mode.py`（D1–D4：開關、邀請碼
         -、上限與並發加入、釋放與切換撤銷、同組並發送出、組員看得到送出 
         -、草稿規則與清除、組隊不改計分）                               
       5 -- [ ] 1.2 `server/tests/test_isolation.py` 新增組隊負例三則（D5
         -）                                                             
       6 -- [ ] 1.3 `eval/acceptance/matrix.yaml` M-017～M-019           
       7 -- [ ] 1.4 web：`web/src/pages/team.test.tsx`（D6）             
       4 +- [x] 1.1 `server/tests/test_team_mode.py`（D1–D4：開關、邀請碼
         +、上限與並發加入、釋放與切換撤銷、同組並發送出、組員看得到送出 
         +、草稿規則與清除、組隊不改計分）                               
       5 +- [x] 1.2 `server/tests/test_isolation.py` 新增組隊負例三則（D5
         +）                                                             
       6 +- [x] 1.3 `eval/acceptance/matrix.yaml` M-017～M-019           
       7 +- [x] 1.4 web：`web/src/pages/team.test.tsx`（D6）             
       8  
       9  ## 2. 實作
      10 -- [ ] 2.1 `activity.py`：`team_play`、`set_team_play`、`join(te
         -am, code)`、邀請碼、`MAX_DEVICES`、`devices`、`drafts` 與清除  
      11 -- [ ] 2.2 `app.py`：`/api/teacher/team-play`、`/api/student/dra
         -ft`、join 本體 `code`、403；`views.py` D5 欄位；`contracts/api.
         -md`（D7）                                                      
      12 -- [ ] 2.3 web：老師組隊開關與台數／邀請碼、首頁邀請碼欄、學生頁
         -邀請碼與組內草稿                                               
      10 +- [x] 2.1 `activity.py`：`team_play`、`set_team_play`、`join(te
         +am, code)`、邀請碼、`MAX_DEVICES`、`devices`、`drafts` 與清除  
      11 +- [x] 2.2 `app.py`：`/api/teacher/team-play`、`/api/student/dra
         +ft`、join 本體 `code`、403；`views.py` D5 欄位；`contracts/api.
         +md`（D7 新增與四處語意補充）；`docs/product-trd.md` §3、§4     
      12 +- [x] 2.3 web：老師組隊開關與台數／邀請碼、首頁邀請碼欄、學生頁
         +邀請碼與組內草稿                                               
      13  
      14  ## 3. 驗證
      15  - [ ] 3.1 `make gate` 原樣輸出、變異實錄、人工驗證步驟寫入 `ver
          ification.md` 與 `docs/manual-verification.md` 場次 E

● Bash(cd /c/workspace/software_fin/software_fin-openspec; sed -i
      's/新增組隊負例三則（D5）/新增組隊負例五則（D5）/'
      openspec/changes/team-mode/tasks.md; grep -n "每組一台裝置\|組隊模式 |"
      docs/pro…)
  ⎿  15:| 活動前發講義、活動中收回、學生輪流上台寫黑板 | 每組一台裝置線上作
     答，老師畫面即時看到全部 |
     23:- **學生**：以**組**為單位，預設 4 組（可設 2–12 組）；每組一台裝置
     … +12 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\tasks.md (+1 
     -1)
      2  
      3  ## 1. 驗收先行
      4  - [x] 1.1 `server/tests/test_team_mode.py`（D1–D4：開關、邀請碼
         、上限與並發加入、釋放與切換撤銷、同組並發送出、組員看得到送出、
         草稿規則與清除、組隊不改計分）
      5 -- [x] 1.2 `server/tests/test_isolation.py` 新增組隊負例三則（D5 
        -）                                                              
      5 +- [x] 1.2 `server/tests/test_isolation.py` 新增組隊負例五則（D5 
        +）                                                              
      6  - [x] 1.3 `eval/acceptance/matrix.yaml` M-017～M-019
      7  - [x] 1.4 web：`web/src/pages/team.test.tsx`（D6）
      8  

● Bash(cd /c/workspace/software_fin/software_fin-openspec; python - <<'EOF'
      from pathlib import Path…)
  ⎿  227 passed, 1 warning in 40.12s
     41 passed in 5.18s
      Test Files  7 passed (7)
     … +5 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\docs\manual-verification.md (+12 -3)
       97  5. 老師判第1組正確 →「揭曉本題」⇒ 第1組看到「本組答對，+8xx 分
           」左右（分數＝`(20010 − 作答毫秒) // 20`：2 秒約 900、3 秒約 8
           50，越快越高）；第2組看到「本組未作答」與名次表，名次表**沒有
           分數欄**；第2組 WebSocket 訊息看不到第1組答案與分數。
       98  6. 老師未揭曉時「開放下一題」「結束活動」停用；揭曉後可開下一
           題或結束活動；結束後學生看到完整結果與各組分數。
       99  
      100 -### 場次 E：組隊模式（team-mode，第三期）                     
      101 -                                                              
      102 -第三期卡合入後補上步驟；屆時以該卡 `verification.md` 的人工驗 
          -證段為準。                                                    
      100 +### 場次 E：組隊（team-mode，約 15 分鐘）                     
      101 +                                                              
      102 +需要三個學生分頁（第1組 A、第1組 B、第2組）；同一組的兩個分頁 
          +請用不同瀏覽器或無痕視窗（組別憑證存在分頁裡）。              
      103 +                                                              
      104 +1. 重置；模式選「經典搶答」；匯入 `group.xlsx`；老師在「組別」
          +區塊勾「組隊（一組多台裝置）」。                              
      105 +2. 第1組 A 分頁到首頁選「第1組」⇒ 學生頁顯示「本組邀請碼：XXXX
          +XX」；老師頁第1組顯示「已加入（1 台）」與同一組邀請碼。       
      106 +3. 第1組 B 分頁到首頁，不填邀請碼按「第1組」⇒ 顯示「邀請碼不正
          +確」；填入 A 畫面上的邀請碼（可打小寫）再按 ⇒ 加入成功；老師頁
          +第1組變「已加入（2 台）」。第2組分頁選「第2組」。             
      107 +4. 老師按「開始搶答」⇒ A、B 學生頁不再顯示邀請碼（改提示向老師
          +索取）；老師頁第1組的邀請碼換成新的。                         
      108 +5. A 在第 3 題輸入「甲」⇒ 約半秒後 B 的第 3 題出現「組內草稿：
          +甲」與「套用」；按「套用」⇒ B 的輸入欄變成「甲」。第2組畫面沒 
          +有任何變化；第2組開發者工具的 WebSocket 訊息**沒有新訊息**、看
          +不到「甲」。                                                  
      109 +6. B 送出第 3 題 ⇒ A 的第 3 題立刻變成「已送出：甲」，A 不能再
          +送第 3 題。                                                   
      110 +7. 老師在組別區按第1組「釋放」⇒ A、B 都顯示「尚未加入組別或組 
          +別已被老師釋放」；老師頁第1組出現新的邀請碼。A 到首頁用**舊** 
          +碼加入 ⇒「邀請碼不正確」；用老師頁的新碼 ⇒ 加入成功。         
      111 +8. 老師按「結束搶答」⇒ 結果與經典搶答相同（第 3 題得主第1組， 
          +答案「甲」）。                                                
      112  
      113  ## 4. Demo 影片可順便錄
      114  
  ⎿  Updated software_fin-openspec\docs\product-trd.md (+2 -2)
      20  ## 3. 使用者與流程
      21  
      22  - **老師**：一人，用啟動時產生的老師金鑰網址進入。
      23 -- **學生**：以**組**為單位，預設 4 組（可設 2–12 組）；每組一台
         -裝置，裝置掛掉由老師「釋放」。                                 
      23 +- **學生**：以**組**為單位，預設 4 組（可設 2–12 組）；每組一台
         +裝置，裝置掛掉由老師「釋放」；老師開啟**組隊**時一組最多 6 台，
         +第二台起憑該組邀請碼加入。                                     
      24  
      25  ```mermaid
      26  flowchart LR
     ...
      46  | 只計對錯模式 | 不比速度、比正確；結束後老師判定，參考答案欄可
          預填建議並「採用全部建議」 | X-04 | 已合入 |
      47  | 雙倍分數題 | 任何模式下把指定題目設為 ×2 分，學生看得到標記 |
           X-04 | 已合入 |
      48  | 時間計分模式（Kahoot 式） | 老師逐題開放、每題 5–120 秒時限由
          伺服器計時；答越快分越高（最高 1000 分 × 倍率）；每題揭曉後公開
          各組**名次** | X-04 | 已合入 |
      49 -| 組隊模式 | 一組多台裝置，組內任一人送出即代表全組，組員看得到
         -組內草稿 | X-04 | 第三期 |                                     
      49 +| 組隊 | 活動設定，可與任一模式搭配：一組最多 6 台裝置、憑邀請 
         +碼加入，組內任一人送出即代表全組，搶答中組員看得到本組草稿（老 
         +師與他組看不到） | X-04 | 第三期（待合入） |                   
      50  | CSV 匯出、公平順位、錯誤遞補 | 見 `docs/parity.md` §4 | X-02
          、X-03 | 未開 |
      51  
      52  ## 5. 專案特色（和一般搶答系統不一樣的地方）
  ⎿  Updated software_fin-openspec\eval\acceptance\matrix.yaml (+18 -0)
       99      守門: server/tests/test_timed_mode.py::test_timed_mode_iso
           lated、test_timed_other_team_submit_sends_nothing、test_studen
           t_leaderboard_has_no_scores、test_leaderboard_counts_revealed_
           only；web/src/pages/timed.test.tsx
      100      狀態: covered
      101      卡: mode-timed-scoring
      102 +  - id: M-017                                                 
      103 +    需求: R-01、X-04                                          
      104 +    聲明: 組隊時同組第二台起須帶相符邀請碼（不分大小寫與全半形
          +），否則 403 且不發憑證；每組最多 6 台；學生只在準備階段看得到
          +邀請碼，開始搶答與釋放某組都換新碼                            
      105 +    守門: server/tests/test_team_mode.py::test_join_requires_c
          +ode、test_fullwidth_code_accepted、test_device_limit、test_con
          +current_join_at_limit、test_concurrent_first_join_one_code、te
          +st_release_revokes_all_devices_and_code、test_code_rotates_on_
          +start_and_hidden_from_students、test_toggle_revokes_only_on_ch
          +ange；web/src/pages/team.test.tsx                             
      106 +    狀態: covered                                             
      107 +    卡: team-mode                                             
      108 +  - id: M-018                                                 
      109 +    需求: R-07、R-10、X-04                                    
      110 +    聲明: 組隊時組內任一人送出即代表全組，同組多台並發送出同一
          +題恰一筆成功；組隊不改任何模式的順位、判定與分數              
      111 +    守門: server/tests/test_team_mode.py::test_concurrent_subm
          +it_same_team、test_member_sees_team_submission、test_team_play
          +_does_not_change_scoring                                      
      112 +    狀態: covered                                             
      113 +    卡: team-mode                                             
      114 +  - id: M-019                                                 
      115 +    需求: R-09、X-04                                          
      116 +    聲明: 組內草稿只在搶答中送給本組裝置，他組、老師與公開資訊
          +都拿不到，他組草稿更新不觸發本組推播                          
      117 +    守門: server/tests/test_isolation.py::test_team_draft_isol
          +ated、test_other_team_draft_sends_nothing、test_drafts_only_in
          +_answering、test_invalid_token_gets_no_team_fields、test_invit
          +e_code_not_sent_to_students_while_answering；server/tests/test
          +_team_mode.py::test_draft_rules、test_teacher_view_has_no_draf
          +ts                                                            
      118 +    狀態: covered                                             
      119 +    卡: team-mode                                             
  ⎿  (timeout 5m)
● All green. Now mutation records (S tier: guards must go red when broken).

  Ran 1 shell command (ctrl+o to expand)

● M2 survived — the rotation test's if new != old guard made it vacuous.
  Tightening both rotation assertions (collision chance ≈10⁻⁹).

● Bash(cd /c/workspace/software_fin/software_fin-openspec/server; python -
      <<'EOF'
      from pathlib import Path…)
  ⎿  == M2 重跑 ['FAILED tests/test_team_mode.py::test_code_rotates_on_star
     t_and_hidden_from_students', '1 failed, 1 warning in 1.14s']
     22 passed, 1 warning in 2.03s
     … +3 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\server\tests\test_team_mode.py (+4 -5)
      207      s = state(c, teacher_headers)
      208      assert s["devices"]["第1組"] == 0 and "第1組" not in s["jo
           ined"]
      209      new = s["invite_codes"]["第1組"]  # 釋放即換新碼，只在老師
           畫面
      210 -    assert new != old or len(new) == 6                        
      210 +    assert new != old  # 換新（撞碼機率約 10⁻⁹）              
      211      # 被踢的人不能搶先以「第一台」重新佔住：不帶碼、帶舊碼都 4
           03
      212      assert join(c, "第1組").status_code == 403
      213 -    if new != old:                                            
      214 -        assert join(c, "第1組", old).status_code == 403       
      213 +    assert join(c, "第1組", old).status_code == 403           
      214      assert join(c, "第1組", new).status_code == 200
      215      assert state(c, teacher_headers)["invite_codes"]["第1組"] 
           == new
      216  
     ...
      360      new = state(c, teacher_headers)["invite_codes"]["第1組"]
      361      view = student_view(act, "第1組")
      362      assert "invite_code" not in view and new not in str(view) 
           and old not in str(view)
      364 -    if new != old:                                            
      365 -        assert join(c, "第1組", old).status_code == 403  # 準 
          -備階段被瞄到的碼失效                                          
      363 +    assert new != old  # 換新（32⁶ 種，撞碼機率約 10⁻⁹）      
      364 +    assert join(c, "第1組", old).status_code == 403  # 準備階 
          +段被瞄到的碼失效                                              
      365      assert join(c, "第1組", new).status_code == 200  # 搶答中
           向老師索取的新碼可用

● All 8 mutations now go red. Running the full make gate for the verification
  record.

  Ran 1 shell command (ctrl+o to expand)

● Parity is red only because SpecKit isn't synced yet. Porting the code and
  shared files to SpecKit.

  Ran 2 shell commands (ctrl+o to expand)

● Now SpecKit's spec/research/plan/data-model/contracts/tasks to v1.1.

● Bash(cd /c/workspace/software_fin/software_fin-speckit/specs/009-team-mode;
      python - <<'EOF'
      from pathlib import Path…)
  ⎿  32:- [ ] T012 圖碼一致核對、`make gate` 寫入 `verification.md`
     33:- [ ] T013 人工驗證（`docs/manual-verification.md` 場次 E）
  ⎿  Updated software_fin-speckit\specs\009-team-mode\contracts\README.md
     (+3 -1)
      1  # 009 team-mode 介面契約
      2  
      3 -於 [`/contracts/api.md`](../../../contracts/api.md) 新增 `POST /
        -api/teacher/team-play`（`{enabled}` ⇒ `{team_play}`；401／409 非
        - preparing／422）、`POST /api/student/draft`（`{question, answer
        -s}` ⇒ `{question}`；403／404／409／422，見 research R4）；`POST 
        -/api/student/join` 本體 `{team, code?}`，增 403 邀請碼不正確、40
        -9 此組裝置已滿；`/api/public/info` 增 `team_play`；老師 view 增 
        -`team_play`、`devices`、`invite_codes`；學生 view 增 `team_play`
        -、`invite_code`、`drafts`。全部只增不改。                       
      3 +於 [`/contracts/api.md`](../../../contracts/api.md) **新增** `PO
        +ST /api/teacher/team-play`（`{enabled}` ⇒ `{team_play}`；401／40
        +9 非 preparing／422）、`POST /api/student/draft`（`{question, an
        +swers}` ⇒ `{question}`；403／404／409／422，見 research R4）；`/
        +api/public/info` 增 `team_play`；老師 view 增 `team_play`、`devi
        +ces`、`invite_codes`；學生 view 增 `team_play`、`invite_code`（ 
        +只在 preparing）、`drafts`（只在 answering）。                  
      4 +                                                                
      5 +**語意補充（v1.1，呈負責人批准，見 research R7）**：身分表一組多
        +台；`POST /api/student/join` 本體 `{team, code?}`、403 邀請碼不 
        +正確、組隊時 409 指已滿；`release` 組隊時撤銷全部裝置、清草稿並 
        +換新碼；`teams` 另清除邀請碼與草稿。組隊關閉時與 001 相同。     
  ⎿  Updated software_fin-speckit\specs\009-team-mode\data-model.md (+2 -2)
       5  | 實體 | 欄位 | 說明 |
       6  |---|---|---|
       7  | `Activity`（增） | `team_play: bool = False` | 只在 preparing
           改；改變時撤銷憑證與邀請碼；重置保留 |
       8 -| `Activity`（增） | `_codes: dict[組別, str]` | 6 碼邀請碼；第
         -一台加入時產生；釋放、改組數、切換組隊時刪除 |                 
       8 +| `Activity`（增） | `_codes: dict[組別, str]` | 6 碼邀請碼；第
         +一台加入時產生；開始搶答與釋放時換新；改組數、切換組隊時刪除 | 
       9  | `Activity`（增） | `drafts: dict[組別, dict[題號, tuple[str, 
          ...]]]` | 組內草稿，最後寫入者為準 |
      10  | `Activity`（改） | `_tokens: dict[憑證, 組別]` | 組隊時同組可
          多筆（最多 `MAX_DEVICES = 6`） |
      11  | `InviteCodeError`（新） | — | API 層轉 403 |
      12  
      13 -view 增欄位：老師 `team_play`、`devices`、`invite_codes`；學生 
         -`team_play`、`invite_code`、`drafts`（只在 answering）；公開資 
         -訊 `team_play`。                                               
      13 +view 增欄位：老師 `team_play`、`devices`、`invite_codes`；學生 
         +`team_play`、`invite_code`（只在 preparing）、`drafts`（只在 an
         +swering）；公開資訊 `team_play`。                              
  ⎿  Updated software_fin-speckit\specs\009-team-mode\plan.md (+4 -2)
       6  ## Summary
       7  
       8  1. **組隊是與模式正交的活動設定**（`team_play`）／代價：與 TRD 
          模式表名稱不一致／可被「三種模式 × 組隊開關計分相同」證偽；屬取
          捨（research R1）。
       9 -2. **同組第二台起須輸入 6 碼邀請碼**／代價：組員多輸入一次／可 
         -被「無碼或錯碼 403 且不發憑證」證偽（R2）。                    
       9 +2. **同組第二台起須輸入 6 碼邀請碼，學生只在準備階段看得到，開 
         +始搶答與釋放都換新碼**／代價：組員多輸入一次，搶答中加入要問老 
         +師／可被「無碼、錯碼、舊碼 403 且不發憑證」證偽（R2）。        
      10  3. **每組每題仍只送一次，任一人送出代表全組**，判定沿用 003 的
          鎖與序號／可被「同組並發送出恰一筆成功」證偽（R3）。
      11  4. **組內草稿只在 `answering` 送給本組**，老師與他組永遠拿不到
          ／可被「他組草稿不在本組 payload、不觸發本組推播」證偽（R4、R5
          ）。
      12  5. **切換組隊、改組數、釋放都撤銷相關憑證與邀請碼**／代價：準備
          階段切換後要重新加入／屬取捨（R1、R2）。
      13  
      14 +**v1.1**：提案輪兩通道藥方已併入（research 開頭）；**契約四處語
         +意補充呈負責人批准**（R7，阻塞合入、不阻塞實作）。             
      15 +                                                               
      16  **矩陣落點**：M-017（組隊加入與邀請碼）、M-018（代表作答）、M-0
          19（組內草稿隔離）。
      17  
      18  ## Technical Context
     ...
      21  **Primary Dependencies**: 無新增
      22  **Storage**: 記憶體 `team_play`、`_codes: dict[組別, 邀請碼]`、
          `drafts: dict[組別, dict[題號, tuple]]`
      23  **Testing**: pytest、vitest
      22 -**Constraints**: `contracts/api.md` 只增不改；組隊關閉時行為與 
         -001–008 相同                                                   
      24 +**Constraints**: `contracts/api.md` 新增為主，四處語意補充（R7 
         +）；組隊關閉時行為與 001–008 相同                              
      25  
      26  ## Constitution Check
      27  
  ⎿  Updated software_fin-speckit\specs\009-team-mode\research.md (+13 -6)
      2  
      3  知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，2
         026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論時
         間」，隊員分數平均；Quizlet Live 隨機分隊、每位隊員只看到部分選
         項。依 TRD §6 裁定只取「一隊多人、一人代表作答」。
      4  
      5 +**v1.1（提案輪評審）**：紅隊——釋放後下一台不需碼即可搶佔（改為釋
        +放即換新碼、只在老師畫面）；全形輸入使 `compare_digest` 拋例外（
        +改 NFKC 後以位元組比對）。架構——邀請碼常駐學生畫面且搶答中可加入
        +（改為學生只在準備階段看得到、開始搶答換新碼）；契約身分表、join
        +、release 屬語意補充（R7，呈負責人批准）；台數算憑證數（列為取捨
        +）。                                                            
      6 +                                                                
      7  倉外行為探針：無。決策只依賴本倉既有的鎖、序號與依身分裁切的 vie
         w，不依賴第三方函式庫新行為、外部服務或瀏覽器新行為。
      8  
      9  ## R1 組隊是活動設定，不是模式
     ...
      15  
      16  ## R2 憑證與邀請碼
      17  
      16 -- **Decision**：`_tokens`（憑證 → 組別）多對一。組隊關閉：同 00
         -1（已有憑證 ⇒ 409）。組隊開啟：該組無裝置 ⇒ 發憑證並產生邀請碼 
         -（6 碼，字母表 `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`，`secrets.cho
         -ice`，約 10⁹ 種，本機模擬不設嘗試次數限制）；已有裝置 ⇒ `code` 
         -轉大寫去空白後 `secrets.compare_digest` 比對，不符 403；再檢查 
         -`MAX_DEVICES = 6`，滿 409。先比對邀請碼再檢查上限：沒有正確碼的
         -人不該知道該組幾台。`release` 撤銷該組全部憑證並刪除邀請碼。讓 
         -出點夾在檢查與寫入之間。                                       
      17 -- **Rationale**：沒有邀請碼，選一個已有人的組別就能讀到該組草稿
         -與送出。                                                       
      18 -- **證偽欄｜可證偽**：`test_join_requires_code`、`test_device_l
         -imit`、`test_concurrent_join_at_limit`、`test_release_revokes_a
         -ll_devices_and_code`、`test_toggle_revokes`。                  
      18 +- **Decision**：`_tokens`（憑證 → 組別）多對一。組隊關閉：同 00
         +1（已有憑證 ⇒ 409）。組隊開啟且該組**有邀請碼**（已有裝置或曾被
         +釋放）⇒ `code` 經 NFKC、去空白、轉大寫後以位元組 `secrets.compa
         +re_digest` 比對，不符 403；再檢查 `MAX_DEVICES = 6`，滿 409（先
         +比對碼：沒有正確碼的人不該知道該組幾台）。組隊開啟且**無邀請碼*
         +* ⇒ 發憑證並產生邀請碼（6 碼，字母表 `ABCDEFGHJKLMNPQRSTUVWXYZ2
         +3456789`，`secrets.choice`，約 10⁹ 種，不設嘗試次數限制，屬取捨
         +）。`start` 換新所有邀請碼；`release` 撤銷該組全部憑證、清草稿 
         +並換新碼（只在老師畫面）。讓出點夾在檢查與寫入之間。台數＝已發 
         +出憑證數，關分頁不釋放名額，只能整組釋放（屬取捨：單台釋放需裝 
         +置識別與在線偵測）。                                           
      19 +- **Rationale**：沒有邀請碼，選一個已有人的組別就能讀到該組草稿
         +與送出；常駐顯示的碼在搶答中被瞄到、或釋放後搶先以第一台加入， 
         +都會重新打開冒用。                                             
      20 +- **證偽欄｜可證偽**：`test_join_requires_code`、`test_fullwidt
         +h_code_accepted`、`test_device_limit`、`test_concurrent_join_at
         +_limit`、`test_concurrent_first_join_one_code`、`test_release_r
         +evokes_all_devices_and_code`、`test_code_rotates_on_start_and_h
         +idden_from_students`、`test_toggle_revokes_only_on_change`。   
      21  
      22  ## R3 送出：代表作答
      23  
     ...
      26  
      27  ## R4 組內草稿
      28  
      27 -- **Decision**：`POST /api/student/draft`（`X-Team-Token`，`{qu
         -estion, answers}` ⇒ `{question}`，不回顯內容）。403 憑證無效；4
         -09 非組隊、非 `answering`、本組已送出、時間計分非開放中題；404 
         -題號；422 長度≠子題數、超過 200 字、控制字元（訊息固定）；空白 
         -允許。`drafts: dict[組別, dict[題號, tuple]]`，最後寫入者為準；
         -送出、匯入、重置、釋放、切換組隊時清除。不記日誌內容。         
      29 +- **Decision**：`POST /api/student/draft`（`X-Team-Token`，`{qu
         +estion, answers}` ⇒ `{question}`，不回顯內容）。`set_draft` 在 
         +鎖內檢查與寫入。403 憑證無效；409 非組隊（「只有組隊模式可以共 
         +用草稿」）、非 `answering`、本組已送出、時間計分非開放中題；404
         + 題號；422 長度≠子題數、超過 200 字、控制字元（訊息固定）；空白
         +允許。`drafts: dict[組別, dict[題號, tuple]]`，最後寫入者為準；
         +送出、匯入、重置、釋放、切換組隊、改組數時清除。草稿與邀請碼都 
         +不記日誌。前端送出時取消未送的草稿計時器，草稿請求失敗靜默。   
      30  - **證偽欄｜可證偽**：`test_draft_rules`；`test_isolation.py::t
          est_team_draft_isolated`、`test_other_team_draft_sends_nothing`
          。
      31  
      32  ## R5 view 與作答隔離
      33  
      32 -- **Decision**：學生（有效憑證）`team_play`、`invite_code`（組 
         -隊時）、`drafts`（只在 `answering`、只含本組）；老師 `team_play
         -`、`devices`、`invite_codes`（不含草稿）；公開資訊只增 `team_pl
         -ay`；無效憑證仍只回最少資訊。草稿更新只改本組 view，他組連線不 
         -推送。                                                         
      33 -- **證偽欄｜可證偽**：`test_isolation.py` 三則（他組草稿與邀請 
         -碼不在本組 WebSocket／REST 成功與錯誤回應／公開資訊；他組草稿更
         -新時本組 seq 不跳號；判定中與已結束學生 view 無 `drafts` 鍵）。
      34 +- **Decision**：學生（有效憑證）`team_play`、`invite_code`（組 
         +隊且只在 `preparing`）、`drafts`（只在 `answering`、只含本組） 
         +；老師 `team_play`、`devices`（每組都列）、`invite_codes`（只列
         +有碼的組，含釋放後待加入者；不含草稿）；公開資訊只增 `team_play
         +`；無效憑證仍只回最少資訊。草稿更新只改本組 view，他組連線不推 
         +送。                                                           
      35 +- **證偽欄｜可證偽**：`test_isolation.py` 五則：`test_team_draf
         +t_isolated`、`test_other_team_draft_sends_nothing`、`test_draft
         +s_only_in_answering`、`test_invalid_token_gets_no_team_fields` 
         +、`test_invite_code_not_sent_to_students_while_answering`。    
      36  
      37  ## R6 web
      38  
      39  - **Decision**：老師「組別」區塊組隊勾選框（準備階段）、每組「
          已加入（n 台）」與邀請碼；首頁組隊時已加入的組別不停用、多「邀
          請碼」輸入欄；學生頁顯示本組邀請碼；作答卡輸入後 400 毫秒送草稿
          ，組內草稿與本機輸入不同時顯示「組內草稿：…」與「套用」（不覆蓋
          正在輸入的內容）。
      40  - **證偽欄｜可證偽**：`web/src/pages/team.test.tsx`。
      41 +                                                               
      42 +## R7 契約語意補充（v1.1，呈負責人批准）                       
     … 3 more lines (ctrl+o to expand)
  ⎿  Updated software_fin-speckit\specs\009-team-mode\spec.md (+8 -7)
      2  
      3  **Feature Branch**: `009-team-mode`
      4  **Created**: 2026-11-14
      5 -**Status**: Draft（v1.0）                                       
      5 +**Status**: Implemented（v1.1；契約語意補充呈負責人批准；人工驗 
        +證待執行，見 `docs/manual-verification.md` 場次 E）             
      6  **Input**: User description: "第三期做組隊模式"（負責人 2026-11-
         14）；TRD §6 裁定「代表作答：組內任一人送出即代表全組，其餘組員
         看得到組內草稿；不採分數平均」（2026-11-12）
      7  **需求編號**：X-04（`docs/trd-game-modes.md` M4）｜**parity**：`
         docs/parity.md` §4 `team-mode`｜**檔位**：S（作答隔離：新增送往
         學生端的草稿通道；`contracts/` 增端點與欄位；組別憑證口徑改變）
      8  **圖表**：`diagrams/009-team-mode-{component,class,sequence}.pum
         l`
     ...
      11  
      12  ### User Story 1 - 老師開啟組隊，組員以邀請碼加入同一組 (Priori
          ty: P1)
      13  
      14 -準備階段老師勾選「組隊（一組多台裝置）」。每組第一位組員選組後 
         -，畫面顯示 6 碼邀請碼；其他組員在首頁選同一組並輸入邀請碼才能加
         -入。每組最多 6 台。                                            
      14 +準備階段老師勾選「組隊（一組多台裝置）」。每組第一位組員選組後 
         +，畫面顯示 6 碼邀請碼；其他組員在首頁選同一組並輸入邀請碼才能加
         +入。每組最多 6 台。學生只在準備階段看得到邀請碼；開始搶答時邀請
         +碼換新，搶答中要加入的組員向老師索取。                         
      15  
      16  **Why this priority**: 沒有邀請碼，任何人選一個已有人的組別就能
          讀到該組草稿與送出——第一期「一組一台」擋掉的冒用會重新打開。
      17  
     ...
      21  
      22  1. **Given** 準備階段，**When** 老師開啟組隊，**Then** 所有已加
          入裝置失效，老師與公開資訊的 `team_play` 為 true。
      23  2. **Given** 組隊、第1組已有一台，**When** 另一台不帶或帶錯邀請
          碼選第1組，**Then** 回 403「邀請碼不正確」，台數不變。
      24 -3. **Given** 同上，**When** 帶正確邀請碼（大小寫不拘、可有前後 
         -空白），**Then** 取得第1組憑證。                               
      24 +3. **Given** 同上，**When** 帶正確邀請碼（大小寫、全半形不拘、 
         +可有空白），**Then** 取得第1組憑證。                           
      25  4. **Given** 第1組已有 6 台，**When** 第 7 台帶正確碼加入，**Th
          en** 回 409「此組裝置已滿（最多 6 台）」；並發加入不超過 6 台。
      26  5. **Given** 搶答中，**When** 老師切換組隊，**Then** 回 409。
      27 -6. **Given** 組隊、第1組 3 台，**When** 老師釋放第1組，**Then**
         - 3 台全部失效，舊邀請碼不能再用。                              
      27 +6. **Given** 組隊、第1組 3 台，**When** 老師釋放第1組，**Then**
         + 3 台全部失效；不帶碼或帶舊碼加入第1組回 403，帶老師畫面上的新 
         +碼可加入。                                                     
      28 +7. **Given** 組隊、準備階段的邀請碼，**When** 老師開始搶答，**T
         +hen** 舊碼失效、學生畫面不再含邀請碼，老師畫面的新碼可加入。   
      29  
      30  ---
      31  
     ...
      69  ### Functional Requirements
      70  
      71  - **FR-001**: 老師 MUST 能在 `preparing` 開關組隊（`POST /api/t
          eacher/team-play {enabled}`）；其他階段 409；值改變時撤銷所有憑
          證與邀請碼；重置保留。
      71 -- **FR-002**: 組隊時同組第二台起 MUST 帶相符邀請碼（403），每組
         -最多 6 台（409）；邀請碼 6 碼、只出現在本組學生畫面與老師畫面。
      72 -- **FR-003**: 釋放 MUST 撤銷該組全部憑證並作廢邀請碼。         
      72 +- **FR-002**: 組隊時該組有邀請碼後，加入 MUST 帶相符邀請碼（403
         +），每組最多 6 台（409，先比對碼再檢查上限）；學生畫面 MUST 只 
         +在 `preparing` 含本組邀請碼，老師畫面一直含現行碼；開始搶答 MUS
         +T 換新所有邀請碼。                                             
      73 +- **FR-003**: 釋放 MUST 撤銷該組全部憑證、清草稿並換新邀請碼（ 
         +新碼只在老師畫面）。                                           
      74  - **FR-004**: 送出規則 MUST 與 003 相同；同組並發送出同一題 MUS
          T 恰一筆成功。
      75  - **FR-005**: `POST /api/student/draft {question, answers}` MUS
          T 只在組隊、`answering`、本組未送出該題（時間計分另限開放中那一
          題）時接受；草稿 MUST 只出現在本組 `answering` 階段的學生畫面。
      76  - **FR-006**: 草稿 MUST 在該題送出、重置、重新匯入、釋放、切換
          組隊時清除；MUST NOT 計分或匯出。
      76 -- **FR-007**: 組隊關閉時所有行為 MUST 與 001–008 相同；`contrac
         -ts/api.md` 只增不改。                                          
     … 4 more lines (ctrl+o to expand)
  ⎿  … 1 more file changed

● Bash(cd /c/workspace/software_fin/software_fin-speckit; python - <<'EOF'
      from pathlib import Path…)
  ⎿  diagrams: 28 個圖檔已轉 PNG
     gate-diagrams: 28 個圖檔，0 處問題
  ⎿  Updated software_fin-speckit\diagrams\009-team-mode-class.puml (+5 -4)
       7    - _codes : dict[str, str]  ' 組別 → 6 碼邀請碼
       8    + drafts : dict[str, dict[int, tuple[str, ...]]]
       9    + set_team_play(enabled)  ' 只在 preparing；值改變時撤銷憑證
          與邀請碼
      10 -  + join(team, code=None) : str  ' 先比對邀請碼、再檢查 MAX_DEV
         -ICES                                                           
      11 -  + release(team)  ' 撤銷整組憑證、刪邀請碼、清草稿            
      10 +  + join(team, code=None) : str  ' 有碼就須帶碼（NFKC 後位元組 
         +比對）；先比對碼、再檢查 MAX_DEVICES                           
      11 +  + release(team)  ' 撤銷整組憑證、清草稿；組隊時換新碼（只在老
         +師 view）                                                      
      12 +  + start()  ' 組隊時換新所有邀請碼                            
      13    + devices(team) : int
      14    + invite_code(team) : str | None
      15    + set_draft(team, number, answers)
      15 -  + submit(team, number, answers)  ' 不改；成功後清該組該題草稿
      16 +  + submit(team, number, answers)  ' 判定口徑不變；成功後清該組
         +該題草稿                                                       
      17  }
      18  
      19  class InviteCodeError <<Exception>>
     ...
      22  
      23  class views_module <<module>> {
      24    + teacher_view(a)  ' team_play、devices、invite_codes
      24 -  + student_view(a, team)  ' team_play、invite_code、drafts（只
         -在 answering）                                                 
      25 +  + student_view(a, team)  ' team_play、invite_code（只在 prepa
         +ring）、drafts（只在 answering）                               
      26  }
      27  
      28  Activity ..> InviteCodeError : 403
  ⎿  Updated software_fin-speckit\diagrams\009-team-mode-sequence.puml (+9 
     -0)
      23  App -> Act : join：compare_digest 相符、未滿 6 台 → 發憑證
      24  App --> B : {team, token}
      25  
      26 +T -> App : POST /api/teacher/start                             
      27 +App -> Act : start()：組隊時換新所有邀請碼                     
      28 +App -> V : 學生 view 不再含 invite_code；老師 view 有新碼      
      29 +                                                               
      30  == 搶答中 ==
      31  A -> App : POST /api/student/draft {question: 3, answers}
      32  App -> Act : set_draft(第1組, 3, answers)（組隊、answering、未
          送出）
     ...
      40  App --> A : 推播 my_submissions 含第 3 題
      41  A -> App : POST /api/student/submit {question: 3, ...}
      42  App --> A : 409 本組已送出這一題，不可修改
      43 +                                                               
      44 +T -> App : POST /api/teacher/release {team: 第1組}             
      45 +App -> Act : release(第1組)：撤銷 A、B 憑證、清草稿、換新碼（只
         +在老師 view）                                                  
      46 +A -> App : POST /api/student/join {team: 第1組, 舊碼}          
      47 +App --> A : 403 邀請碼不正確                                   
      48  @enduml
  ⎿  Updated software_fin-speckit\specs\009-team-mode\plan.md (+1 -1)
      28  | 原則 | 本功能如何符合 | 結果 |
      29  |---|---|---|
      30  | I 需求即法律、兩組一致 | X-04；parity §4 `team-mode`；OpenSpe
          c 組同批 `team-mode` change | ✅ |
      31 -| II 作答隔離 | 草稿與邀請碼只進本組 view；新增三則傳輸內容負例
         - | ✅ |                                                        
      31 +| II 作答隔離 | 草稿只進本組 view、邀請碼只在準備階段給本組；新
         +增五則傳輸內容負例 | ✅ |                                      
      32  | III 順位以伺服器為準 | 送出沿用 003 的鎖與序號；同組並發測試 
          | ✅ |
      33  | IV Guided Notes 動態定位 | 不讀寫 Guided Notes | ✅ |
      34  | V 測試先行與人工驗證 | `test_team_mode.py`、隔離負例先寫；人
          工驗證場次 E | ✅ |
  ⎿  … 2 more files changed
  ⎿  (timeout 10m)

● Now parity status/§5 for v1.1 (both repos), then the verification records.

● Bash(cd /c/workspace/software_fin; python - <<'EOF'
      from pathlib import Path…)
  ⎿  same
  ⎿  Updated software_fin-speckit\docs\parity.md (+2 -1)
      47  | `question-settings` | X-04 | 準備階段老師可把任一題設為**雙倍
          分數**（倍率 1 或 2），任何模式下該題得分 ×2；重新匯入即清除、
          重置活動保留；學生看得到哪些題是雙倍；分數欄名在全部倍率為 1 的
          經典搶答顯示「得題數」，其餘顯示「得分」（TRD T-05 倍率） | 已
          合入 | 已合入 |
      48  | `mode-buzz-fallback` | X-03、X-04 | 搶答＋錯誤遞補：最先送出
          者判錯則依順位遞補（TRD M1） | 未開 | 未開 |
      49  | `mode-timed-scoring` | X-04 | **時間計分**模式：老師逐題開放
          ，每題時限 5–120 秒（預設 20，準備階段設定），到時伺服器關閉該
          題、老師也可提早結束；只收開放中那一題；老師判定該題後揭曉；正
          確得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（以整數運算 `
          (2001 × T − 作答毫秒) // (2 × T)` 實作，避免浮點誤差）（t ≤ 0.5
           秒得滿分，t 為伺服器量得的作答秒數）；揭曉後學生看到本組該題對
          錯與得分、本組累積分數，以及全部組別的累積**名次**（不含他組分
          數，以免反推作答秒數）；他組答案、分數仍只在活動結束後才看得到
          （TRD M2、T-04、T-05 時限） | 已合入 | 已合入 |
      50 -| `team-mode` | X-04 | **組隊**（活動設定，可與任一模式搭配，只
         -在準備階段切換）：一組最多 6 台裝置，同組第二台起須輸入該組 6  
         -碼邀請碼（只顯示在本組與老師畫面）；組內任一人送出即代表全組， 
         -每組每題仍只送出一次；搶答中組員看得到本組草稿（不計分、不匯出 
         -，老師與他組看不到）；切換組隊、改組數、釋放某組都撤銷相關裝置 
         -（TRD M4，§6 裁定）；第三期 | 提案中 | 提案中 |                
      50 +| `team-mode` | X-04 | **組隊**（活動設定，可與任一模式搭配，只
         +在準備階段切換）：一組最多 6 台裝置，同組有邀請碼後加入須帶碼（
         +6 碼，不分大小寫與全半形；學生只在準備階段看得到本組碼，開始搶 
         +答與老師釋放某組時換新，搶答中向老師索取）；組內任一人送出即代 
         +表全組，每組每題仍只送出一次；搶答中組員看得到本組草稿（不計分 
         +、不匯出，老師與他組看不到）；切換組隊、改組數、釋放某組都撤銷 
         +相關裝置（TRD M4，§6 裁定）；第三期 | 已實作（待合入） | 已實作
         +（待合入） |                                                   
      51  
      52  狀態值：未開／提案中／實作中／已實作（待合入）／已合入。
      53  
     ...
      67  | 2026-11-12 | 第二期三卡 | 兩組皆合入 `dev`（OpenSpec #9–#11；
          SpecKit #8–#10），`dev` 上 server、web 逐字相同；人工驗證待補驗
           | 兩組 | 已確認 |
      68  | 2026-11-14 | 第二期三卡 | 負責人批准契約語意補充三處（經典得
          主得 1×倍率分、`team_scores` 欄名看 `score_label`；設定 API 兩
          欄位可選；時間計分在 `answering` 內判定），並確認兩處落實方式（
          學生端排行榜只公開名次；時間計分活動前不先發學習單） | 兩組（負
          責人裁定） | 已確認 |
      69  | 2026-11-14 | `team-mode` | 負責人指示第三期做組隊；開卡 v1.0
          ：組隊做成與模式正交的活動設定（非第四種模式），同組第二台起憑
          邀請碼加入，組內草稿只給本組 | 兩組（負責人指示） | 同一會話兩
          組同批起稿 |
      70 +| 2026-11-14 | `team-mode` | 提案輪評審（v1.1）：邀請碼只在準備
         +階段給學生、開始搶答與釋放即換新碼；全形輸入正規化；契約四處語 
         +意補充（身分表、join、release、改組數）呈負責人批准；兩組實作完
         +成、程式碼一致 | 兩組 | 同一會話兩組同批修訂；語意補充待負責人 
         +批准 |                                                         

  Ran 1 shell command (ctrl+o to expand)

● Both repos fully green. Writing the verification records.

● Write(software_fin-openspec\openspec\changes\team-mode\verification.md)
  ⎿  Wrote 65 lines to
     software_fin-openspec\openspec\changes\team-mode\verification.md
       1 # team-mode — verification（v1.1）
       2 
       3 ## 設計決策 → 實作落點
       4 
       5 | 決策 | 落點 |
       6 |---|---|
       7 | D1 組隊開關 | `server/quiz_server/activity.py`「`async def set
         _team_play`」、「`def _revoke_all`」；`app.py`「`/api/teacher/te
         am-play`」 |
       8 | D2 邀請碼 | `activity.py`「`def normalize_code`」、「`async de
     … +58 lines (~2 KB) (ctrl+o to expand)

● Write(software_fin-speckit\specs\009-team-mode\verification.md)
  ⎿  Wrote 52 lines to
     software_fin-speckit\specs\009-team-mode\verification.md
       1 # Verification: 009 team-mode（v1.1）
       2 
       3 ## 圖碼一致核對（憲章原則 VII）
       4 
       5 | 圖 | 圖上元素／訊息 | 程式落點 | 結果 |
       6 |---|---|---|---|
       7 | component | TeamSettings 組隊勾選・台數・邀請碼 | `web/src/pag
         es/Teacher.tsx`「組隊（一組多台裝置）」 | 一致 |
       8 | component | Home 邀請碼輸入欄 | `web/src/pages/Home.tsx` `Team
         Picker` | 一致 |
     … +44 lines (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; sed -i 's/- \[ \] 3.1
      /- [x] 3.1 /; s/- \[ \] 3.2 /- [x] 3.2 /'
      openspec/changes/team-mode/tasks.md; sed -i…)
  ⎿  550ae9f feat(server): [CORE] team-mode
     組隊：邀請碼加入、代表作答、組內
     草稿
     c5b84f9 docs(openspec): team-mode 提案 v1.1（提案輪評審） [CORE]
     … +5 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\tasks.md (+2 
     -2)
      12  - [x] 2.3 web：老師組隊開關與台數／邀請碼、首頁邀請碼欄、學生頁
          邀請碼與組內草稿
      13  
      14  ## 3. 驗證
      15 -- [ ] 3.1 `make gate` 原樣輸出、變異實錄、人工驗證步驟寫入 `ver
         -ification.md` 與 `docs/manual-verification.md` 場次 E          
      16 -- [ ] 3.2 `docs/parity.md` 狀態更新、`make gate-parity` 綠     
      15 +- [x] 3.1 `make gate` 原樣輸出、變異實錄、人工驗證步驟寫入 `ver
         +ification.md` 與 `docs/manual-verification.md` 場次 E          
      16 +- [x] 3.2 `docs/parity.md` 狀態更新、`make gate-parity` 綠     

● Both repos committed. Sending each reviewer back for (a) re-verification of
  its own remedies and (b) the implementation round (final round, diff-scoped).
  ⎿  Resuming agent a029e22
  ⎿  Resuming agent ae3a560

● While both reviews run, preparing the PR descriptions — checking the template.

● Bash(cd /c/workspace/software_fin/software_fin-openspec; cat
      .github/pull_request_template.md; gh pr list --state merged --limit 3
      --json number,title | head -20)
  ⎿  檔位：S / B / C（理由：）
     評審閉環否：
     測試與門禁綠否：
     … +38 lines (ctrl+o to expand)
  ⎿  (another command ran in this repository at the same time; a change 
     made by either may show under either result)

● Waiting on the two reviewers before drafting PR bodies (their verdicts go into
  the "評審閉環否" line).

✻ Crunched for 36m 44s · done Saturday 7:14 PM

› Message from general-purpose
  一句話結論：我上輪開的四帖藥方在兩組都已落地，實作輪沒有阻斷項，也沒有淨回歸或
  讓原修復失效的問題。剩 1 個次要：SpecKit 有一段文件寫法過時，不影響行為。

  藥方回驗：
  - 發現 1（邀請碼常駐學生畫面）已修。views.py 只在 preparing 帶
  invite_code；activity.py 的 start 換新所有碼，release 也換新碼，新碼只在老師
  view；Student.tsx 搶答中改提示向老師索取；契約學生 view 段也同步了。
  - 發現 2（契約語意補充沒列出）已修。contracts/api.md
  的身分表、join、release、teams 四處標了「team-mode 語意補充」；design D7 與
  SpecKit research R7 逐條列出；product-trd §3 已補；parity
  歷史記為「待負責人批准」。
  - 發現 3（全形輸入導致 500）已修。normalize_code 先做
  NFKC、去空白、轉大寫，再以位元組 compare_digest 比對；非 ASCII
  只會比對失敗，不會拋例外。
  - 發現 4（台數算憑證數、只能整組釋放）已修。design D2 第 26 行與 research R2
  都寫明「屬取捨」及理由：單台釋放需要裝置識別與在線偵測。
  - followup 六項我都核到了落點：set_draft 在鎖內、前端 cancelDraft、design
  開頭寫明負載量級屬取捨、邀請碼不記日誌、D5 與 R5 的鍵一致、D3 改寫。

  發現 1｜次要
    哪兒：speckit specs/009-team-mode/research.md 的 R6
  段（「學生頁顯示本組邀請碼」）；diagrams/009-team-mode-component.puml:15
    什麼錯：R6 沒跟著 v1.1 補「只在準備階段」。OpenSpec D6 第 59 行、SpecKit
  R5、程式和類別圖都已改；組件圖寫「學生
  invite_code・drafts（answering、本組）」，讀起來像邀請碼在搶答中也給學生。
    會怎樣：日後照 R6
  或組件圖維護的人，可能把邀請碼又改回常駐顯示，重新打開上輪發現 1
  的冒用。目前行為正確。
    怎麼修：R6 和組件圖改成「invite_code 只在 preparing；drafts 只在
  answering」。
    證據：git show 83ce667:diagrams/009-team-mode-component.puml | grep -n
  invite → 15 行。

  其他核對（都成立）：
  - 兩組 server/、web/src、contracts 逐字相同：用 git ls-tree 比對
  blob，結果一致。
  - 矩陣 M-017～M-019 列的 18 個守門測試名稱，在 550ae9f
  都恰好存在一次。我沒有親跑測試；227 passed 是 coordinator 的自報，我沒核。
  - 契約與 join、release、team-play、draft
  的錯誤碼與訊息一致，包括「先比對邀請碼、再查上限」的順序。
  - 場次 E 第 2～7 步與介面文案、換碼行為相符。
  - SpecKit 時序圖新增的 start 換碼、release 換碼兩段與 activity.py 一致。

  followup（不擋）：準備階段瞄到邀請碼就加入的冒用者，開始搶答後憑證不會被撤銷，
  只有換碼，所以會一直留在該組。老師只能從台數看出異常。建議 design
  補一句說明這是殘餘風險。

  外包檢查：A-5「make gate-diagrams 28 個 0 處問題」和 A-6「227
  passed」都是自報輸出，稿內 verification.md 有沒有原樣貼出，我沒逐行核。

  我查閱的檔案：git diff 04b77d3 550ae9f（server/quiz_server/*、contracts/api.md
  、docs/{manual-verification,parity,product-trd}.md、eval/acceptance/matrix.yam
  l、web/src/pages/{Home,AnswerForm,Student}.tsx、openspec design.md
  的定點）；git diff 6865239
  83ce667（diagrams/009-*.puml、specs/009-team-mode/research.md）；兩倉 ls-tree
  比對結果。
  CLEARED

● Architecture channel: CLEARED (one minor doc fix). Applying it plus the
  residual-risk note now.

● Bash(cd /c/workspace/software_fin; python - <<'EOF'
      from pathlib import Path…)
  ⎿  diagrams: 28 個圖檔已轉 PNG
     gate-diagrams: 28 個圖檔，0 處問題
  ⎿  Updated software_fin-openspec\openspec\changes\team-mode\design.md (+1
     -0)
      23    3. 組隊開啟且該組**沒有邀請碼**（從未有人加入）：發憑證並產生
          邀請碼。
      24  - **開始搶答即換新所有邀請碼**（`start`）：準備階段被他組瞄到的
          碼在搶答中失效；搶答中要加入的組員只能向老師索取（老師 view 永
          遠有現行碼）。
      25  - `release(team)`：撤銷該組全部憑證、清該組草稿；組隊時**換新邀
          請碼**（只在老師 view）。被踢的冒用者不能搶先以「第一台」重新佔
          住該組。
      26 +- 殘餘風險：準備階段已憑碼加入的冒用者，開始搶答換碼後憑證不會 
         +被撤銷，仍留在該組；老師可從台數看出異常並釋放整組。           
      27  - `devices(team)`＝該組已發出的憑證數。憑證存在分頁的 sessionSt
          orage，關分頁不會釋放名額；名額不夠時老師只能釋放整組、組員以新
          碼重新加入（屬取捨：單台釋放需要裝置識別與在線偵測，超出本卡範
          圍；6 台高於一般分組人數）。
      28  
      29  - 證偽欄｜可證偽：`test_team_mode.py::test_join_requires_code`
          （無碼、錯碼、截短碼 403 且不發憑證；小寫與前後空白可）、`test_
          fullwidth_code_accepted`、`test_single_device_without_team_play
          _unchanged`、`test_device_limit`（滿後錯碼仍 403）、`test_concu
          rrent_join_at_limit`（6 台後並發 5 次恰 0 成功；5 台後恰 1 成功
          ）、`test_concurrent_first_join_one_code`、`test_release_revoke
          s_all_devices_and_code`（釋放後無碼、舊碼 403，新碼可加入）、`t
          est_code_rotates_on_start_and_hidden_from_students`。
  ⎿  (timeout 10m)

● Agent "Architecture proposal review team-mode" finished · 1m 8s
● Architecture fix applied and diagrams re-rendered. Waiting for the red-team
  implementation-round result.

✻ Brewed for 24s · done Saturday 7:16 PM

› Message from general-purpose
  一句話結論：我上一輪的兩項修正都落實了，而且我自己做的變異實驗兩項都會讓測試變
  紅；實作輪定點掃描沒有找到淨回歸、讓原修復失效或掩蓋原病的假綠。可以放行。

  藥方回驗：
  - 發現 1（釋放後別人可以不帶碼搶先佔住該組）→ 已落實。activity.py 的 `release`
  在組隊時改為立即換新碼；`join` 的 `known is not None`
  分支讓「曾被釋放、目前沒有裝置」的組別也必須帶碼。我把 `release`
  改回「刪除邀請碼」→ `test_release_revokes_all_devices_and_code` 變紅。
  - 發現 2（全形輸入讓比對拋例外、回 500）→ 已落實。`normalize_code`
  先做全形轉半形，再去空白、轉大寫，最後以位元組比對。我把它改回直接比對字串 →
  `test_fullwidth_code_accepted` 拋 TypeError、變紅。
  - 跟進項「草稿寫入與送出同一把鎖」→ 已落實：`set_draft` 和 `submit` 都在
  `_lock` 內檢查並寫入，送出成功時順手清掉該組該題草稿。

  實作輪：沒有發現。我核過下列幾點：
  - 交錯操作下的冒用：`join`、`release`、`set_team_play`、`start`
  全部在同一把鎖內。開始搶答時只換已存在的碼，從沒有人加入過的組別仍不用碼，這和
  第一期「先到先得」相同，不是新洞。重置回準備階段時，學生畫面重新出現的是現行碼
  ，下一次開始搶答又會換新。
  - 外洩管道：加入失敗的訊息固定，回應先 403 後 409；草稿 API
  只回題號；兩者都不寫日誌。公開資訊只多了組隊開關。學生畫面只在準備階段帶本組邀
  請碼、只在搶答中帶本組草稿；憑證無效時只回四個鍵；老師畫面不含草稿。
  - 前端：學生頁只顯示伺服器推來的本組草稿；草稿送出失敗時靜默不提示；送出後取消
  尚未送出的草稿。
  - 契約四處語意補充：與實作一致，兩組規格、類別圖、時序圖也與實作一致，SpecKit
  的 verification.md 也標為一致。批准仍待負責人。

  followup（一行）：時間計分下，`set_draft` 只檢查回合是否已關閉，沒有像
  `submit` 那樣再比對時限。從時限到、到計時器真正關閉的那幾毫秒內，仍收得進草稿
  ，但只有本組自己看得到，不影響判定公平。

  證據：把 550ae9f 的 `server` 和 `tests` 匯出到暫存目錄，`uv run --project
  server pytest -q server/tests` → 227 passed；兩項變異 → 3
  failed（release、fullwidth、draft_cleared_on_release_and_reset）。這兩則測試是
  真的能抓到問題，不是假綠。

  我查閱的檔案：
  - OpenSpec：`git diff 04b77d3 550ae9f`（server/quiz_server/{activity,app,views
  }.py、server/tests/{test_isolation,test_team_mode}.py、web/src/{api.ts,pages/H
  ome,Student,AnswerForm.tsx}、contracts/api.md），以及
  openspec/changes/team-mode 下 design、proposal、verification 的落點行。
  - SpecKit 83ce667：specs/009-team-mode/{spec,plan,research,data-model,contract
  s/README,verification}.md、diagrams/009-team-mode-{class,sequence}.puml。

  CLEARED

● Both channels CLEARED. Writing the review record (shared in both repos) and
  committing.

● Write(software_fin-openspec\docs\reviews\2026-11-14-team-mode-review.md)
  ⎿  Wrote 29 lines to
     software_fin-openspec\docs\reviews\2026-11-14-team-mode-review.md
      1 # 第三期評審紀錄：team-mode（2026-11-14）
      2 
      3 - 對象：S 檔卡 `team-mode`（兩組同批：OpenSpec change `team-mode`
        、SpecKit `009-team-mode`）。
      4 - 方式：提案輪＋實作輪各一輪，紅隊與架構兩通道互不知情（`.claude/
        agents/finder-tail-{red,arch}.md`＋`review-dispatch` 骨架）；藥方
        由各自開方的通道回驗。
      5 - 結論：
      6   - 提案輪（v1.0）：紅隊 `NOT CLEARED(0B/1M/1m)`、架構 `NOT CLEAR
        ED(0B/2M/2m)`；藥方併入 v1.1。
     … +23 lines (ctrl+o to expand)

● Agent "Red-team proposal review team-mode" finished · 2m 40s

● Bash(cd /c/workspace/software_fin; cp
      software_fin-openspec/docs/reviews/2026-11-14-team-mode-review.md
      software_fin-speckit/docs/reviews/; for r in software_fin-ope…)
  ⎿  d2b8411 docs: [CORE] team-mode
     實作輪評審藥方（文件一致、殘餘風險）；第
     三期評審紀錄
     gate-zh-hant: 0 處簡體字
     … +11 lines (ctrl+o to expand)
  ⎿  Created
     software_fin-speckit\docs\reviews\2026-11-14-team-mode-review.md (+29 
     -0)
       1 +# 第三期評審紀錄：team-mode（2026-11-14）                      
       2 +                                                               
       3 +- 對象：S 檔卡 `team-mode`（兩組同批：OpenSpec change `team-mod
         +e`、SpecKit `009-team-mode`）。                                
       4 +- 方式：提案輪＋實作輪各一輪，紅隊與架構兩通道互不知情（`.claud
         +e/agents/finder-tail-{red,arch}.md`＋`review-dispatch` 骨架）；
         +藥方由各自開方的通道回驗。                                     
       5 +- 結論：                                                       
       6 +  - 提案輪（v1.0）：紅隊 `NOT CLEARED(0B/1M/1m)`、架構 `NOT CLE
         +ARED(0B/2M/2m)`；藥方併入 v1.1。                               
       7 +  - 實作輪（末輪，含藥方回驗）：紅隊 `CLEARED`（另以兩則變異自 
         +證守門測試會紅）；架構 `CLEARED`（另 1 次要：SpecKit R6 與組件 
         +圖未寫「邀請碼只在準備階段」，已修）。兩通道閉環。             
       8 +                                                               
       9 +## 提案輪發現與藥方                                            
      10 +                                                               
      11 +| 通道 | 等級 | 發現 | 藥方落點 |                              
      12 +|---|---|---|---|                                              
      13 +| 紅隊 | 重要 | 釋放後該組回到「無裝置」，任何人不帶碼即可以第 
         +一台搶佔，新碼還顯示在冒用者畫面 | 釋放即換新碼、只在老師 view 
         +；有碼就須帶碼（design D2；`test_release_revokes_all_devices_an
         +d_code`） |                                                    
      14 +| 紅隊 | 次要 | 全形輸入使 `compare_digest` 拋例外、回 500 | NF
         +KC 後以位元組比對（`normalize_code`；`test_fullwidth_code_accep
         +ted`） |                                                       
      15 +| 架構 | 重要 | 邀請碼常駐學生畫面且搶答中可加入，瞄到 6 碼即可
         +冒用 | 學生只在準備階段看得到；開始搶答換新所有碼（design D2、D
         +5；`test_code_rotates_on_start_and_hidden_from_students`、`test
         +_invite_code_not_sent_to_students_while_answering`） |         
      16 +| 架構 | 重要 | 契約身分表、join、release 的語意改變被寫成「純 
         +新增」，繞過負責人批准 | design D7／research R7 逐條列四處語意 
         +補充，**呈負責人批准** |                                       
      17 +| 架構 | 次要 | 同紅隊次要 | 同上 |                            
      18 +| 架構 | 次要 | 台數算憑證數、關分頁不釋放名額、只能整組釋放 | 
         +列為取捨並寫明理由（design D2、research R2） |                 
      19 +                                                               
      20 +## followup（不阻塞）                                          
      21 +                                                               
      22 +- 準備階段已憑碼加入的冒用者，開始搶答換碼後憑證不撤銷；老師可 
         +從台數看出並釋放整組（已寫入 design D2 殘餘風險）。            
      23 +- 時間計分下 `set_draft` 只看回合是否關閉、不比對時限；時限到與
         +計時器關閉之間的數毫秒仍收草稿，只有本組看得到，不影響判定。   
      24 +- 首頁只在載入時讀一次公開資訊，老師切換組隊後學生要重新整理首 
         +頁（同第一期）。                                               
      25 +                                                               
      26 +## 呈負責人                                                    
      27 +                                                               
      28 +1. `contracts/api.md` 四處語意補充（身分表一組多台；join 帶 `co
         +de`、403、組隊時 409 指已滿；release 換新碼；改組數清碼與草稿）
         +——我傾向批准：組隊關閉時與第一期完全相同。                     
      29 +2. 人工驗證（P-05）：`docs/manual-verification.md` 場次 E，交組
         +員執行。                                                       
  ⎿  (timeout 5m)

● Adding the rollback tag and ops-log entry per the project's convention.

  Ran 1 shell command (ctrl+o to expand)

● Everything is committed. Drafting the six PR descriptions to the scratchpad so
  the PRs can be opened right after you push.

  Ran 1 shell command (ctrl+o to expand)

● Write(~\.claude\projects\C--workspace\memory\software-fin-todo.md)
  ⎿  Added 11 lines, removed 6 lines
       5    type: project
       6  ---
       7  
       8 -Updated 2026-11-14. Owner said on 2026-11-14: delete phase-2 br
         -anches, approve the five pending points, do phase 3 (team-mode)
         -, open a card that collects all manual verification for teammat
         -es, archive the rest, and add a product TRD for newcomers.     
       8 +Updated 2026-11-14 (end of session). On 2026-11-14 the owner sa
         +id: delete the phase-2 branches, approve the five pending point
         +s, do phase 3, collect all manual verification into one card fo
         +r teammates, archive everything else, and write a product TRD f
         +or newcomers. All of that is done locally.                     
       9  
      10 -Done 2026-11-14: phase-2 branches deleted (local+remote via gh 
         -api); approvals recorded; OpenSpec phase-2 changes archived; AI
         - log 2026-11-12 added to docs/ai-logs.                         
      10 +Local stacked branches, all committed and gates green, waiting 
         +for the owner to push with `!` (agents cannot push):           
      11 +- OpenSpec: docs/phase2-closeout → docs/team-handoff → feat/tea
         +m-mode, plus tag rollback/03-pre-phase3                        
      12 +- SpecKit: docs/phase2-closeout → docs/team-handoff → 009-team-
         +mode, plus the same tag                                        
      13 +- PR bodies are drafted in the session scratchpad (prs/closeout
         +.md, handoff.md, team.md). After the push: open 3 stacked PRs p
         +er repo, link the two repos' PRs to each other, and merge only 
         +when the owner says "合" (retarget each PR to dev first; do not
         + delete branches until the whole stack is merged).             
      14  
      12 -Local stacked branches waiting for the owner to push with `!` (
         -pushing is agent-denied):                                      
      13 -- both repos: `docs/phase2-closeout` → `docs/team-handoff` (pro
         -duct-trd.md + manual-verification.md; C-tier review CLEARED aft
         -er one fix round)                                              
      14 -- OpenSpec `feat/team-mode`, SpecKit `009-team-mode` stacked on
         - docs/team-handoff: proposal v1.0 committed; proposal-round dua
         -l review dispatched, then implement → impl review → PRs.       
      15 +Still open:                                                    
      16 +1. The owner must approve the 4 contract semantic additions for
         + team-mode (design D7 / research R7). This blocks merging.     
      17 +2. Manual verification P-05: teammates run docs/manual-verifica
         +tion.md scenes A–E and fill in the results table.              
      18 +3. /export the 2026-11-14 session into docs/ai-logs (scan it fo
         +r secrets first).                                              
      19 +4. Optional card: show question text in timed mode.            
      20  
      16 -Still open: manual verification P-05 (teammates use docs/manual
         --verification.md; scene E added when team-mode lands); /export 
         -of the 2026-11-14 session into docs/ai-logs; optional card "sho
         -w question text in timed mode". Deadline 2026-11-30. Related: [
         -[software-fin-project]]                                        
      21 +Deadline 2026-11-30. Related: [[software-fin-project]]         

● 你交代的事都做完了，兩組都已 commit，門禁全綠。不過還沒推到
  GitHub：我被設定擋住不能 push，要你來推。另外第三期有一件事要你批准才能合入。

  做好的事
  - 刪分支：第二期六支分支（本地＋遠端）已刪。刪之前逐支確認過內容都已在 dev
    裡。
  - 批准記錄：五處都記進 parity、TRD 和評審紀錄了。
  - 歸檔：OpenSpec 第二期三個 change 已歸檔。parity
    三張卡改成「已合入」，ops-log 也補上了。11/12
    的對話紀錄先掃過沒有權杖和個資，再放進 docs/ai-logs/。
  - 人工驗證手冊（docs/manual-verification.md）：八張卡加上第三期，整理成 A 到 E
    五個場次，附準備步驟、記錄方式和結果表，可以直接交給組員。
  - 產品 TRD（docs/product-trd.md）：寫給第一次看專案的人，有一句話介紹、流程圖
    、功能一覽、七項特色、架構和閱讀路線。README 也加了連結。
  - 第三期組隊模式：
    - 組隊做成活動設定，可以和任一模式一起開。一組最多 6
      台裝置，第二台起要輸入該組的 6 碼邀請碼。
    - 組內任一人送出就代表全組，每題還是只能送一次。搶答中組員看得到本組草稿，老
      師和他組看不到。
    - 紅隊和架構兩邊各評兩輪，最後都通過。提案輪抓到兩個冒用漏洞，已經修掉：
      - 老師釋放某組後，任何人都能不帶碼搶先以第一台加入。現在釋放會換新碼，新碼
        只顯示在老師畫面。
      - 邀請碼一直顯示在學生畫面上，搶答中被他組瞄到就能加入。現在學生只在準備階
        段看得到，開始搶答時邀請碼會換新。
    - 測試：server 227、web 33
      全過；另外故意把八處檢查改壞，對應的測試都會失敗。

  要你處理的事
  1. 推送（PowerShell 寫法）：
  ! cd C:\workspace\software_fin\software_fin-openspec; git push -u origin 
  docs/phase2-closeout docs/team-handoff feat/team-mode rollback/03-pre-phase3
  ! cd C:\workspace\software_fin\software_fin-speckit; git push -u origin 
  docs/phase2-closeout docs/team-handoff 009-team-mode rollback/03-pre-phase3
     推完之後我開六個疊層 PR，PR 描述已經擬好。等你說「合」才會合併。
  2. 批准契約的四處語意補充，這會擋住組隊的合入。組隊模式改了契約上原有的幾句話
     ：
     - 「一組一台裝置」改成組隊時最多 6 台。
     - 加入組別要帶邀請碼，碼錯回 403，組隊時 409 改成「裝置已滿」。
     - 組隊時釋放某組會換新邀請碼。
     - 改組數時會清掉邀請碼和草稿。

     組隊沒開的時候，所有行為和第一期完全一樣。我傾向批准。
  3. 人工驗證：把手冊交給組員，照 A 到 E 五個場次跑並填結果表。
  4. 匯出今天的對話紀錄：用 /export，我會先掃過個資再放進 docs/ai-logs/。

  待辦清單已經更新到記憶裡，下次開 session 我會先提醒你。

✻ Worked for 40m 38s · done Saturday 7:18 PM

※ recap: 你要的收尾、交接文件和第三期組隊模式，兩組都做完並 commit 了，測試全綠，現在等你推送。下一步請你用 `!` 執行我給的兩行 git push 指令，並批准契約的四處語意補充。 (disable recaps in /config)

!  cd C:\workspace\software_fin\software_fin-openspec; git push -u origin       
  docs/phase2-closeout docs/team-handoff feat/team-mode rollback/03-pre-phase3  
  ⎿  /usr/bin/bash: line 1: cd: C:workspacesoftware_finsoftware_fin-openspe
     c: No such file or directory
     error: src refspec feat/team-mode does not match any
     … +2 lines (ctrl+o to expand)

● 那行指令是用 bash 執行的：反斜線被吃掉，所以 cd 失敗，結果是在 SpecKit
  目錄裡推送。SpecKit 沒有 feat/team-mode 這支，git 才報錯，但同一行的其他三個
  ref 可能已經推上去了。我先查一下遠端現況。

  Ran 1 shell command (ctrl+o to expand)

● 兩個遠端都沒有新的 ref，所以這次沒有推上任何東西，不需要清理。

  ! 指令是用 bash 執行的，請改用正斜線和 git -C。一次貼一行：

  ! git -C /c/workspace/software_fin/software_fin-openspec push -u origin 
  docs/phase2-closeout docs/team-handoff feat/team-mode rollback/03-pre-phase3
  ! git -C /c/workspace/software_fin/software_fin-speckit push -u origin 
  docs/phase2-closeout docs/team-handoff 009-team-mode rollback/03-pre-phase3

  兩行都推完後告訴我，我就開六個疊層 PR，並把兩組的 PR 互相連結。

✻ Baked for 14s · done Saturday 7:27 PM

!  git -C /c/workspace/software_fin/software_fin-openspec push -u origin        
  docs/phase2-closeout docs/team-handoff feat/team-mode rollback/03-pre-phase3  
  ⎿  To https://github.com/yue083139/software_fin-openspec.git
      * [new branch]      docs/phase2-closeout -> docs/phase2-closeout
      * [new branch]      docs/team-handoff -> docs/team-handoff
     … +6 lines (ctrl+o to expand)

● OpenSpec 推好了，三支分支和回復標籤都到了遠端。請再貼 SpecKit 那一行：

  ! git -C /c/workspace/software_fin/software_fin-speckit push -u origin 
  docs/phase2-closeout docs/team-handoff 009-team-mode rollback/03-pre-phase3

  推完我就把兩邊的六個 PR 一起開，好讓兩組的 PR 互相連結。

✻ Cooked for 5s · done Saturday 7:27 PM

!  git -C /c/workspace/software_fin/software_fin-speckit push -u origin         
  docs/phase2-closeout docs/team-handoff 009-team-mode rollback/03-pre-phase3   
  ⎿  To https://github.com/yue083139/software_fin-speckit.git
      * [new branch]      docs/phase2-closeout -> docs/phase2-closeout
      * [new branch]      docs/team-handoff -> docs/team-handoff
     … +6 lines (ctrl+o to expand)

● Both pushed. Opening the six stacked PRs.

  Created PR #13 (ctrl+o to expand)

● Now cross-linking each pair (replacing the "見下方連結" placeholder with the
  sibling PR URL).

  Edited PR #13 (ctrl+o to expand)

● PRs are open and cross-linked. Checking CI on the stacks.

  Ran 1 shell command (ctrl+o to expand)

● CI is running (one already passed). Waiting for the rest in the background.

  Ran 1 shell command (ctrl+o to expand)

● 六個 PR 都開好了，兩組對應的 PR 也互相連結了。SpecKit #11 的 CI
  已經過了，另外五個還在跑，結果出來我會回報。

  1/3 第二期收尾
  OpenSpec: #12 (https://github.com/yue083139/software_fin-openspec/pull/12)
  SpecKit: #11 (https://github.com/yue083139/software_fin-speckit/pull/11)
  合併目標: dev
  ────────────────────────────────────────
  2/3 組員交接（產品 TRD、人工驗證手冊）
  OpenSpec: #13 (https://github.com/yue083139/software_fin-openspec/pull/13)
  SpecKit: #12 (https://github.com/yue083139/software_fin-speckit/pull/12)
  合併目標: 1/3 的分支
  ────────────────────────────────────────
  3/3 組隊模式
  OpenSpec: #14 (https://github.com/yue083139/software_fin-openspec/pull/14)
  SpecKit: #13 (https://github.com/yue083139/software_fin-speckit/pull/13)
  合併目標: 2/3 的分支

  還要你處理的：
  1. 契約的四處語意補充還沒批准，這會擋住 3/3 的合入。內容寫在 #14 和 #13
     的「待負責人批准」那一段。批准後我會把它記進 parity 和評審紀錄。
  2. 合併：你說「合」我才合，照之前的做法從 1/3
     開始。前兩張（1/3、2/3）只改文件，現在就可以合；3/3 要等你批准上面那四處。
  3. 人工驗證：交給組員照 docs/manual-verification.md 的五個場次跑。3/3 的 PR
     描述也明寫了人工驗證還沒做。
  4. 匯出今天的對話紀錄：用 /export，匯出後我先掃過個資和金鑰，再放進
     docs/ai-logs/。

✻ Churned for 1m 15s · done Saturday 7:29 PM
● Background command "Wait for CI on remaining PRs" completed (exit code 0)

  Read 1 file (ctrl+o to expand)

● 六個 PR 的 CI（gate-pr）都通過了。

  1/3 第二期收尾和 2/3 組員交接只改文件，評審和門禁都過了，現在就能合。3/3
  組隊模式的評審和 CI 也都過了，但要等你批准契約的四處語意補充才能合入。人工驗證
  交給組員做，不擋合併。

  你可以這樣回我：
  - 只說「合」：我照先例從 1/3 開始，每合一個之前先把基底改成 dev。合到 2/3
    為止，3/3 先不動。
  - 說「批，合」：連 3/3 一起合，並把你的批准記進 parity 和評審紀錄。

✻ Worked for 6s · done Saturday 7:29 PM

❯ 批，合                                                                        

● 你批准了，我先在兩個組隊 PR 上留言記下這次批准，再照順序合併。

  Edited PR #13 (ctrl+o to expand)

● Six PRs merged into dev. Verifying both dev branches contain everything and
  the code matches across repos.

  Ran 1 shell command (ctrl+o to expand)

● Write(~\.claude\projects\C--workspace\memory\software-fin-todo.md)
  ⎿  Added 9 lines, removed 9 lines
       5    type: project
       6  ---
       7  
       8 -Updated 2026-11-14 (end of session). On 2026-11-14 the owner sa
         -id: delete the phase-2 branches, approve the five pending point
         -s, do phase 3, collect all manual verification into one card fo
         -r teammates, archive everything else, and write a product TRD f
         -or newcomers. All of that is done locally.                     
       8 +Updated 2026-11-14. On 2026-11-14 the owner approved the 4 team
         +-mode contract semantic additions (their words: 「批，合」; the
         + approval is recorded as a PR comment on openspec #14 and speck
         +it #13). The same day these were merged to dev in order: opensp
         +ec #12–#14 (dev fd78846) and speckit #11–#13 (dev 9dc25b4). ser
         +ver, web and contracts are identical in both repos.            
       9  
      10 -Local stacked branches, all committed and gates green, waiting 
         -for the owner to push with `!` (agents cannot push):           
      11 -- OpenSpec: docs/phase2-closeout → docs/team-handoff → feat/tea
         -m-mode, plus tag rollback/03-pre-phase3                        
      12 -- SpecKit: docs/phase2-closeout → docs/team-handoff → 009-team-
         -mode, plus the same tag                                        
      13 -- PR bodies are drafted in the session scratchpad (prs/closeout
         -.md, handoff.md, team.md). After the push: open 3 stacked PRs p
         -er repo, link the two repos' PRs to each other, and merge only 
         -when the owner says "合" (retarget each PR to dev first; do not
         - delete branches until the whole stack is merged).             
      14 -                                                               
      10  Still open:
      16 -1. The owner must approve the 4 contract semantic additions for
         - team-mode (design D7 / research R7). This blocks merging.     
      17 -2. Manual verification P-05: teammates run docs/manual-verifica
         -tion.md scenes A–E and fill in the results table.              
      18 -3. /export the 2026-11-14 session into docs/ai-logs (scan it fo
         -r secrets first).                                              
      11 +1. Delete the 6 merged branches (docs/phase2-closeout, docs/tea
         +m-handoff, feat/team-mode / 009-team-mode in each repo). Ask th
         +e owner first.                                                 
      12 +2. Phase-3 close-out PR, done by me:                           
      13 +   - change 「待負責人批准」 to approved in design D7, research
         + R7, both verification.md files, the review record and parity §
         +5                                                              
      14 +   - set parity §4 team-mode to 已合入 and product-trd to 已合 
         +入                                                             
      15 +   - `openspec archive team-mode`                              
      16 +   - add the merges to ops-log                                 
      17 +   - after the owner runs /export, scan the 2026-11-14 session 
         +log for secrets and put it in docs/ai-logs                     
      18 +3. Manual verification P-05: teammates run docs/manual-verifica
         +tion.md scenes A–E.                                            
      19  4. Optional card: show question text in timed mode.
      20  
      21  Deadline 2026-11-30. Related: [[software-fin-project]]
  ⎿  Loaded 11 skills from software_fin-speckit\.claude\skills
  ⎿  Loaded 7 skills from software_fin-openspec\.claude\skills
  ⎿  18 skills available

● 兩組各三個 PR 都合進 dev 了：OpenSpec #12、#13、#14（dev 現在在
  fd78846），SpecKit #11、#12、#13（dev 現在在
  9dc25b4）。照先例，每合一個之前先把它的基底改成 dev，用一般合併。

  - 批准：契約四處語意補充的批准，已經留言記在 OpenSpec #14 和 SpecKit #13。
  - 核對：合入後兩組 dev 上的 server/、web/src、contracts/
    逐字相同；六支分支的內容也都已經在 dev 裡。
  - 還沒更新的文件：文件裡仍寫著「待負責人批准」，parity
    上組隊卡的狀態也還是「已實作（待合入）」。這兩處會在下一個收尾 PR 改掉。

  還沒做的：
  1. 刪分支：兩組各 3 支已合併的分支（本地＋遠端）。整串都合完了，照先例可以刪，
     你說「刪」我就刪。
  2. 第三期收尾 PR（我來做）：
     - 把「待負責人批准」改成「已批准」，parity 改成「已合入」。
     - 用 openspec archive 歸檔組隊這個 change。
     - 在 ops-log 記下這次合併。
  3. 對話紀錄：你先跑 /export 匯出今天的對話，我掃過個資和金鑰後，跟收尾 PR
     一起提交。
  4. 人工驗證：請組員照 docs/manual-verification.md 的 A 到 E 五個場次執行。

  待辦清單已經更新到記憶裡。

✻ Cooked for 1m 16s · done Saturday 7:33 PM

※ recap: 我們在收尾 software_fin 第二期、做完第三期組隊模式，兩組六個 PR 已全部合進 dev。下一步請你決定要不要刪掉已合併的六支分支，再用 /export 匯出今天的對話給我放進收尾 PR。 (disable recaps in /config)
  ⎿  Read 
     ..\..\Users\user\.claude\projects\C--workspace\memory\software-fin-todo.md 
     (22 lines)
  ⎿  Read software_fin-speckit\specs\009-team-mode\verification.md (53 lines)
  ⎿  Read software_fin-openspec\web\src\pages\Home.tsx (84 lines)
  ⎿  Read software_fin-openspec\web\src\pages\AnswerForm.tsx (126 lines)
  ⎿  Read software_fin-openspec\openspec\changes\team-mode\verification.md (66 
     lines)

● Compacted while idle, before the prompt cache expired · turn off with 
  "idleCompaction": false in settings.json

❯ 刪  收尾                                                                      

  Ran 1 shell command (ctrl+o to expand)

● Precedent: gh api DELETE. Proceed.

  Ran 2 shell commands (ctrl+o to expand)

● Now the close-out. Find all "待負責人批准" and status strings.

  Ran 2 shell commands (ctrl+o to expand)

● Bash(cd /c/workspace/software_fin/software_fin-openspec; openspec archive
      team-mode --yes 2>&1 | tail -15; ls openspec/changes
      openspec/changes/archive; ls openspec/…)
  ⎿  Proposal warnings in proposal.md (non-blocking):
       ⚠ Change must have a Why section. Missing required sections. Expecte
     d headers: "## Why" and "## What Changes". Ensure deltas are documente
     … +43 lines (ctrl+o to expand)
  ⎿  Created software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\.openspec.yaml (+2 -0)
      1 +schema: spec-driven                                             
      2 +created: 2026-11-14                                             
  ⎿  Created software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\design.md (+77 -0)
       1 +# team-mode — design（v1.1）                                   
       2 +                                                               
       3 +知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，
         +2026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論
         +時間」，隊員分數平均；Quizlet Live 隨機分隊，每位隊員只看到部分
         +選項。本卡依 TRD §6 裁定只取「一隊多人、一人代表作答」，不採分 
         +數平均與討論時間。                                             
       4 +                                                               
       5 +倉外行為探針：無。本卡的決策只依賴本倉既有的鎖、序號與依身分裁 
         +切的 view（`server/quiz_server/activity.py`、`views.py`），不依
         +賴第三方函式庫的新行為、外部服務或瀏覽器新行為；前端草稿的防抖 
         +用 `setTimeout`，不影響伺服器端判據。草稿更新會讓每條連線重算一
         +次 view，與既有「任何狀態改變都重算」相同，量級為（組數 × 6 台 
         +＋老師）≤ 73 條連線、每台每 400 毫秒至多一次，本機模擬不另跑效 
         +能探針（屬取捨）。                                             
       6 +                                                               
       7 +**v1.1（提案輪評審）**：紅隊——釋放後下一台不需邀請碼即可搶佔（ 
         +改為釋放即換新碼、只顯示在老師畫面，之後連第一台也要帶碼）；全 
         +形輸入使 `compare_digest` 拋例外（改 NFKC 正規化後以位元組比對 
         +）。架構——邀請碼常駐學生畫面且搶答中可加入（改為學生只在準備階 
         +段看得到、開始搶答即換新碼）；契約身分表、join、release 屬語意 
         +補充而非純新增（D7 逐條列出、呈負責人批准）；台數算憑證數、關分
         +頁不釋放名額（列為取捨）。                                     
       8 +                                                               
       9 +## 決策                                                        
      10 +                                                               
      11 +### D1 組隊是活動設定，不是模式                                
      12 +                                                               
      13 +`Activity.team_play: bool = False`。`set_team_play(enabled)`： 
         +鎖內、`preparing`（其他階段 409）；值改變時撤銷**所有**組別憑證
         +、邀請碼與草稿（`_revoke_all`），`_bump()`；值不變時什麼都不做 
         +。`reset` 保留；`configure_teams` 也走 `_revoke_all`（撤銷憑證 
         +、清邀請碼與草稿）。                                           
      14 +                                                               
      15 +- 證偽欄｜屬取捨，理由：代表作答不改 TRD T-01 的四個面向（誰能 
         +作答、何時鎖題、如何計分、何時揭曉），做成模式就無法與時間計分 
         +等模式並用。可證偽部分：`test_team_mode.py::test_team_play_does
         +_not_change_scoring`（三種模式各跑同樣的送出，組隊開／關的順位 
         +、判定與分數相同；時間計分的分數取決於真實時鐘，只比順位與判定 
         +）、`test_toggle_only_when_preparing`、`test_toggle_revokes_onl
         +y_on_change`、`test_configure_teams_clears_codes`；第一、二期全
         +部測試在預設 `team_play=False` 下照舊綠。                      
      16 +                                                               
      17 +### D2 憑證與邀請碼                                            
      18 +                                                               
      19 +- `_tokens: dict[str, str]`（憑證 → 組別）多對一；`_codes: dict
         +[str, str]`（組別 → 邀請碼）。邀請碼 6 碼，字母表 `ABCDEFGHJKLM
         +NPQRSTUVWXYZ23456789`（32 字，`secrets.choice`；約 10⁹ 種，本機
         +模擬不設嘗試次數限制，屬取捨）。                               
      20 +- `join(team, code)`，全部在鎖內，讓出點夾在檢查與寫入之間：   
      21 +  1. 組隊關閉：同第一期，該組已有憑證 ⇒ `TeamTakenError` 409「 
         +此組已有裝置加入，請老師釋放後再加入」。                       
      22 +  2. 組隊開啟且該組**有邀請碼**（已有裝置，或曾被老師釋放）：輸
         +入經 NFKC 正規化（全形轉半形）、去空白、轉大寫後**以位元組** `s
         +ecrets.compare_digest` 比對，不符 ⇒ `InviteCodeError` **403**「
         +邀請碼不正確」（非 ASCII 輸入只會比對失敗，不會拋例外）；相符但
         +已有 `MAX_DEVICES = 6` 台 ⇒ 409「此組裝置已滿（最多 6 台）」。 
         +先比對邀請碼再檢查上限：沒有正確邀請碼的人不該知道該組有幾台。 
      23 +  3. 組隊開啟且該組**沒有邀請碼**（從未有人加入）：發憑證並產生
         +邀請碼。                                                       
      24 +- **開始搶答即換新所有邀請碼**（`start`）：準備階段被他組瞄到的
         +碼在搶答中失效；搶答中要加入的組員只能向老師索取（老師 view 永 
         +遠有現行碼）。                                                 
      25 +- `release(team)`：撤銷該組全部憑證、清該組草稿；組隊時**換新邀
         +請碼**（只在老師 view）。被踢的冒用者不能搶先以「第一台」重新佔
         +住該組。                                                       
      26 +- 殘餘風險：準備階段已憑碼加入的冒用者，開始搶答換碼後憑證不會 
         +被撤銷，仍留在該組；老師可從台數看出異常並釋放整組。           
      27 +- `devices(team)`＝該組已發出的憑證數。憑證存在分頁的 sessionSt
         +orage，關分頁不會釋放名額；名額不夠時老師只能釋放整組、組員以新
         +碼重新加入（屬取捨：單台釋放需要裝置識別與在線偵測，超出本卡範 
         +圍；6 台高於一般分組人數）。                                   
      28 +                                                               
      29 +- 證偽欄｜可證偽：`test_team_mode.py::test_join_requires_code` 
         +（無碼、錯碼、截短碼 403 且不發憑證；小寫與前後空白可）、`test_
         +fullwidth_code_accepted`、`test_single_device_without_team_play
         +_unchanged`、`test_device_limit`（滿後錯碼仍 403）、`test_concu
         +rrent_join_at_limit`（6 台後並發 5 次恰 0 成功；5 台後恰 1 成功
         +）、`test_concurrent_first_join_one_code`、`test_release_revoke
         +s_all_devices_and_code`（釋放後無碼、舊碼 403，新碼可加入）、`t
         +est_code_rotates_on_start_and_hidden_from_students`。          
      30 +                                                               
      31 +### D3 送出：代表作答                                          
      32 +                                                               
      33 +送出的判定口徑不變：同組任一憑證都反查到同一組別，「本組已送出 
         +這一題」的檢查、序號與時間計分的截止都在同一把鎖內。`submit` 唯
         +一的新增是送出成功後清除該組該題的草稿（D4）。                 
      34 +                                                               
      35 +- 證偽欄｜可證偽：`test_team_mode.py::test_concurrent_submit_sa
         +me_team`（同組 3 台裝置、每題並發 20 次，每次恰 1 筆成功、其餘 
         +`AlreadySubmittedError`、序號無重號）；`test_member_sees_team_s
         +ubmission`（A 裝置送出後 B 裝置收到含該筆的推播；B 再送 409「本
         +組已送出這一題，不可修改」）。                                 
      36 +                                                               
      37 +### D4 組內草稿                                                
      38 +                                                               
      39 +- `POST /api/student/draft`，`X-Team-Token`，本體 `{question, a
         +nswers}`，回 `{question}`（不回顯內容）。`set_draft` 在鎖內依序
         +檢查：組隊（409「只有組隊模式可以共用草稿」）、`answering`（409
         +）、題號（404）、時間計分只收開放中那一題（409「這一題目前沒有 
         +開放作答」）、本組尚未送出該題（409「本組已送出這一題，不可修改
         +」）、`answers` 長度＝子題數且每格 ≤200 字、不含控制字元（422，
         +訊息固定、不回顯）；**空白允許**。檢查與寫入同在一把鎖內，與送 
         +出不會交錯成「送出後又寫入草稿」。                             
      40 +- `Activity.drafts: dict[str, dict[int, tuple[str, ...]]]`，最 
         +後寫入者為準；清除時機：該題送出成功、`_clear_answers`（匯入、 
         +重置）、`release`、`_revoke_all`（切換組隊、改組數）。         
     … 37 more lines (ctrl+o to expand)
  ⎿  Created software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\proposal.md (+48 -0)
       1 +# team-mode — 組隊模式：一組多台裝置、代表作答（v1.1）         
       2 +                                                               
       3 +檔位：**S**（作答隔離：新增送往學生端的組內草稿通道；`contracts
         +/` 增端點與欄位；組別憑證口徑改變）｜主人：@yue083139｜parity：
         +`docs/parity.md` §4 `team-mode`｜需求：X-04（TRD M4、§6 裁定「 
         +代表作答」）｜依賴：`game-mode-framework`                      
       4 +                                                               
       5 +## 首屏決策摘要                                                
       6 +                                                               
       7 +1. **組隊是與模式正交的活動設定，不是第四種模式**：選了 `team_p
         +lay` 開關（任何模式都可開）／代價：TRD §3 把 M4 列在模式表，名 
         +稱上不一致／可被「三種模式 × 組隊開關的計分與第一期全部測試結果
         +不變」證偽；屬取捨，理由：代表作答不改「誰能作答、何時鎖題、如 
         +何計分、何時揭曉」任何一項（TRD T-01 的四個面向），做成模式就得
         +和經典／只計對錯／時間計分各組合一次。                         
       8 +2. **同組第二台起的裝置要輸入該組的邀請碼**：第一台加入時伺服器
         +產生 6 碼邀請碼；學生只在準備階段看得到，開始搶答即換新、釋放某
         +組也換新，搶答中只有老師畫面有現行碼／代價：組員多輸入一次，搶 
         +答中加入要問老師／可被「無碼、錯碼、準備階段的舊碼、釋放前的舊 
         +碼加入 ⇒ 403 且拿不到憑證」的負例證偽。不設邀請碼時，任何人選一
         +個已有人的組別就能讀到該組草稿與送出——第一期「一組一台裝置」擋 
         +掉的冒用，在組隊下會重新打開。                                 
       9 +3. **每組每題仍只能送出一次，組內任一人送出即代表全組**：送出判
         +定與順位完全沿用 `buzz-answering`（同一把鎖、同一個序號）／可被
         +「同組兩台裝置並發送出同一題 N 次，每次恰一筆成功」證偽。      
      10 +4. **組內草稿只在 `answering` 階段送給本組裝置**：最後寫入者為 
         +準，不進結果、不匯出、老師看不到／可被「他組草稿更新時本組連線 
         +不收到任何訊息，且本組 payload 不含他組草稿字串」證偽。        
      11 +5. **切換組隊開關、改組數、釋放某組都撤銷相關憑證**：代價：準備
         +階段切換後所有裝置要重新加入；台數算的是已發出的憑證，關分頁不 
         +釋放名額，只能整組釋放／屬取捨，理由：撤銷是唯一不必處理「多台 
         +變一台時留哪台」的做法；單台釋放需要裝置識別與在線偵測，超出本 
         +卡範圍。                                                       
      12 +                                                               
      13 +**v1.1（提案輪評審）**：釋放後與搶答中的邀請碼口徑收緊（摘要第 
         +2 條）；全形輸入正規化；契約身分表、join、release 四處屬**語意 
         +補充**，見 design D7，**呈負責人批准**。                       
      14 +                                                               
      15 +**矩陣落點**：新增 M-017（組隊加入與邀請碼）、M-018（組內任一人
         +送出即代表全組）、M-019（組內草稿隔離）。                      
      16 +                                                               
      17 +**merge 三問第三問**：需求證實——X-04；負責人 2026-11-12 裁定組 
         +隊＝代表作答，2026-11-14 指示「第三期做」。                    
      18 +                                                               
      19 +## 目標                                                        
      20 +                                                               
      21 +- `Activity.team_play`、`set_team_play()`；憑證表改為「憑證 →  
         +組別」多對一，每組上限 6 台；邀請碼產生、比對、撤銷。          
      22 +- `POST /api/teacher/team-play`、`POST /api/student/draft`；`PO
         +ST /api/student/join` 本體增可選 `code`。                      
      23 +- view：老師 `team_play`、`devices`、`invite_codes`；學生 `team
         +_play`、`invite_code`、`drafts`；公開資訊 `team_play`。        
      24 +- web：老師「組別」區塊的組隊開關、各組台數與邀請碼；首頁邀請碼
         +欄；學生頁邀請碼與組內草稿。                                   
      25 +                                                               
      26 +## 邊界（本卡不做）                                            
      27 +                                                               
      28 +組內分數平均（裁定不採）；組內聊天；指定隊長或限定只有隊長可送 
         +出；學生自行建立組別；Kahoot 式「討論時間」倒數。              
      29 +                                                               
      30 +## 驗收                                                        
      31 +                                                               
      32 +| # | 指令 | 期望輸出 |                                        
      33 +|---|---|---|                                                  
      34 +| 1 | `uv run --project server pytest -q server/tests/test_team
         +_mode.py` | 加入與邀請碼（403、409 已滿、切換撤銷）、並發送出恰
         +一筆成功、草稿限制（409、422）、草稿清除；passed |             
      35 +| 2 | `uv run --project server pytest -q server/tests/test_isol
         +ation.py` | 新增組隊負例：他組草稿與邀請碼不出現在本組 payload 
         +、他組草稿不觸發本組推播；既有負例不變；passed |               
      36 +| 3 | `make test` | 第一、二期全部測試照舊綠（組隊關閉時行為不 
         +變） |                                                         
      37 +| 4 | `npm --prefix web test` | 組隊開關呼叫 API、首頁帶邀請碼 
         +加入、學生頁顯示組內草稿並可套用；passed |                     
      38 +| 5 | 人工驗證 | `docs/manual-verification.md` 場次 E |        
      39 +                                                               
      40 +## 未決呈裁                                                    
     … 8 more lines (ctrl+o to expand)
  ⎿  Created software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\specs\activity-lifecycle\spec.md (+21 -0)
       1 +## MODIFIED Requirements                                       
       2 +                                                               
       3 +### Requirement: 系統必須區分老師與學生兩種身分                
       4 +                                                               
       5 +系統 MUST 提供老師與學生兩種身分進場。老師 MUST 以伺服器啟動時 
         +產生的老師金鑰驗證；學生 MUST 選定一個組別並取得伺服器發出的組 
         +別憑證，之後的連線與操作 MUST 以憑證辨識組別，MUST NOT 採信客戶
         +端自報的組別名稱。組隊關閉時每組 MUST 只有一台裝置；組隊開啟時 
         +同組可有多台裝置，第二台起 MUST 以該組邀請碼加入（team-mode）。
       6 +                                                               
       7 +#### Scenario: 學生選組進場                                    
       8 +- **WHEN** 學生在首頁選擇「第2組」                             
       9 +- **THEN** 學生頁 MUST 顯示所屬組別「第2組」與目前活動階段     
      10 +                                                               
      11 +#### Scenario: 無金鑰不得使用老師功能                          
      12 +- **WHEN** 未帶老師金鑰或帶錯金鑰呼叫任何老師端 API            
      13 +- **THEN** 伺服器 MUST 回 401，且活動狀態 MUST NOT 改變        
      14 +                                                               
      15 +#### Scenario: 同一組只能有一台裝置                            
      16 +- **WHEN** 組隊關閉時第1組已有裝置加入，另一台裝置再選第1組    
      17 +- **THEN** 伺服器 MUST 回 409，直到老師釋放第1組               
      18 +                                                               
      19 +#### Scenario: 沒有憑證只拿到最少資訊                          
      20 +- **WHEN** 學生連線未帶憑證、帶錯憑證或帶已被撤銷的憑證        
      21 +- **THEN** 伺服器 MUST 只回傳階段與「組別無效」標記，MUST NOT  
         +回傳任何組別或老師端資料                                       
  ⎿  Created software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\specs\team-mode\spec.md (+73 -0)
       1 +## ADDED Requirements                                          
       2 +                                                               
       3 +### Requirement: 老師可在準備階段開啟組隊                      
       4 +                                                               
       5 +老師 MUST 能在 `preparing` 階段開啟或關閉「組隊（一組多台裝置）
         +」；其他階段 MUST 回 409。開關的值改變時，伺服器 MUST 撤銷所有 
         +組別憑證與邀請碼。重置活動 MUST 保留開關。組隊 MUST NOT 改變任 
         +何模式的作答規則、計分與揭曉時機。                             
       6 +                                                               
       7 +#### Scenario: 開啟組隊                                        
       8 +- **WHEN** 老師在準備階段開啟組隊                              
       9 +- **THEN** 老師畫面與公開資訊的 `team_play` MUST 為 true，所有 
         +已加入的裝置 MUST 失效                                         
      10 +                                                               
      11 +#### Scenario: 搶答中不可切換                                  
      12 +- **WHEN** 老師在 `answering` 階段要求切換組隊                 
      13 +- **THEN** 伺服器 MUST 回 409，開關與憑證 MUST 不變            
      14 +                                                               
      15 +#### Scenario: 組隊不改計分                                    
      16 +- **WHEN** 同一組送出紀錄分別在組隊開與關下計分                
      17 +- **THEN** 每題得主、順位與各組分數 MUST 相同                  
      18 +                                                               
      19 +### Requirement: 組隊時同組第二台起須輸入邀請碼                
      20 +                                                               
      21 +組隊時，某組第一台裝置加入 MUST 取得組別憑證並使伺服器產生該組 
         +6 碼邀請碼；該組有邀請碼之後，加入的裝置 MUST 提供相符的邀請碼 
         +（不分大小寫與全半形、忽略空白），否則 MUST 回 403 且 MUST NOT 
         +發出憑證。每組最多 6 台；已滿 MUST 回 409，且 MUST 先比對邀請碼
         +再檢查上限。學生畫面 MUST 只在 `preparing` 階段含本組邀請碼；老
         +師畫面 MUST 一直含各組現行邀請碼。開始搶答時 MUST 換新所有邀請 
         +碼。老師釋放某組 MUST 撤銷該組全部裝置的憑證並換新邀請碼（新碼 
         +只在老師畫面）。                                               
      22 +                                                               
      23 +#### Scenario: 沒有邀請碼不能加入已有組員的組別                
      24 +- **WHEN** 組隊時第1組已有一台裝置，另一台裝置選第1組但未帶或帶
         +錯邀請碼                                                       
      25 +- **THEN** 伺服器 MUST 回 403「邀請碼不正確」，第1組的裝置數 MU
         +ST 不變                                                        
      26 +                                                               
      27 +#### Scenario: 帶正確邀請碼加入                                
      28 +- **WHEN** 另一台裝置帶第1組的邀請碼選第1組                    
      29 +- **THEN** 該裝置 MUST 取得第1組的憑證，老師畫面第1組 MUST 顯示
         + 2 台                                                          
      30 +                                                               
      31 +#### Scenario: 裝置已滿                                        
      32 +- **WHEN** 第1組已有 6 台裝置，第 7 台帶正確邀請碼加入         
      33 +- **THEN** 伺服器 MUST 回 409，且並發加入時 MUST 不超過 6 台   
      34 +                                                               
      35 +#### Scenario: 釋放整組                                        
      36 +- **WHEN** 老師釋放第1組                                       
      37 +- **THEN** 第1組所有裝置的憑證 MUST 失效；之後不帶碼或帶舊邀請 
         +碼加入第1組 MUST 回 403，帶老師畫面上的新邀請碼 MUST 可加入    
      38 +                                                               
      39 +#### Scenario: 開始搶答換新邀請碼                              
      40 +- **WHEN** 老師開始搶答                                        
     … 33 more lines (ctrl+o to expand)
  ⎿  … 11 more files changed

  Made 1 scratchpad edit +76, ran 1 shell command (ctrl+o to expand)

● Bash(python "C:/Users/user/AppData/Local/Temp/claude/c0ee99454f32d4b9/98614fbc
      -ec22-47f6-9745-70be090678d7/scratchpad/closeout3.py" && cd
      /c/workspace/software_fin/s…)
  ⎿  ok C:\workspace\software_fin\software_fin-openspec\openspec\specs\team
     -mode\spec.md
     ok C:\workspace\software_fin\software_fin-openspec\openspec\changes\ar
     … +22 lines (ctrl+o to expand)
  ⎿  Updated software_fin-openspec\docs\ops-log.md (+2 -0)
      14  | 2026-11-12 | dev | 依負責人「合」依序合併第二期疊層 PR #9–#11
          （每合一個前先把基底改為 dev，一般合併，整串合完前不刪分支）；d
          ev 到 070ac4a | dev 含第二期三卡 | 以 `rollback/02-pre-phase2` 
          開回復分支經 PR 還原 |
      15  | 2026-11-14 | 已合併的遠端功能分支 | 依負責人「刪」以 `gh api 
          -X DELETE …/git/refs/heads/<分支>` 刪除第二期三支遠端分支（feat
          /game-mode-framework、feat/question-settings、feat/mode-timed-s
          coring；刪前以 `git rev-list --count origin/dev..<分支>` 確認皆
          為 0），並刪除對應本機分支 | GitHub 分支清單只剩 main、dev | 以
          已合併 PR 頁面的 Restore branch 還原 |
      16  | 2026-11-14 | 本機 | 第二期收尾、組員交接文件、第三期 `team-mo
          de` 完成：疊層分支 docs/phase2-closeout → docs/team-handoff → f
          eat/team-mode；本機打標籤 `rollback/03-pre-phase3`（指向第三期
          前的 dev 070ac4a），待負責人以 `!` 推送分支與標籤 | 僅本機 | 刪
          除本機分支與標籤 |
      17 +| 2026-11-14 | dev | 依負責人「批，合」先在最上層 PR 留言記下契
         +約語意補充的批准，再依序把疊層 PR 基底改為 `dev` 後以一般合併合
         +入：#12 → #13 → #14（`dev` → fd78846） | dev 含第二期收尾、交接
         +文件、第三期組隊 | 以 `rollback/03-pre-phase3` 開回復分支經 PR 
         +還原 |                                                         
      18 +| 2026-11-14 | 已合併的遠端功能分支 | 依負責人「刪」以 `gh api 
         +-X DELETE …/git/refs/heads/<分支>` 刪除三支遠端分支（docs/phase
         +2-closeout、docs/team-handoff、feat/team-mode；刪前以 `git rev-
         +list --count origin/dev..<分支>` 確認皆為 0），並刪除對應本機分
         +支 | GitHub 分支清單只剩 main、dev | 以已合併 PR 頁面的 Restore
         + branch 還原 |                                                 
  ⎿  Updated software_fin-openspec\docs\parity.md (+3 -2)
      47  | `question-settings` | X-04 | 準備階段老師可把任一題設為**雙倍
          分數**（倍率 1 或 2），任何模式下該題得分 ×2；重新匯入即清除、
          重置活動保留；學生看得到哪些題是雙倍；分數欄名在全部倍率為 1 的
          經典搶答顯示「得題數」，其餘顯示「得分」（TRD T-05 倍率） | 已
          合入 | 已合入 |
      48  | `mode-buzz-fallback` | X-03、X-04 | 搶答＋錯誤遞補：最先送出
          者判錯則依順位遞補（TRD M1） | 未開 | 未開 |
      49  | `mode-timed-scoring` | X-04 | **時間計分**模式：老師逐題開放
          ，每題時限 5–120 秒（預設 20，準備階段設定），到時伺服器關閉該
          題、老師也可提早結束；只收開放中那一題；老師判定該題後揭曉；正
          確得 `floor(1000 × (1 − t ÷ T ÷ 2) + 0.5) × 倍率`（以整數運算 `
          (2001 × T − 作答毫秒) // (2 × T)` 實作，避免浮點誤差）（t ≤ 0.5
           秒得滿分，t 為伺服器量得的作答秒數）；揭曉後學生看到本組該題對
          錯與得分、本組累積分數，以及全部組別的累積**名次**（不含他組分
          數，以免反推作答秒數）；他組答案、分數仍只在活動結束後才看得到
          （TRD M2、T-04、T-05 時限） | 已合入 | 已合入 |
      50 -| `team-mode` | X-04 | **組隊**（活動設定，可與任一模式搭配，只
         -在準備階段切換）：一組最多 6 台裝置，同組有邀請碼後加入須帶碼（
         -6 碼，不分大小寫與全半形；學生只在準備階段看得到本組碼，開始搶 
         -答與老師釋放某組時換新，搶答中向老師索取）；組內任一人送出即代 
         -表全組，每組每題仍只送出一次；搶答中組員看得到本組草稿（不計分 
         -、不匯出，老師與他組看不到）；切換組隊、改組數、釋放某組都撤銷 
         -相關裝置（TRD M4，§6 裁定）；第三期 | 已實作（待合入） | 已實作
         -（待合入） |                                                   
      50 +| `team-mode` | X-04 | **組隊**（活動設定，可與任一模式搭配，只
         +在準備階段切換）：一組最多 6 台裝置，同組有邀請碼後加入須帶碼（
         +6 碼，不分大小寫與全半形；學生只在準備階段看得到本組碼，開始搶 
         +答與老師釋放某組時換新，搶答中向老師索取）；組內任一人送出即代 
         +表全組，每組每題仍只送出一次；搶答中組員看得到本組草稿（不計分 
         +、不匯出，老師與他組看不到）；切換組隊、改組數、釋放某組都撤銷 
         +相關裝置（TRD M4，§6 裁定）；第三期 | 已合入 | 已合入 |        
      51  
      52  狀態值：未開／提案中／實作中／已實作（待合入）／已合入。
      53  
     ...
      67  | 2026-11-12 | 第二期三卡 | 兩組皆合入 `dev`（OpenSpec #9–#11；
          SpecKit #8–#10），`dev` 上 server、web 逐字相同；人工驗證待補驗
           | 兩組 | 已確認 |
      68  | 2026-11-14 | 第二期三卡 | 負責人批准契約語意補充三處（經典得
          主得 1×倍率分、`team_scores` 欄名看 `score_label`；設定 API 兩
          欄位可選；時間計分在 `answering` 內判定），並確認兩處落實方式（
          學生端排行榜只公開名次；時間計分活動前不先發學習單） | 兩組（負
          責人裁定） | 已確認 |
      69  | 2026-11-14 | `team-mode` | 負責人指示第三期做組隊；開卡 v1.0
          ：組隊做成與模式正交的活動設定（非第四種模式），同組第二台起憑
          邀請碼加入，組內草稿只給本組 | 兩組（負責人指示） | 同一會話兩
          組同批起稿 |
      70 -| 2026-11-14 | `team-mode` | 提案輪評審（v1.1）：邀請碼只在準備
         -階段給學生、開始搶答與釋放即換新碼；全形輸入正規化；契約四處語 
         -意補充（身分表、join、release、改組數）呈負責人批准；兩組實作完
         -成、程式碼一致 | 兩組 | 同一會話兩組同批修訂；語意補充待負責人 
         -批准 |                                                         
      70 +| 2026-11-14 | `team-mode` | 提案輪評審（v1.1）：邀請碼只在準備
         +階段給學生、開始搶答與釋放即換新碼；全形輸入正規化；契約四處語 
         +意補充（身分表、join、release、改組數）呈負責人批准；兩組實作完
         +成、程式碼一致 | 兩組 | 同一會話兩組同批修訂 |                 
      71 +| 2026-11-14 | `team-mode` | 負責人批准契約四處語意補充（「批，
         +合」，記於 OpenSpec #14、SpecKit #13 留言）；兩組皆合入 `dev`（
         +OpenSpec #12–#14；SpecKit #11–#13），`dev` 上 server、web/src、
         +contracts 逐字相同；人工驗證交組員（`docs/manual-verification.m
         +d` 場次 E） | 兩組（負責人裁定） | 已確認 |                    
  ⎿  Updated software_fin-openspec\docs\product-trd.md (+1 -1)
      46  | 只計對錯模式 | 不比速度、比正確；結束後老師判定，參考答案欄可
          預填建議並「採用全部建議」 | X-04 | 已合入 |
      47  | 雙倍分數題 | 任何模式下把指定題目設為 ×2 分，學生看得到標記 |
           X-04 | 已合入 |
      48  | 時間計分模式（Kahoot 式） | 老師逐題開放、每題 5–120 秒時限由
          伺服器計時；答越快分越高（最高 1000 分 × 倍率）；每題揭曉後公開
          各組**名次** | X-04 | 已合入 |
      49 -| 組隊 | 活動設定，可與任一模式搭配：一組最多 6 台裝置、憑邀請 
         -碼加入，組內任一人送出即代表全組，搶答中組員看得到本組草稿（老 
         -師與他組看不到） | X-04 | 第三期（待合入） |                   
      49 +| 組隊 | 活動設定，可與任一模式搭配：一組最多 6 台裝置、憑邀請 
         +碼加入，組內任一人送出即代表全組，搶答中組員看得到本組草稿（老 
         +師與他組看不到） | X-04 | 第三期（已合入） |                   
      50  | CSV 匯出、公平順位、錯誤遞補 | 見 `docs/parity.md` §4 | X-02
          、X-03 | 未開 |
      51  
      52  ## 5. 專案特色（和一般搶答系統不一樣的地方）
  ⎿  Updated
     software_fin-openspec\docs\reviews\2026-11-14-team-mode-review.md (+2 
     -0)
      27  
      28  1. `contracts/api.md` 四處語意補充（身分表一組多台；join 帶 `co
          de`、403、組隊時 409 指已滿；release 換新碼；改組數清碼與草稿）
          ——我傾向批准：組隊關閉時與第一期完全相同。
      29  2. 人工驗證（P-05）：`docs/manual-verification.md` 場次 E，交組
          員執行。
      30 +                                                               
      31 +**負責人裁定（2026-11-14）**：第 1 項批准（「批，合」，記於 Ope
         +nSpec #14、SpecKit #13 留言）；第 2 項照辦。                   
  ⎿  Updated software_fin-openspec\openspec\changes\archive\2026-11-14-team
     -mode\design.md (+1 -1)
      65  
      66  **新增**：`POST /api/teacher/team-play`（`{enabled}` ⇒ `{team_p
          lay}`；401／409 非 preparing／422）、`POST /api/student/draft`
          （D4）；`/api/public/info` 增 `team_play`；老師 view 增 `team_p
          lay`、`devices`、`invite_codes`；學生 view 增 `team_play`、`inv
          ite_code`、`drafts`。
      67  
      68 -**語意補充（v1.1，呈負責人批准）**——`contracts/api.md` 以下既有
         -字句在組隊時語意改變（組隊關閉時與第一期相同）：               
      68 +**語意補充（v1.1，負責人 2026-11-14 批准）**——`contracts/api.md
         +` 以下既有字句在組隊時語意改變（組隊關閉時與第一期相同）：     
      69  
      70  1. 身分表「組別憑證（一組一台裝置）」⇒ 補「組隊時一組最多 6 台
          ，第二台起憑邀請碼加入」。
      71  2. `POST /api/student/join` 本體 `{team}` ⇒ `{team, code?}`；錯
          誤增 403「邀請碼不正確」；409 在組隊時改指「此組裝置已滿」。
  ⎿  … 3 more files changed

● 正在跑兩組的門禁（收尾的文件修改都已經改好）。

  Searched for 1 pattern, ran 4 shell commands (ctrl+o to expand)

● Skill(software_fin-openspec:review-dispatch)  ⎿  Successfully loaded skill

● 兩組的收尾提交都已完成，門禁全綠。接下來派一輪對抗評審只看這次的差異（依 C
  級規定）。

● Agent(C-tier red review of closeout diff)
  ⎿  Backgrounded agent (↓ to manage · ctrl+o to expand)

● Write(~\.claude\projects\C--workspace\memory\software-fin-todo.md)
  ⎿  Added 5 lines, removed 8 lines
       5    type: project
       6  ---
       7  
       8 -Updated 2026-11-14. On 2026-11-14 the owner approved the 4 team
         --mode contract semantic additions (their words: 「批，合」; the
         - approval is recorded as a PR comment on openspec #14 and speck
         -it #13). The same day these were merged to dev in order: opensp
         -ec #12–#14 (dev fd78846) and speckit #11–#13 (dev 9dc25b4). ser
         -ver, web and contracts are identical in both repos.            
       8 +Updated 2026-11-14. Phase 3 (team-mode) was merged to dev on 20
         +26-11-14 (openspec #12–#14 → fd78846; speckit #11–#13 → dev 9dc
         +25b4). The same day, all 6 merged branches were deleted, local 
         +and remote, via gh api DELETE, which follows precedent.        
       9  
      10 +Phase-3 close-out branch `docs/phase3-closeout` is committed lo
         +cally: openspec 3288200, speckit cce86bf. It records the approv
         +al wording, sets parity and product-trd to 已合入, runs `opensp
         +ec archive team-mode`, and adds the ops-log rows. A C-tier red 
         +review ran on it. Next: the owner pushes it with `!`, then I op
         +en the PRs.                                                    
      11 +                                                               
      12  Still open:
      11 -1. Delete the 6 merged branches (docs/phase2-closeout, docs/tea
         -m-handoff, feat/team-mode / 009-team-mode in each repo). Ask th
         -e owner first.                                                 
      12 -2. Phase-3 close-out PR, done by me:                           
      13 -   - change 「待負責人批准」 to approved in design D7, research
         - R7, both verification.md files, the review record and parity §
         -5                                                              
      14 -   - set parity §4 team-mode to 已合入 and product-trd to 已合 
         -入                                                             
      15 -   - `openspec archive team-mode`                              
      16 -   - add the merges to ops-log                                 
      17 -   - after the owner runs /export, scan the 2026-11-14 session 
         -log for secrets and put it in docs/ai-logs                     
      13 +1. Close-out PR (above): push, open the PR, merge.             
      14 +2. After the owner runs /export, scan the 2026-11-14 session lo
         +g for secrets and put it in docs/ai-logs. This could go in its 
         +own small PR.                                                  
      15  3. Manual verification P-05: teammates run docs/manual-verifica
          tion.md scenes A–E.
      16  4. Optional card: show question text in timed mode.
      17  

● 評審還在跑，結果出來我再接著處理。

✻ Brewed for 3m 38s · done Saturday 8:56 PM

› Message from general-purpose
  一句話結論：我沒找到會阻斷或重要的問題。四條斷言都用 git 和 PR
  紀錄核過，全部成立。另有 1 個次要的措辭漂移，建議列入 followup。

  發現 1｜次要（followup，不阻塞）
    哪兒：SpecKit `specs/009-team-mode/research.md:5`、OpenSpec
  `openspec/changes/archive/2026-11-14-team-mode/design.md:7`
    什麼錯：這兩處的 v1.1 摘要句仍寫「呈負責人批准」。同一卡的 R7 標題和 D7
  已經改成「負責人 2026-11-14 批准」，兩處說法不一致。
    會怎樣：組員只讀摘要句，會以為契約補充還沒批准。產品行為不受影響。
    怎麼修：句尾補「（已於 2026-11-14
  批准）」，或者在「有意不改」登記為歷史敘述。
    證據：在兩 repo 跑 `git grep -n "呈負責人批准" -- ':/'
  ':!docs/ai-logs'`，除上面兩處外還命中 parity.md:70 和
  review.md:16。後兩處屬歷史列，可以不改。同樣範圍
  grep「待負責人批准」零命中，A-1 成立。

  斷言核對：
  - A-1：PR 留言時間比合併早。OpenSpec #14 留言 11:32:43Z，#12 合併
  11:32:48Z；SpecKit #13 留言 11:32:44Z，#11 合併
  11:33:06Z。留言原文含「批，合」，四處補充逐條列出。
  - A-2：`git log --merges dev` 確認 OpenSpec #12→#13→#14 合成 fd78846，SpecKit
  #11→#12→#13 合成 9dc25b4。三個 PR 的 base 都是 dev。`make gate-parity` 輸出「0
  處不一致」。
  - A-3：archive 內的 delta 和主規格的身分需求逐字相同，diff
  只差到下一節的範圍邊界。team-mode 有 4 條 Requirement，Purpose 已補。`openspec
  validate --all` 輸出「9 passed, 0 failed」。
  - A-4：兩 repo 用 `gh api …/branches` 查都只剩 dev、main，`git branch -a`
  本機只剩 main、dev、docs/phase3-closeout。ops-log 列和 #12–#14、#11–#13
  的合併順序一致。刪前 ahead=0
  無法事後重驗，但三支分支都已經合併，這個說法和事實不衝突。另外三個目錄
  `server`、`web/src`、`contracts` 兩 repo 間只差快取檔，parity
  列寫的「逐字相同」成立。

  外包檢查：A-4 的「刪前 rev-list 皆
  0」只能看操作當下的輸出，事後無法重驗，屬於無法證偽的自述。A-1
  的「零命中」只擋「待…」字樣，沒擋「呈…」字樣，所以發現 1 漏網。

  我查閱的檔案：`git show 3288200`、`git show cce86bf` 的全部 diff；`gh pr view`
  OpenSpec #12/#13/#14、SpecKit #11/#12/#13；`gh api
  branches`；`openspec/specs/activity-lifecycle/spec.md`；archive 內的 delta
  specs；finder-tail-red.md。
  CLEARED

  Ran 1 shell command (ctrl+o to expand)

● Agent "C-tier red review of closeout diff" finished · 51s

● 兩組 6 支已合併的分支都刪了，本地和遠端一起刪。兩組的收尾 PR
  也在本機做好、提交了，還沒推送。

  刪分支
  - 刪的是 OpenSpec 的
    docs/phase2-closeout、docs/team-handoff、feat/team-mode，以及 SpecKit
    同名的兩支和 009-team-mode。
  - 刪之前確認過，每支分支都沒有 dev 以外的提交。
  - 現在兩組遠端只剩 main 和 dev。萬一要找回，可以在已合併 PR 的頁面按 Restore
    branch。

  收尾（分支 docs/phase3-closeout）
  - 契約那四處補充，原本寫「待負責人批准」，現在改成「負責人 2026-11-14 批准」。
  - 組隊功能在 parity 和產品 TRD 上的狀態改成「已合入」，parity
    也多記了一列合入紀錄。
  - 在 OpenSpec 組跑了 openspec archive team-mode，組隊這個 change
    歸檔了，它的規格也併入正式規格。
  - ops-log 新增兩列：這次合併，和這次刪分支。
  - 兩組門禁全綠；兩組共用的檔案逐字相同。
  - 依 C 級規定只對這次的差異做了一輪對抗評審，通過，沒有阻斷項也沒有重要項。評
    審指出兩處摘要句還寫著「呈負責人批准」，我已補上「已於 2026-11-14
    批准」，再跑一次門禁也是綠的。

  要你做的
  1. 推送收尾分支，推完我開 PR：
  ! git -C /c/workspace/software_fin/software_fin-openspec push -u origin 
  docs/phase3-closeout
  ! git -C /c/workspace/software_fin/software_fin-speckit push -u origin 
  docs/phase3-closeout
  2. 跑 /export 匯出今天的對話。我掃過個資和金鑰後放進
     docs/ai-logs，可以順便併進這次的收尾 PR。
  3. 請組員照 docs/manual-verification.md 的 A 到 E 場次執行人工驗證。

  待辦清單已更新到記憶裡。

✻ Cogitated for 4m 43s · done Saturday 8:57 PM

※ recap: 我們在收尾第三期組隊功能：合併的分支已刪，兩組的收尾分支已提交、評審通過、門禁全綠。下一步請你用 `!` 推送兩組的 `docs/phase3-closeout`，推完我就開 PR。 (disable recaps in /config)

!  git -C /c/workspace/software_fin/software_fin-openspec push -u origin        
  docs/phase3-closeout                                                          
  ⎿  remote:
     remote: Create a pull request for 'docs/phase3-closeout' on GitHub by
     visiting:
     … +7 lines (ctrl+o to expand)

● OpenSpec 收到了。等你推送 SpecKit：

  ! git -C /c/workspace/software_fin/software_fin-speckit push -u origin 
  docs/phase3-closeout

  兩組都推上去後，我再一起開兩個 PR。

✻ Baked for 9s · done Saturday 10:21 PM

! git -C /c/workspace/software_fin/software_fin-speckit push -u origin          
  docs/phase3-closeout                                                          
  ⎿  remote:
     remote: Create a pull request for 'docs/phase3-closeout' on GitHub by
     visiting:
     remote:      https://github.com/yue083139/software_fin-speckit/pull/new/doc
     s/phase3-closeout
     remote:
     To https://github.com/yue083139/software_fin-speckit.git
      * [new branch]      docs/phase3-closeout -> docs/phase3-closeout
     branch 'docs/phase3-closeout' set up to track
     'origin/docs/phase3-closeout'.

  Made 1 scratchpad edit +23, created PR #14 (ctrl+o to expand)

● 兩組的收尾 PR 都開好了，目標分支是 dev：

  - OpenSpec #15：https://github.com/yue083139/software_fin-openspec/pull/15
  - SpecKit #14：https://github.com/yue083139/software_fin-speckit/pull/14

  這是 C 級的純文件變更，一輪對抗評審已經通過，兩組門禁本機都跑過、全綠，所以 PR
  描述最後寫的是「都綠」。CI 我還沒看。

  剩下兩件事：
  1. 合併：說「合」，我就等 CI 跑完再合進 dev。
  2. 對話紀錄：你跑 /export 匯出今天的對話後，我會掃過個資和金鑰，另開一個小 PR
     放進 docs/ai-logs。收尾 PR 會先合，所以不併進去。

  組員那邊的人工驗證照舊依 docs/manual-verification.md。

✻ Brewed for 25s · done Saturday 10:21 PM

※ recap: 我們在收尾第三期的組隊功能：已合併的分支都刪了，兩組收尾 PR 也開好了（OpenSpec #15、SpecKit #14），本機門禁全綠，CI 我還沒看。下一步請你說「合」，我等 CI 跑完就合進 dev。

❯ 合                                                                            

  Merged PR #15, ran 2 shell commands (ctrl+o to expand)

● 兩組的收尾 PR 都已合進 dev：OpenSpec #15 在 0b8b803，SpecKit #14 在
  194f4a8。合併前兩組 CI 的 gate-pr 都通過，合入後兩組的 docs/parity.md
  逐字相同。

  第三期到此全部收完：契約補充記為已批准，組隊狀態改成「已合入」，OpenSpec 的
  change 也歸檔了。

  剩下的事：
  1. 刪收尾分支：兩組的 docs/phase3-closeout
     還在，本地和遠端都有。說「刪」我就刪。
  2. 對話紀錄：你跑 /export 後，我會掃過個資和金鑰，另開一個小 PR 放進
     docs/ai-logs。
  3. 人工驗證：請組員照 docs/manual-verification.md 的 A 到 E 場次執行。
  4. 選做卡：時間計分模式顯示題目文字。期限是 11/30，要做再跟我說。

✻ Churned for 34s · done 2:04 AM
~~~~
