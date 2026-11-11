# diagrams — Diagram First Development

憲章原則 VII（PlantUML 設計優先）的產物目錄。`/speckit-specify` 階段在此產出圖表，`/speckit-plan` 以此為藍圖，`/speckit-implement` 後逐圖核對程式。

## 命名

| 檔名 | 內容 |
|---|---|
| `system-component.puml` | 全系統組件總覽（server、web 老師端、web 學生端、Guided Notes 檔案），由第一個功能建立，之後各功能增改 |
| `<NNN-功能>-component.puml` | 該功能涉及的組件與介面 |
| `<NNN-功能>-class.puml` | 該功能的類別／資料模型與組件描述 |
| `<NNN-功能>-sequence.puml` | 該功能的時序互動（老師、各組學生、伺服器、WebSocket 廣播） |

每個 `.puml` 旁邊必須有同名 `.png`（`make diagrams` 產生，一併提交）。

## 指令

- `make diagrams`：把 `diagrams/*.puml` 轉成 PNG，輸出在同目錄。優先用 `java -jar .tools/plantuml-<版本>.jar`（不在則自動下載，版本寫在 `ops/diagrams.py`）；本機無 Java 時改用 Docker 映像 `plantuml/plantuml`（版本同 jar）。
- `make gate-diagrams`：每個 `.puml` 有同名 `.png`、沒有孤兒 PNG、PNG 不比原檔舊。
- `make gate-diagrams-syntax`：以 PlantUML `-checkonly` 驗所有圖的語法（CI 必跑）。

## 圖碼一致核對（實作階段）

每個功能在 `specs/<NNN-功能>/verification.md` 留一張表：

| 圖 | 元素（組件／類別／訊息） | 程式落點 `path:line` | 一致／偏離 | 偏離處理 |
|---|---|---|---|---|

偏離時**先改圖、重轉 PNG，再改碼**，不得只改碼。
