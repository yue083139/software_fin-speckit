# software_fin 門禁與常用指令。認綠判據見 docs/discipline-precedents.md「都綠否的三條認綠判據」。
# 應用程式（server／web）的 dev、測試與 lint 目標由 app-skeleton 卡加入，並接進 test、lint 兩個目標。
SHELL := bash
.SHELLFLAGS := -eu -o pipefail -c
export PYTHONUTF8 := 1
OPS := uv run --group dev
SRV := uv run --project server
WEB := npm --prefix web
SIBLING ?= ../software_fin-openspec

.PHONY: help hooks dev web-install test lint gate-zh-hant gate-secrets gate-speckit gate-diagrams gate-diagrams-syntax gate-agents gate-parity gate-docs gate-pr gate probe-guided-notes sync-agents review-codex codex-venv diagrams

help: ## 列出所有目標
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  %-22s %s\n",$$1,$$2}'

hooks: ## 安裝本機 git 鉤子（pre-push 拒推 main／dev）；clone 後執行一次
	git config core.hooksPath .githooks
	@echo "core.hooksPath=$$(git config core.hooksPath)"

dev: ## 建置前端並啟動伺服器（http://127.0.0.1:8000，終端機會印出老師頁網址）
	$(WEB) run build
	$(SRV) python -m quiz_server

web-install: ## 依 package-lock.json 安裝前端依賴（clone 後與 CI 執行）
	$(WEB) ci --no-fund --no-audit

test: ## 全部單元測試：server、門禁腳本、前端；認 pytest 末行「N passed」與 vitest「Tests … passed」
	$(SRV) pytest -q server/tests
	$(OPS) pytest -q ops/tests
	$(WEB) test

lint: ## ruff（server、門禁腳本、探針）＋前端 ESLint 與型別檢查
	$(SRV) ruff check server
	$(OPS) ruff check ops probes
	$(WEB) run lint
	$(WEB) run typecheck

gate-zh-hant: ## 倉內不得含簡體專用字
	$(OPS) python ops/gate_zh_hant.py .

gate-secrets: ## 倉內不得含真憑證形狀
	$(OPS) python ops/gate_secrets.py .

gate-speckit: ## 憲章已填妥：無範本佔位符、有版本列、含圖表優先原則
	$(OPS) python ops/gate_speckit.py .

gate-diagrams: ## 每個 diagrams/*.puml 有同名 PNG、無孤兒、PNG 不比原檔舊
	$(OPS) python ops/gate_diagrams.py .

diagrams: ## 把 diagrams/*.puml 轉成同目錄的 PNG（有 Java 用 jar，否則用同版本 Docker 映像）
	$(OPS) python ops/diagrams.py render .

gate-diagrams-syntax: ## 以 PlantUML -checkonly 驗所有圖的語法（CI 必跑）
	$(OPS) python ops/diagrams.py check .

gate-agents: ## Codex 規範（AGENTS.md 等）與 CLAUDE.md 同步，手改或漏產生即紅
	$(OPS) python ops/sync_agents.py --check .

gate-parity: ## 兩組共用檔逐位元組一致：make gate-parity SIBLING=<另一 repo 路徑>；路徑不存在印「未跑」
	$(OPS) python ops/gate_parity.py . "$(SIBLING)"

sync-agents: ## 由 CLAUDE.md 與 .claude/skills 重新產生 Codex 規範；改 CLAUDE.md 後必跑
	$(OPS) python ops/sync_agents.py --write .

probe-guided-notes: ## 印出 Guided Notes 範本的表頭、合併範圍與非空儲存格
	$(OPS) python probes/guided_notes_structure_probe.py tests/fixtures/guided-notes/single.xlsx tests/fixtures/guided-notes/group.xlsx

CODEX ?= codex
codex-venv: ## Windows：讓 .venv 在 Codex 沙箱內可用（uv 管理的 Python＋複製模式安裝）
	uv venv --python-preference only-managed --python 3.12 --allow-existing .venv && UV_LINK_MODE=copy uv sync --group dev --reinstall

review-codex: ## 以 Codex 隔離會話評審：make review-codex CHANNEL=red|arch DISPATCH=<派單檔> [DIR=<工作樹>] [CODEX=<執行檔>]
	$(OPS) python ops/review_codex.py $(CHANNEL) $(DISPATCH) $(or $(DIR),.) --codex "$(CODEX)"

gate-docs: gate-zh-hant gate-secrets gate-speckit gate-diagrams gate-agents ## 純文件批的門禁

gate-pr: lint test gate-docs ## PR 門禁（B/C 檔）；CI 另跑 gate-diagrams-syntax

gate: gate-pr gate-diagrams-syntax gate-parity ## 全量門禁（S 檔；含圖表語法與兩組共用檔比對）
