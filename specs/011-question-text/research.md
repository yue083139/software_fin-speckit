# Research: 011 question-text（v1.0）

知識時點：2026-11-26。夾具結構以探針為準，原樣輸出 `probes/results/2026-11-26-question-text.txt`（四份夾具的表頭與題目欄逐列文字）。本檔 R1–R5 與 OpenSpec 組 `openspec/changes/question-text/design.md` D1–D5 一一對應、口徑相同。

背景：R-02 只要求題號，現行解析因此略過題目欄（`server/quiz_server/guided_notes.py:105`「`if number_col is None and text in NUMBER_ALIASES:`」）；學生 view 只有 `{number, labels, multiplier, time_limit}`（`server/quiz_server/views.py:17`）。負責人 2026-11-26 驗證全流程時指出學生頁「只有答題欄」。

## R1 解析：可選的題目欄，以表頭別名定位，逐子題讀取

- **Decision**：表頭列沿用 `_find_header` 掃描（同一列須同時有題號欄與作答欄，規則不變）；同一列另找題目欄，別名 `QUESTION_ALIASES = ("題目", "題目敘述", "問題", "題幹", "question")`，以 `_norm`（NFKC、去空白、小寫）全等比對；表頭格屬合併範圍時取最左欄。找不到 ⇒ 每個子題 `prompt` 為 `""`，匯入照常成功。每個 `Slot` 的 `prompt`＝該子題所在那一列的題目欄值；該格屬合併範圍時只有錨點列取值，其餘列為 `""`（與 `_reference` 縱向合併規則相同）；值去頭尾空白、保留內部換行；整數值的浮點數轉整數字串（`1.0` ⇒ `"1"`），其餘 `str()`。題目欄與作答欄或參考答案欄落在同一欄時不取。
- **Rationale**：題組每個子題各有一段敘述（探針 group C5、C6、C8、C9），逐子題取才對得上；可選欄不改 R-02 成功條件。
- **Alternatives**：每題只取第一列敘述（不採：題組第 2 子題會沒有題目）；把敘述併進 `labels`（不採：改變既有 `labels` 語意與寫回保留的標籤）。
- **證偽欄｜可證偽**：探針四份夾具皆有題目欄——single「C4: 題目」6 列、group「C4: 題目」6 列（第 1、2 題各 2 子題逐列各一段：C5、C6、C8、C9）、variant「D8: 題目敘述」8 列、reference「C3: 題目」5 列；`test_guided_notes_parse.py` 逐子題比對，另以 openpyxl 合成「無題目欄」與「題組敘述縱向合併」兩檔做負例。

## R2 可見性：學生只在開放作答後收到敘述

- **Decision**：老師 view 任何階段每題都有 `prompts`。學生 view（`team_valid: true`）：`preparing` 每題都不帶 `prompts` 鍵；`answering`／`judging` 非逐題模式每題都帶，逐題模式（`mode.sequential`）只有 `number in a.rounds`（開放中、已關閉、已揭曉）的題帶；`ended` 每題都帶。無效憑證 view 不變。判斷集中在 `views.question_outline(a, teacher: bool)` 一處；學生預設不帶，符合條件才加（fail-closed）。
- **Rationale**：原情境講義在活動開始前收回；逐題模式提早給敘述會讓各組在計時前先想答案，與時間計分（008）以伺服器量得作答秒數計分的用意衝突。
- **Alternatives**：準備階段也給（不採，屬取捨：較方便但削弱公平）。
- **證偽欄｜屬取捨**：可證偽部分＝`test_isolation.py::test_prompts_hidden_until_open`（準備階段 0 個 `prompts` 鍵）、`test_prompts_sequential_only_opened`（開第 1 題後只有第 1 題帶）。

## R3 契約：`questions[].prompts`

- **Decision**：老師與學生 view 的 `questions[]` 增加 `prompts: [每個子題一段字串]`，長度與順序同 `labels`；學生看不到的題不帶此鍵。`results`／`board` 不重複帶（前端以題號對 `questions[]` 取）。`contracts/api.md` 同批補述，須負責人批准。
- **證偽欄｜可證偽**：`test_api_skeleton.py`／`test_isolation.py` 斷言鍵名與長度；`web/src/types.ts` 型別 `prompts?: string[]`。

## R4 寫回與匯出不變

- **Decision**：`Slot` 新增 `prompt: str = ""`（frozen dataclass 加預設值，既有建構點不需改）；`write_answers` 與 Google 寫回只用 `cell`、`label`、`placeholder`，不讀 `prompt`。
- **證偽欄｜可證偽**：`test_guided_notes_export.py`、`test_google_sheets.py` 不改即綠。

## R5 web：作答卡與結果表顯示敘述

- **Decision**：學生作答卡每個子題輸入欄上方顯示 `prompts[i]`（非空才顯示）；單題顯示在題號標題下。老師題目清單與即時作答表題號旁顯示敘述。學生結束後結果表題號旁顯示敘述。純文字渲染（React 預設跳脫），`white-space: pre-wrap`，不解讀 HTML。
- **證偽欄｜可證偽**：`web/src/pages/answer.test.tsx`「有敘述顯示、無敘述不顯示」；`results.test.tsx` 結果表顯示敘述。

## 風險

- 學習單若把答案提示寫在題目欄，提示會隨敘述送給學生——老師檔案本身的內容，與他組作答無關，不屬作答隔離範圍；手冊提醒老師題目欄只放題目。
