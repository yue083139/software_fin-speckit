# 011 question-text 介面契約

**狀態：負責人 2026-11-26 照傾向批准（research R3）**；實作時同批改 [`/contracts/api.md`](../../../contracts/api.md)。

| 位置 | 增加 | 規則 |
|---|---|---|
| 老師 view `questions[]` | `prompts: [每個子題一段字串]` | 任何階段都帶；長度與順序同 `labels`；無題目欄時為空字串 |
| 學生 view `questions[]` | `prompts: [每個子題一段字串]` | `preparing` 不帶；`answering`／`judging` 非逐題模式每題帶、逐題模式只帶已開放過的題；`ended` 每題帶；看不到的題不含此鍵 |

**不變**：REST 端點、錯誤碼、`results`／`board` 格式、學生無效憑證 view、匯出（xlsx 與 Google 試算表）。
