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

## 快速開始

```bash
make hooks            # 安裝 pre-push 鉤子（clone 後一次）
uv sync --group dev   # 門禁工具依賴
make gate-pr          # PR 門禁
make help             # 全部指令
```

需求：Python 3.12＋[uv](https://docs.astral.sh/uv/)、Node.js 24、GNU make、bash（Windows 用 Git Bash）；轉 PlantUML 圖需 Java 或 Docker（`make diagrams`）。

## 執行搶答活動

```bash
uv sync --project server --group dev
make web-install
make dev              # 建置前端並啟動 http://127.0.0.1:8000，終端機印出老師頁網址（含老師金鑰）
```

1. 老師開終端機印出的老師頁網址；學生（每組一台裝置）開 `http://127.0.0.1:8000/` 選組別。
2. 老師匯入 Guided Notes：上傳 xlsx（Google 試算表「檔案 → 下載 → Microsoft Excel」），或貼「知道連結者可檢視」的試算表連結。
3. 老師按「開始搶答」；各組作答、送出（每題每組一次，題組一次送出全部子題）；最先送出的組別得該題。
4. 老師按「結束搶答」後，學生看到結果；老師按「匯出 Guided Notes」下載填好答案的 xlsx。
5. 放回 Google 試算表：在原試算表「檔案 → 匯入 → 上傳 → 取代試算表」。

限制：伺服器重啟即清空活動（結束後請先匯出）；匯出只保證儲存格內容與合併範圍不變，圖片、資料驗證等 openpyxl 不完整支援的元素可能遺失；同一組只能一台裝置，裝置關閉後由老師在組別區按「釋放」。


## 狀態

| 卡 | 狀態 |
|---|---|
| 專案建置（治理文件、SpecKit 初始化、門禁、CI） | 已完成 |
| 第一期子功能 `001-app-skeleton`～`005-guided-notes-export` | 已實作，見 `specs/` 各功能 `verification.md` 與 `diagrams/` |
| 功能卡 | 見 [`docs/parity.md`](docs/parity.md) §4 |
