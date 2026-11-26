# Research: 012 answer-review（v1.0）

知識時點：2026-11-26。本卡不依賴倉外行為（Google 端只改副本名稱字串與寫入範圍，端點與 `RAW` 寫法沿用 010 已探針的 `values:batchUpdate`），故無新探針；現行行為以原始碼引述為證。本檔 R1–R6 與 OpenSpec 組 `openspec/changes/answer-review/design.md` D1–D6 一一對應、口徑相同。

## 背景與對標


負責人 2026-11-26 裁定：經典搶答**結束後**，老師在作答狀況與結果表逐題從第 1 順位檢查，「答錯」換下一順位、「答對」鎖定；未檢查的題維持最快者得主（R-10）；得主與各組得分跟著變；全部答錯 ⇒ 無得主、匯出留空；只套經典搶答；副本改名「<原標題>_作答情況」。

對標（知識時點 2026-11-26，依公開說明與課堂常見做法）：電視益智節目與課堂「搶答＋錯誤遞補」——主持人判第一個按鈴者答錯後，機會依按鈴順序交給下一位；Kahoot 的「type answer」題由系統以預設答案比對、主持人不逐筆改判；Mentimeter 測驗不提供逐組遞補。本卡採前者「依順序遞補、主持人判定」的做法，但把判定放在結束後（負責人裁），避免搶答中判定與新送出交錯。裁剪：不做自動比對（參考答案建議只留在判定模式，`game-mode-framework`）。

現行：

- 經典規則不看判定：`server/quiz_server/scoring.py:62`「`Ranked(s.team, s.answers, s.seq, i, i == 1, m if i == 1 else 0)`」。
- 判定端點只在判定中或逐題已關閉：`server/quiz_server/activity.py:413`「`self._require(Phase.JUDGING)`」；經典模式 `judged=False` 永不進 `judging`（`server/quiz_server/modes.py`「`Mode("classic", "經典搶答", False, ClassicBuzzRule())`」）。
- Google 寫回跳過無得主題：`server/quiz_server/google_sheets.py:129`「`if values is None:`」。
- 副本名稱：`server/quiz_server/google_sheets.py:17`「`COPY_SUFFIX = "-搶答結果"`」；下載檔名 `server/quiz_server/app.py:107`「`return f"{stem}-搶答結果.xlsx"`」。

## R1 資料模型：共用 `Activity.judgments`，經典規則改讀判定

- 檢查結果存在既有 `Activity.judgments: dict[題號, dict[組別, bool]]`（`activity.py`「`self.judgments: dict[int, dict[str, bool]] = {}`」），不另設結構：經典模式在 `ended` 前不會有任何判定（`/judge` 在經典模式恆 409），故共用不與判定模式衝突；`_clear_answers`（重新匯入、重置）已一併清空。
- `ClassicBuzzRule.rank(submissions, judgments, attrs)`：依 `seq` 排序後，**候選**＝第一個 `judgments.get(team)` 不是 `False` 的送出；候選即得主（`is_winner=True`、`score=1×倍率`），其餘 `score=0`；`Ranked.correct` 帶該組判定（`True`／`False`／`None`）。全部為 `False` ⇒ 無得主、全 0。
- **鎖定**＝候選的判定為 `True`；**未檢查**＝候選判定為 `None`（仍是得主，維持 R-10）。
- 無任何判定時輸出與現行逐筆相同（`correct=None`、順位 1 得主）。
- `team_scores` 不變（`_sum_scores`）；`score_label` 不變（經典且倍率全 1 仍為「得題數」）。
- `pending_judgments` 語意不變（只在判定模式顯示，前端不在經典模式讀）。
- 證偽欄｜可證偽：`test_scoring.py` 新增四例——無判定與現行輸出逐欄相同；順位 1 為 `False` ⇒ 順位 2 得主、分數 1×倍率；順位 2 為 `True` 鎖定；全部 `False` ⇒ 無 `is_winner`、分數全 0。屬取捨：另設 `reviews` 結構可讓兩種判定語意分開，但會多一條清空路徑與一個 view 欄位；共用的前提「經典在 `ended` 前無判定」由 R2 階段檢查保證。

