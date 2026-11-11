# software_fin — Vibe Coding 課堂搶答系統（SpecKit 組）

NCU SE6005 2026 軟體工程期末專題。老師匯入填空式學習單（Guided Notes），開啟搶答後各組線上作答，伺服器判定最快送出的組別；結束後揭曉結果，並把搶答成功的答案寫回原 Guided Notes 的填空格。

本 repo 以 **SpecKit** 流程開發（constitution → specify＋PlantUML 圖 → clarify → plan → tasks → analyze → implement，導入 Diagram First Development）；姊妹 repo [`software_fin-openspec`](../software_fin-openspec) 以另一套流程實作**相同功能**。

| 文件 | 內容 |
|---|---|
| [`docs/requirements.md`](docs/requirements.md) | 需求基線（兩組共用，編號 R-／X-／P-） |
| [`docs/parity.md`](docs/parity.md) | 兩組功能一致協議、共用技術選型、功能清單與未決事項 |
| [`docs/trd-game-modes.md`](docs/trd-game-modes.md)、[`docs/research/competitors.md`](docs/research/competitors.md) | 多模式搶答 TRD（時間計分、雙倍分數、組隊等）與競品探索 |
| [`CLAUDE.md`](CLAUDE.md)／`AGENTS.md` | AI 代理工程規範（Claude Code／Codex） |
| [`docs/workflow.md`](docs/workflow.md) | 開發工作流導讀 |
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md)、[`specs/`](specs/)、[`diagrams/`](diagrams/) | 憲章、各子功能規格、PlantUML 圖表（評分檢驗 constitution／spec／plan／tasks／圖表） |

## 快速開始

```bash
make hooks            # 安裝 pre-push 鉤子（clone 後一次）
uv sync --group dev   # 門禁工具依賴
make gate-pr          # PR 門禁
make help             # 全部指令
```

需求：Python 3.12＋[uv](https://docs.astral.sh/uv/)、Node.js 24、GNU make、bash（Windows 用 Git Bash）。應用程式的啟動方式（`make dev`）由第一張功能卡 `app-skeleton` 加入。

## 狀態

| 卡 | 狀態 |
|---|---|
| 專案建置（治理文件、SpecKit 初始化、門禁、CI） | 已完成 |
| 功能卡 | 見 [`docs/parity.md`](docs/parity.md) §4 |
