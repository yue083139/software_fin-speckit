# Research: 002 guided-notes-import

知識時點：2026-11-11。範本實測結構見 `docs/requirements.md` §4 與 `probes/results/2026-11-11-guided-notes-structure.txt`。

## R1 表頭定位

- **Decision**：逐工作表、前 50 列掃描；NFKC 正規化、去空白後**整格等於**別名；同一列同時有題號類與作答類別名即為表頭列；作答欄若為合併範圍取最左欄。
- **Rationale**：官方範本表頭為「題號／題目／作答」，助教檔可能位移或改名；「包含」比對會把「題號說明」誤判為表頭。
- **證偽欄｜可證偽**：`test_variant_layout`（表頭第 8 列 C 欄起、「編號／答案」、跨工作表）、`test_header_aliases_must_match_whole_cell`、`test_fullwidth_and_english_aliases`。

## R2 題目與題組

- **Decision**：題號格（合併範圍左上角或未合併）為正整數（`1`、`1.0`、`"1"`、`"1."`）即開始一題；列範圍＝題號格縱向合併範圍；範圍內每列取作答欄（合併取左上角，同一左上角只算一次）；橫跨題號欄的合併列略過。
- **Rationale**：探針顯示 group 範本 `B5:B6` 合併 ⇒ 第 1 題作答格 G5、G6；single 範本分隔列 `B6:H6` 橫跨題號欄 ⇒ 不是作答格。
- **證偽欄｜可證偽**：`test_single_template`、`test_group_template`、`test_question_without_answer_cell`。屬取捨：「第2題」等非數字題號不算題目（followup 提示）。

## R3 佔位符與標籤

- **Decision**：作答格既有文字為標籤（如「（1）」）；含連續 3 個以上半形或全形底線為佔位符；學生顯示標籤去掉底線，題組無標籤時顯示 `(1)`、`(2)`。
- **證偽欄｜可證偽**：variant 夾具第 1 題佔位符、第 2 題 `(a)(b)(c)`。

## R4 連結來源與 SSRF 防護

- **Decision**：只收 https、`docs.google.com`、無自訂埠、id 字元集；改寫為 `/export?format=xlsx`（數字 `gid` 才保留）；httpx 手動逐跳（最多 5 跳），每跳限 `docs.google.com` 或 `*.googleusercontent.com`；串流 5 MB 上限；非準備階段先擋再下載。
- **Rationale**：探針顯示匯出會轉址 1 次；只驗第一跳無法排除轉往內網（OpenSpec 組提案輪評審指出）。
- **證偽欄｜可證偽**：`test_export_url_rewrite`、`test_export_url_rejects`、`test_import_url_redirect_to_foreign_host_is_refused`、`test_import_url_too_large`、`test_import_url_rejected_while_answering_sends_no_request`。

## R5 寫回可行性（為 005 先行探針）

- **Decision**：以 openpyxl 寫入合併格左上角。
- **證偽欄｜可證偽**：`probes/results/2026-11-11-openpyxl-writeback.txt`：合併範圍不變 True、其他非空格變動數 0、框線保留。
