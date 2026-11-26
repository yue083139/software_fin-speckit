# Data Model: 011 question-text

對照 `diagrams/011-question-text-class.puml`。

| 實體 | 欄位 | 說明 |
|---|---|---|
| `Slot`（增） | `prompt: str = ""` | 該子題所在列的題目欄值（縱向合併只取錨點列）；只供顯示，`write_answers` 與 Google 寫回不讀 |
| `guided_notes`（增常數） | `QUESTION_ALIASES` | `("題目", "題目敘述", "問題", "題幹", "question")`；`_norm` 後全等比對 |
| `Header`（新型別） | `tuple[int, int, int, int \| None, int \| None]` | 表頭列、題號欄、作答欄、參考答案欄、題目欄；`_find_header` 回傳此型別；題目欄與作答欄或參考答案欄同欄時為 `None` |
| `_prompt(grid, merged, row, col)`（新） | → `str` | 縱向合併非錨點列回 `""`；整數值浮點數轉整數字串；去頭尾空白 |
| `views._prompt_visible(a, number, teacher)`（新） | → `bool` | 老師恆真；學生依 R2 |
| view `questions[]`（增） | `prompts: list[str]` | 長度與順序同 `labels`；老師恆帶，學生依 R2 帶或不帶此鍵 |

`results`／`board` 不增欄位；學生無效憑證 view 不變。