## R2 端點：`POST /api/teacher/review` 與 `POST /api/teacher/review-reset`

- `POST /api/teacher/review` 本體 `{question, team, correct}`：
  - 錯誤先後：401 老師金鑰 → 409「只有經典搶答可以檢查」（模式非 classic）→ 409「搶答結束後才能檢查」（非 `ended`）→ 404 題號不存在 → 409「本題已鎖定，請先重設本題」（候選判定為 `True`）→ 409「本題沒有可檢查的答案」（無送出或全部已判錯）→ 409「這一組不是目前要檢查的答案，請重新整理」（`team` ≠ 候選）→ 422 本體格式錯誤（FastAPI 驗證，先於上述）。
  - 成功：`judgments[question][team] = correct`，`_bump()` 推播；回 `{question, team, correct}`（不含答案）。
  - `team` 由老師端帶入目前畫面上的候選，伺服器在活動鎖內比對：連點兩下「答錯」第二下回 409，不會跳過一組。
- `POST /api/teacher/review-reset` 本體 `{question}`：401 → 409 模式 → 409 階段 → 404；成功清空該題 `judgments`（回到順位 1 為候選、未檢查），`_bump()`；回 `{question}`。
- 候選由唯讀方法 `Activity.review_candidate(number)` 取得（經 `rule.rank` 取 `is_winner` 那列，無則 `None`），`review` 在鎖內呼叫它比對；不在端點重算。
- 兩者都在 `Activity` 內以同一把鎖完成（`server/CLAUDE.md`「活動狀態只在 Activity 內改變」）。日誌只記題號、組別、結果。
- 證偽欄｜可證偽：`server/tests/test_review.py` 逐條錯誤碼與先後、連點負例、重設後候選回順位 1、每次成功恰推播一次給每條連線。屬取捨：沿用 `/judge` 可少一個端點，但其語意是「任一組、判定中」，改語意須動 `game-mode-framework` 契約；新端點只增不改。

## R3 適用範圍與階段

- 只在 `mode.key == "classic"` 且 `phase is ended`；只計對錯、時間計分不變。
- `ended` → `preparing`（重置）與重新匯入清空檢查結果（既有 `_clear_answers`）。
- 檢查不改階段；`ended` 中可反覆檢查、重設、匯出。
- 證偽欄｜屬取捨：負責人裁「只在結束後、只套經典」。可證偽：`test_review.py` 對 accuracy／timed 與 answering 各一負例 409；`test_isolation.py` 既有「非 ended 各階段學生 payload 不含判定」不需改即綠（檢查只能在 ended 發生）。

## R4 結果與推播：三處一致

- 老師 `board`、學生 `results`、`team_scores`、`winning_answers` 全經 `results._ranked` → `a.rule.rank(..., a.judgments.get(number, {}), ...)`（`server/quiz_server/results.py:12`），R1 改規則即三處同步；不在 view、匯出或前端重算（`server/CLAUDE.md`）。
- 學生 `ended` 的 `results[].ranking[].correct` 會出現 `true`／`false`（現行經典恆 `null`）；`ended` 已全部公開他組答案，判定公開不違反作答隔離。
- 老師端判斷「鎖定」「全部答錯」由 `board` 推得：候選＝`is_winner` 那列；鎖定＝候選 `correct === true`；全部答錯＝`winner === null` 且 `ranking` 非空且每列 `correct === false`。不另增 view 欄位。
- 證偽欄｜可證偽：`test_results_view.py` 新增「檢查後老師 `board` 與學生 `results` 得主、分數、`correct` 逐欄相同」；`test_api_skeleton.py` 推播測試涵蓋 review 後學生收到新 view。

## R5 匯出：寫選定答案；Google 寫回改寫全部子題

