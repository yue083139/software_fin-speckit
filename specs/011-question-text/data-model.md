# Data Model: 011 question-text

對照 `diagrams/011-question-text-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Slot`（增） | `prompt: str = ""` | 該子題所在列的題目欄值（縱向合併只取錨點列）；只供顯示，`write_answers` 與 Google 寫回不讀 |
| `guided_notes`（增常數） | `QUESTION_ALIASES` | `("題目", "題目敘述", "問題", "題幹", "question")`；`_norm` 後全等比對 |
| `_find_header`（改回傳） | 另回 `question_col: int \| None` | 與題號欄、作答欄同一表頭列；與作答欄或參考答案欄同欄時為 `None` |
| view `questions[]`（增） | `prompts: list[str]` | 長度與順序同 `labels`；老師恆帶，學生依 R2 帶或不帶此鍵 |

`results`／`board` 不增欄位；學生無效憑證 view 不變。
