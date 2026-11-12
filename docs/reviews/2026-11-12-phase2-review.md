# 第二期評審紀錄（2026-11-12）

- 對象：第二期三張 S 檔卡 `game-mode-framework`、`question-settings`、`mode-timed-scoring`（兩組同批：OpenSpec change 與 SpecKit 006–008）。`question-settings` TRD 原建議 B 檔，因增改 `contracts/` 依分檔表取 S。
- 方式：提案輪＋實作輪各一輪，紅隊與架構兩通道互不知情（`.claude/agents/finder-tail-{red,arch}.md`＋`review-dispatch` 骨架）；藥方由各自開方的通道回驗。
- 結論：
  - 提案輪首輪：紅隊 `NOT CLEARED(0B/4M/3m)`、架構 `NOT CLEARED(0B/5M/4m)`；v1.1 回驗：紅隊 `CLEARED`、架構 `NOT CLEARED(0B/0M/2m)`（只剩次要，依分檔規則不阻塞，已併入 v1.2 修掉）。
  - 實作輪（末輪）：紅隊 `CLEARED`（另 3 次要：測試守不住的假綠，已補測試並以變異實錄證明轉紅）；架構 `NOT CLEARED(0B/1M/2m)`，三項皆為文件／契約與實作不符，已修，待架構通道回驗。

## 提案輪發現與藥方

| 通道 | 等級 | 發現 | 藥方落點 |
|---|---|---|---|
| 兩通道 | 重要 | 時間計分若公開他組累積分數，學生把前後兩次排行榜相減即可反推他組作答秒數（解析度約 0.04 秒）與答對先後 | 依負責人裁定原文「公開累積**排名**」，學生只拿名次與本組分數：TRD §6「排行榜的落實方式」、parity §4、mode-timed-scoring 首屏 5／D5、SpecKit 008 |
| 紅隊 | 重要 | Windows asyncio 計時器可能提早約 15.6 毫秒醒來，單次睡眠會讓某題永遠不自動關閉 | 計時器迴圈直到關閉（D3）；`test_timer_retries_after_early_wake` |
| 紅隊 | 重要 | 浮點計分在 T＝5–120 秒間有 5129 例少 1 分（如 T＝5、t＝1.285 應 872 得 871） | 整數式 `(2001T − ms) // (2T)`（D4）；點五案例測試 |
| 紅隊 | 重要 | 系統不送題目文字，學生持紙本可事先備答，速度分量到「誰先備好」 | 寫明代價並**呈負責人**（首屏 1）；建議時間計分前不先發學習單 |
| 架構 | 重要 | 主規格 results-view「結束前不得有結果」與時間計分揭曉後結果矛盾 | mode-timed-scoring `specs/results-view` MODIFIED |
| 架構 | 重要 | 主規格「順位 1 為搶答成功者」未限定經典模式 | game-mode-framework `specs/buzz-answering` MODIFIED |
| 架構 | 重要 | 第一期測試斷言經典規則忽略倍率，與雙倍題衝突，稿未提 | question-settings tasks 1.1 改寫該測試 |
| 架構 | 重要 | 雙倍題改了契約既有欄位的數值語意，未列為語意補充 | question-settings D3「契約語意補充」（**待負責人批准**） |
| 兩通道 | 次要 | TRD／parity 公式寫 `round`；view 缺 `mode.sequential`；送出路徑未寫明只讀一次時鐘；設定 API 本體放寬未列語意補充；同名次可知對方分數；名次測試以數字子字串比對會假紅 | 各卡 v1.1／v1.2 對應段落 |

## 實作期自查（變異實錄抓到的假綠）

- `game-mode-framework`：拿掉 `end()` 的 `_require(ANSWERING)` 仍綠——轉移表本身已擋 `judging → judging`，原設計「不擋即可繞過」不成立，已回寫 v1.2；v1.0 的「揭曉與判定並發」測試拿掉鎖仍綠（讀未判定數前無讓出點），換成「老師判定與採用全部建議」的真競態。
- `mode-timed-scoring`：「被接受送出 elapsed ≤ 時限」在假時鐘下恆真，改為「先開始的提早結束生效後送出必被拒」；截止測試拆成兩個新活動以免計時器先關閉回合。

## 實作輪發現與藥方

| 通道 | 等級 | 發現 | 藥方落點 |
|---|---|---|---|
| 架構 | 重要 | 時間計分在 `answering` 內判定，契約 `judge`／`accept-suggestions` 仍寫「409 非 judging」 | `contracts/api.md` 兩行補語意；design D6 表 |
| 架構 | 次要 | design 寫「尚無揭曉題時名次為空陣列」，實作為全員第 1 名 | design D5、SpecKit data-model |
| 架構 | 次要 | 008 時序圖晚送訊息寫「時間已到」，該情境實際為「沒有開放作答」 | 改圖重轉 PNG；核對表標偏離 |
| 紅隊 | 次要 | 作答毫秒「自開題起算」、重置清回合、開放中不可採用建議三處刪掉後測試仍綠 | `test_timed_mode.py` 補測；變異 R1–R3 必紅（008 verification） |

## 呈負責人

1. 契約語意補充三處（經典得主得 1×倍率、`team_scores` 欄名看 `score_label`；設定 API 本體放寬；時間計分的判定在 `answering` 內）——我傾向批准。
2. 時間計分的紙本備答代價——我傾向接受，並在人工驗證／Demo 時不先發學習單。
3. 三張卡的人工驗證（P-05），步驟在各卡 `verification.md`。
