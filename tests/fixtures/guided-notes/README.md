# Guided Notes 夾具

| 檔 | 來源 | 用途 |
|---|---|---|
| `single.xlsx` | 課程提供的「單題範本」，2026-11-11 以 Google Sheets `/export?format=xlsx` 下載 | 單題匯入／匯出 |
| `group.xlsx` | 課程提供的「題組＋單題範本」，同上 | 題組（X-01）匯入／匯出 |
| `variant.xlsx` | `build_variant.py` 產生的自製變形檔（合成內容） | 表頭在第 8 列 C 欄、欄名改為「編號／答案」、跨工作表、字串與浮點題號、3 子題題組、佔位符、未合併作答格；期望 5 題，子題數 [1, 3, 1, 2, 1] |
| `reference.xlsx` | `build_reference.py` 產生的自製檔（合成內容） | 可選參考答案欄（game-mode-framework）：表頭「題號／題目／作答／參考答案」、題組、一題無參考答案、佔位符；期望 4 題，子題數 [1, 2, 1, 1] |

- 結構摘要見 `docs/requirements.md` §4；重現：`make probe-guided-notes`。
- 內容皆為範本題目，無真實學生資料。
- 測試斷言的座標是「解析結果應等於檔案內容」的期望值，解析程式本身不得寫死座標（`docs/discipline-precedents.md`「Guided Notes 動態定位」）。
