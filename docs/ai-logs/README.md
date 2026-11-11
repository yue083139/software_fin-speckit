# AI 對話紀錄

繳交表單要求附 AI 對話紀錄（`docs/requirements.md` §6）。一卡一會話，卡完成（合入或呈裁）時匯出一份：

- Claude Code：會話中執行 `/export`，存成 `docs/ai-logs/<YYYY-MM-DD>-<卡名>-<成員代號>.md`。
- Codex：複製會話紀錄或以 `codex` 的匯出功能存成同名格式。

入庫前自檢：`make gate-secrets` 綠（紀錄裡貼過的指令輸出可能含權杖）、不含真實學生姓名或學號。
