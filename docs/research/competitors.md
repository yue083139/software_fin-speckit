# 競品探索：課堂搶答與測驗遊戲（2026-11-11）

> 目的：為 `docs/trd-game-modes.md`（多模式搶答 TRD）找可借鏡的機制。兩組共用本檔。
> 知識時點：2026-11-11 網路搜尋；**官方說明頁**標「官方」，其餘為評測部落格（標「二手」），二手資訊在立卡前須再對官方頁或實測確認（`docs/discipline-precedents.md` 提案品質准入第 3、4 條）。

## 1. 競品機制對照

| 產品 | 計分方式 | 特殊題型／加成 | 團隊機制 | 對本系統的啟發 | 來源等級 |
|---|---|---|---|---|---|
| **Kahoot!** | 答對得分隨作答時間遞減：`round(1000 × (1 − (作答秒數 ÷ 題目時限) ÷ 2))`；0.5 秒內答對得滿分；答錯 0 分 | 每題可設「無分數／標準／**雙倍分數**（上限 2000）」；另有只計對錯（每題 1 分）的 Accuracy 模式與 Confidence 模式 | Team mode：隊伍分數＝**隊員分數平均** | 時間計分公式與雙倍題可直接採用；「只計對錯」可作為不想比速度時的模式 | 官方（公式、雙倍、團隊平均） |
| **Kahoot!**（連對） | 官方說明：連對（answer streak）**不加分**；曾短暫實驗過連對加成 | — | — | 連對加成是可選設計，不是業界預設；要做須自己論證公平性 | 官方＋官方部落格 |
| **Quizlet Live** | 不計分數，比**完成度**：先把全部題目答對的隊伍獲勝 | — | 系統**隨機分隊**（約 3–4 人）；每位隊員只看得到部分選項，必須互相溝通；**答錯一題全隊進度歸零** | 「全隊共同完成一組題目」適合題組（X-01）；「答錯重來」可做為高難度模式 | 二手（多篇教師部落格一致） |
| **Gimkit** | 答對賺遊戲幣，可買升級與道具（power-ups）再影響後續得分 | 多種 2D 遊戲模式 | 有團隊模式 | 道具／經濟系統太重，不適合 5 分鐘 Demo 與課堂填空題；不採 | 二手 |
| **Blooket** | 依模式而異（同一題庫可跑十餘種模式） | 塔防、咖啡廳等策略模式 | 依模式 | 「同一題庫、多種玩法」＝本系統的模式架構方向：題目與玩法分離 | 二手 |
| **Quizizz（現 Wayground）** | 計分加報表；可自訂節奏 | 自主步調（self-paced）與老師控場兩種節奏 | — | 「老師控場 vs. 自主步調」可作為模式的一個維度；本系統以老師控場為主 | 二手（含廠商自家頁） |
| **Mentimeter／Slido** | Mentimeter 有競賽式測驗與排行榜；Slido 以投票與問答為主 | — | — | 揭曉畫面與排行榜的節奏可參考；計分細節未查到官方說明 | 二手 |

## 2. 與本系統需求的差異（關鍵）

1. **本系統的題目沒有標準答案**：Guided Notes 是簡答填空，匯入時不含答案（需求 R-02 只要求題號）。競品的「答對才得分」都預設有答案鍵。⇒ 任何依對錯計分的模式都需要新增「**老師判定**」步驟（或匯入時可選的參考答案），這是**架構層的決策**，必須在 `buzz-answering` 卡就預留。
2. **核心需求是「最快的組別得該題」**（R-10），是**搶答（buzzer）**而非**全員作答後排名**。Kahoot 式的時間計分是另一種玩法，兩者要以「模式」並存，不能互相取代核心行為。
3. **以組為單位**（R-07）：本系統的「組」本身就是隊伍；Kahoot 的團隊模式（隊員分數平均）對應到「一組多台裝置各自作答」，與現行「一組一個帳號」的傾向（`docs/parity.md` §3）不同，須在組隊模式卡裁定。

## 3. 取用與不取用

| 機制 | 決定 | 理由 |
|---|---|---|
| Kahoot 時間計分公式 | 取用（時間計分模式） | 有官方公式、可機械驗證、學生熟悉 |
| 雙倍分數題 | 取用（題目屬性，任何計分模式皆可套用） | 實作成本低；老師可標記重點題 |
| 只計對錯 | 取用（作為計分模式之一） | 降低速度壓力，對應公平性需求 X-03 |
| 組隊（組內多人、分數合併） | 取用，待裁合併方式（平均／加總／代表作答） | 使用者明確要求；與 R-07 的關係需裁定 |
| 答錯全隊歸零（Quizlet Live） | 列為候選，不排入第一批 | 需要題組與多裝置分工才好玩，成本高 |
| 搶答錯誤時順位遞補 | 取用（搶答模式的強化） | 真實搶答節目的做法；同時回應 X-03「鼓勵還沒成功的組別」 |
| 遊戲幣、道具、塔防等 | 不取用 | 與填空複習目標無關，Demo 時間不夠 |

## 來源

- Kahoot! 官方：[How points work](https://support.kahoot.com/hc/articles/115002303908)、[Accuracy experience](https://support.kahoot.com/hc/articles/39818967108627)、[Confidence experience](https://support.kahoot.com/hc/en-us/articles/32200674639261)、[Team mode takeover（官方部落格）](https://kahoot.com/en/blog/2021/11/23/team-mode-takeover/)、[Answer Streaks 實驗（官方 Medium）](https://medium.com/inside-kahoot/experimenting-with-answer-streaks-to-help-make-learning-awesome-3b3357e42595)
- Quizlet Live（二手）：[TechCrunch 2016](https://techcrunch.com/2016/04/12/quizlet-creates-a-game-for-groups-in-the-classroom-quizlet-live/)、[Educators Technology](https://www.educatorstechnology.com/2023/05/what-is-quizlet-live-and-how-to-use-it.html)、[Climb the Ladder](https://climbtheladder.com/what-is-quizlet-live-the-classroom-game-explained/)
- 多產品比較（二手）：[Ditch That Textbook](https://ditchthattextbook.com/gameshow)、[Teachfloor](https://www.teachfloor.com/blog/blooket-vs-gimkit-vs-kahoot--vs-quizizz)、[Jotform：Blooket vs Gimkit](https://www.jotform.com/blog/blooket-vs-gimkit/)、[slideswith](https://slideswith.com/blog/blooket-vs-kahoot-vs-gimkit-vs-quizizz)