- `winning_answers` 不改（已經規則）：鎖定或未檢查的候選答案；全部答錯的題不列入。
- xlsx 下載每次由 `source_bytes` 重產（`guided_notes.write_answers`），無得主題保持原樣，**不改**。
- Google 寫回 `google_sheets.write_answers` 改為**每題每個子題都寫**：有得主 ⇒ `fill(slot, answer)`；無得主 ⇒ `slot.label`（佔位符原文、標籤原文，或 R5 右側填空格的 `""`），以 `RAW` 一次 `batchUpdate`。如此重匯出能把「先前有得主、後來全部判錯或重設」的格還原，副本與畫面一致。
- 副本中原本就不是作答格的儲存格不寫（仍只寫解析出的作答格）。
- 證偽欄｜可證偽：`test_google_sheets.py` 新增「第一次寫回有得主、全部判錯後第二次寫回該格為原標籤」與「`data` 長度＝全部子題數」；`test_api_export.py` 新增「順位 1 判錯後 xlsx 為順位 2 答案」「全部判錯該格與原檔相同」。屬取捨：多寫無得主格會把老師在匯出後手動填進副本作答格的內容蓋回原標籤；副本是系統產物，手冊提醒老師在副本以外的地方編修。

## R6 副本與下載檔名：「_作答情況」

- `COPY_SUFFIX = "_作答情況"`：匯入時 `files.copy` 的 `name` 為「<原標題>_作答情況」。既有副本不改名。
- `export_filename`：`<原檔名去副檔名>_作答情況.xlsx`；`Content-Disposition` 的 ASCII 後備名 `guided-notes-result.xlsx` 不變。
- 訂正落全：`git grep -n 搶答結果 -- :/` 共 69 處；其中**檔名／副本名**語意的現行引用點逐一改——`server/quiz_server/google_sheets.py`（2）、`server/quiz_server/app.py`（1）、`server/tests/test_google_sheets.py`（1）、`server/tests/test_api_export.py`（1）、`web/src/pages/ImportPanel.tsx`（1）、`contracts/api.md`（2）、`README.md`（1）、`docs/requirements.md` §4（1）、`docs/manual-verification.md`（2）、`openspec/specs/guided-notes-export/spec.md`（1）、`openspec/specs/guided-notes-import/spec.md`（1；兩者由 OpenSpec 組本卡規格增量改；本組對應 `specs/005-guided-notes-export/`、`specs/010-guided-notes-sheets-sync/` 為歷史功能文件，有意不改）、`docs/parity.md`（2，`guided-notes-export`、`guided-notes-sheets-sync` 兩列；`docs/parity.md` 由 `question-text` 分支先登記，合流時同批改）。**有意不改**：一般用語「搶答結果」（`docs/requirements.md` R-04、`openspec/specs/results-view/spec.md`、`server/quiz_server/results.py` 文件字串、`server/CLAUDE.md`／`AGENTS.md`、`web/src/pages/Results.tsx` 標題）；本組歷史功能文件與圖（`specs/005-guided-notes-export/`、`specs/010-guided-notes-sheets-sync/`、`diagrams/005-guided-notes-export-component.puml`、`diagrams/010-guided-notes-sheets-sync-sequence.puml`；新名稱見 `diagrams/012-answer-review-*.puml`）；歷史紀錄（`openspec/changes/archive/`、`docs/ai-logs/`、`probes/results/2026-11-17-sheets-sync-real-stack.txt`、`probes/google_sheets_probe.py` 探針固定名稱）。
- 證偽欄｜可證偽：驗收 #7 `git grep -n -- '-搶答結果' -- server web/src contracts README.md docs/requirements.md docs/manual-verification.md` 無輸出。

## 風險

- 老師誤按「答對」：以「重設本題」回到順位 1 重新檢查。
- 老師在學生已看完結果後改判：學生畫面即時更新得主與分數；屬預期（負責人裁「得主跟著變」）。
