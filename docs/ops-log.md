# 操作紀錄（ops-log）

AI 代理在本 repo 執行的對外或難以回復的操作（建立 repo、推送、改遠端設定、建立本機以外的資源）逐筆記錄；每個階段前打 `rollback/NN-<階段>` 標籤。

| 時間 | 分支 | 操作 | 影響 | 回復方式 |
|---|---|---|---|---|
| 2026-11-11 | main | 創世提交（治理文件、工具初始化、門禁、CI），打標籤 `rollback/00-genesis` | 僅本 repo | 刪除 GitHub repo 即全部回復（`gh repo delete yue083139/software_fin-speckit`） |
| 2026-11-11 | main、dev | `gh repo create yue083139/software_fin-speckit --private`，推送 `main`、由 `main` 開出並推送 `dev`（創世唯一例外，見先例正文「創世提交」） | GitHub 新增私人 repo | `gh repo delete yue083139/software_fin-speckit --yes` |
| 2026-11-11 | — | 本機拉取 Docker 映像 `plantuml/plantuml:1.2026.9`（`make diagrams` 無 Java 時的退路） | 本機 Docker 映像 | `docker image rm plantuml/plantuml:1.2026.9` |
| 2026-11-11 | 001…005 | 負責人以 `!` 推送五個功能分支與標籤 `rollback/01-pre-phase1`（指向第一期前的 dev 5927e4e）；開 PR #2–#6 | GitHub 新增分支與 PR | 刪除分支；以標籤回復 |
| 2026-11-11 | dev | 依負責人「合」合併：#2 入 dev；`--delete-branch` 使 #3 被關閉（事故，見先例正文「疊層 PR 的合併順序」）；#4–#6 改指 dev 後依序合入（#3 內容隨 #4 合入） | dev 含第一期五功能 | 以 `rollback/01-pre-phase1` 開回復分支經 PR 還原 |
