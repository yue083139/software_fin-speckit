# Implementation Plan: 經典搶答結束後依順位「答對／答錯」檢查，匯出改寫選定答案

**Branch**: `012-answer-review` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/012-answer-review-{component,class,sequence}.puml`

## Summary

1. **檢查狀態共用 `Activity.judgments`，經典規則改讀判定**：候選＝依順位第一個未被判錯者；無判定時與現行相同（R-10）；全部判錯無得主／代價：經典規則從「不看判定」變「看判定」／可被 `test_scoring.py`「無判定與現行逐欄相同」證偽（R1）。
2. **只在經典 `ended`、以 `POST /api/teacher/review {question, team, correct}` 與 `review-reset {question}` 檢查**：`team` 須等於候選（擋連點跳組）；已鎖定 409／屬取捨：負責人裁只在結束後、只套經典（R2、R3）。
3. **得主與分數跟著變，老師表、學生結果、匯出三處經同一規則**／可被 `test_results_view.py` 一致性證偽（R4）。
4. **Google 寫回範圍＝目前有得主的格＋上次寫過、這次已無得主的格**（以原標籤還原），從未寫過的無人搶答格不碰；匯出與寫回以伺服器鎖序列化／可被 `test_api_google.py::test_reexport_restores_previously_written_cells` 證偽（現行 `server/quiz_server/google_sheets.py:129`「`if values is None:`」跳過無得主題）（R5，v1.1）。
5. **副本「<原標題>_作答情況」、下載 `<原檔名>_作答情況.xlsx`**（負責人裁定）（R6）。

**矩陣落點**：M-005、M-006、M-008 聲明與守門更新；新增 M-022「經典搶答結束後依順位檢查，得主、分數、匯出一致；候選不符 409」。

**v1.1**：提案輪評審（紅隊 0B/2M/3m、架構 0B/1M/3m，皆 0 阻斷）藥方與實作偏離回稿見 research 抬頭；負責人 2026-11-26 裁定未決事項照傾向、批准契約。web 按鈕移到 `web-workbench`（antd）整合。

**merge 三問第三問**：最快答案可能錯；R-05 寫回的是「搶答成功的組別答案」。負責人 2026-11-26 指示；期限 2026-11-30，影片須與程式一致。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Storage**: 記憶體 `Activity.judgments`（共用）
**Testing**: pytest（Google 端以 `httpx.MockTransport` 替身）、vitest；人工驗證場次 A
**Constraints**: `contracts/api.md` 改動須負責人批准；OpenSpec 組同批（`openspec/changes/answer-review/`），server／web 程式逐字相同

## Constitution Check

- I 需求即法律：R-10 在未檢查時不變；R-05 寫回改為檢查後得主。✅
- II 契約即法律：新增兩端點、`ranking[].correct` 經典語意、老師 `board[].review`、檔名；負責人 2026-11-26 批准。✅
- IV 作答隔離：檢查只在 `ended`；`answering`／`judging` payload 不變。✅
- VII 圖表優先：三張圖為本計畫藍圖。✅

## Project Structure（受影響檔案）

```
server/quiz_server/scoring.py        # ClassicBuzzRule.rank 讀判定（R1）
server/quiz_server/activity.py       # review、review_reset、review_candidate、sheet_written、mark_sheet_written（R2、R3、R5）
server/quiz_server/results.py        # 老師 board[].review（R4）
server/quiz_server/app.py            # 兩端點、export_filename、匯出鎖（R2、R5、R6）
server/quiz_server/google_sheets.py  # COPY_SUFFIX、write_answers(restore=)（R5、R6）
contracts/api.md
web/（移到 web-workbench 整合：按鈕、匯出中停用、ImportPanel 副本名稱）
server/tests/test_scoring.py、test_review.py（新）、test_results_view.py、test_google_sheets.py、test_api_google.py、test_api_export.py
docs/manual-verification.md、README.md、docs/requirements.md §4
```

## 圖碼一致核對（實作後）

逐圖逐元素對照程式落點，寫入 `verification.md`（憲章原則 VII 實作階段）。
