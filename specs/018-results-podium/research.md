# Research: 018-results-podium（與 OpenSpec design D1–D4 一一對應，R_n＝D_n）

知識時點：2026-11-27。

## 對標
- Kahoot：一局結束時顯示前三名領獎台（第 2、1、3 名由左到右、冠軍台最高），之後才看完整成績（依公開產品操作經驗）。Mentimeter 測驗結束同樣以前幾名排行收尾。
- 裁剪：只做靜態領獎台，不做逐名揭曉動畫與音效。

## R1 資料來源只用結束後 view 既有的 `team_scores`
- Decision：老師 view 任何階段都有 `team_scores`（`server/quiz_server/views.py`「"team_scores": results.team_scores(a)」），學生 view 只在 `ended` 才帶（同檔「只有 ended 才揭曉完整結果」）；老師頁以 `view.phase === "ended"` 決定是否畫。
- Rationale：不新增 view 欄位 ⇒ 作答隔離與契約不受影響，不升 S 檔；經典搶答結束後檢查答錯會改 `team_scores`（012-answer-review），領獎台隨推播即時更新。
- 證偽：「搶答中不顯示」；拿掉 `phase === "ended"` 判斷即紅。

## R2 名次口徑同伺服器 `results.leaderboard`
- Decision：`rank = 1 + 分數嚴格大於自己的組數`；同名次依 `team_scores` 鍵序（＝伺服器 `a.teams` 順序）；只取 `rank ≤ 3`。分數來源差異：`leaderboard` 用已揭曉題分數，領獎台用 `team_scores`（全部題）；兩者在 `ended` 時相等，前提是 `activity.end` 要求先揭曉目前題（`server/quiz_server/activity.py`「請先揭曉目前這一題，再結束活動」），日後若放寬須回頭改本決策。
- Rationale：與時間計分名次表同一口徑，老師不會看到兩套名次。`web/CLAUDE.md`「不在前端判定順位」指搶答先後，不受影響。
- 證偽：`podiumPlaces` 四例（基本、1-1-3 跳號、第三名並列全上台、三組並列第 1 不再有第三名）。

## R3 0 分不上台、沒有組別得分整塊不顯示
- Decision：過濾 `score > 0` 再排名；結果為空 ⇒ `Podium` 回 `null`。
- 證偽：「沒有組別得分 ⇒ 空」「沒有組別得分就不顯示領獎台」；變異 `s > 0` → `s >= 0` 兩例皆紅。

## R4 學生端標出本組
- Decision：`StudentResults` 傳 `team`，該組名旁加「本組」標籤；老師端不傳。
- 證偽：「學生結果標出本組」（第 1 名有、第 2 名沒有）。
