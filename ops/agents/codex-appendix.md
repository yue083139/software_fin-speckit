
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
