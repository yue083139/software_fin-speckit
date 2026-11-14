# 操作紀錄（ops-log）

AI 代理在本 repo 執行的對外或難以回復的操作（建立 repo、推送、改遠端設定、建立本機以外的資源）逐筆記錄；每個階段前打 `rollback/NN-<階段>` 標籤。

| 時間 | 分支 | 操作 | 影響 | 回復方式 |
|---|---|---|---|---|
| 2026-11-11 | main | 創世提交（治理文件、工具初始化、門禁、CI），打標籤 `rollback/00-genesis` | 僅本 repo | 刪除 GitHub repo 即全部回復（`gh repo delete yue083139/software_fin-speckit`） |
| 2026-11-11 | main、dev | `gh repo create yue083139/software_fin-speckit --private`，推送 `main`、由 `main` 開出並推送 `dev`（創世唯一例外，見先例正文「創世提交」） | GitHub 新增私人 repo | `gh repo delete yue083139/software_fin-speckit --yes` |
| 2026-11-11 | — | 本機拉取 Docker 映像 `plantuml/plantuml:1.2026.9`（`make diagrams` 無 Java 時的退路） | 本機 Docker 映像 | `docker image rm plantuml/plantuml:1.2026.9` |
| 2026-11-11 | 001…005 | 負責人以 `!` 推送五個功能分支與標籤 `rollback/01-pre-phase1`（指向第一期前的 dev 5927e4e）；開 PR #2–#6 | GitHub 新增分支與 PR | 刪除分支；以標籤回復 |
| 2026-11-11 | dev | 依負責人「合」合併：#2 入 dev；`--delete-branch` 使 #3 被關閉（事故，見先例正文「疊層 PR 的合併順序」）；#4–#6 改指 dev 後依序合入（#3 內容隨 #4 合入） | dev 含第一期五功能 | 以 `rollback/01-pre-phase1` 開回復分支經 PR 還原 |
| 2026-11-12 | dev | 負責人以 `!` 合併收尾 PR（OpenSpec #8、SpecKit #7）；本機 dev 設定追蹤 origin/dev 並快轉 | dev 含第一期收尾文件 | 以 `rollback/01-pre-phase1` 開回復分支經 PR 還原 |
| 2026-11-12 | 已合併的遠端功能分支 | 依負責人「清理分支」以 `gh api -X DELETE …/git/refs/heads/<分支>` 刪除兩 repo 共 8 支已合併遠端分支（OpenSpec 3 支、SpecKit 5 支；刪前以 `git rev-list` 與 `git diff` 確認內容皆已在 dev），並刪除對應本機分支 | GitHub 分支清單只剩 main、dev | 分支內容皆在 dev；需要時以已合併 PR 頁面的 Restore branch 還原 |
| 2026-11-12 | 本機 | 第二期三功能完成：疊層分支 006-game-mode-framework → 007-question-settings → 008-mode-timed-scoring；本機打標籤 `rollback/02-pre-phase2`（指向第二期前的 dev 4972652），待負責人以 `!` 推送分支與標籤 | 僅本機 | 刪除本機分支與標籤 |
| 2026-11-12 | dev | 依負責人「合」依序合併第二期疊層 PR #8–#10（每合一個前先把基底改為 dev，一般合併，整串合完前不刪分支）；dev 到 1625c4a | dev 含第二期三卡 | 以 `rollback/02-pre-phase2` 開回復分支經 PR 還原 |
| 2026-11-14 | 已合併的遠端功能分支 | 依負責人「刪」以 `gh api -X DELETE …/git/refs/heads/<分支>` 刪除第二期三支遠端分支（006-game-mode-framework、007-question-settings、008-mode-timed-scoring；刪前以 `git rev-list --count origin/dev..<分支>` 確認皆為 0），並刪除對應本機分支 | GitHub 分支清單只剩 main、dev | 以已合併 PR 頁面的 Restore branch 還原 |
| 2026-11-14 | 本機 | 第二期收尾、組員交接文件、第三期 `team-mode` 完成：疊層分支 docs/phase2-closeout → docs/team-handoff → 009-team-mode；本機打標籤 `rollback/03-pre-phase3`（指向第三期前的 dev 1625c4a），待負責人以 `!` 推送分支與標籤 | 僅本機 | 刪除本機分支與標籤 |
