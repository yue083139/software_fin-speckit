# Implementation Plan: 把搶答成功的答案寫回原 Guided Notes 的填空格

**Branch**: `005-guided-notes-export` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/005-guided-notes-export-{component,class,sequence}.puml`

## Summary

1. **以 002 匯入時記下的作答格位置寫回原檔**／代價：只保證儲存格值與合併範圍不變，圖片等 openpyxl 不完整支援的元素可能遺失／可被三份夾具往返測試證偽（探針 `probes/results/2026-11-11-openpyxl-writeback.txt`）。
2. **佔位符取代、否則接在標籤後；一律存為文字**／代價：學生刻意輸入公式也只顯示為文字（正是所要）／可被「`=1+1` 讀回仍為文字」測試證偽。
3. **只在 ended 可匯出；無人搶答題不變**／屬取捨：結果未定前匯出沒有意義。
4. **回到 Google 試算表以手動「匯入→取代」完成**／屬取捨：直接寫回需 OAuth 憑證（`docs/parity.md` §3）。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: openpyxl
**Testing**: pytest（往返比對）、vitest；真棧探針 `probes/e2e_flow_probe.py`
**Constraints**: 憲章原則 IV（動態定位）

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | R-05；parity §4 `guided-notes-export` | ✅ |
| II 作答隔離 | 匯出只有老師、只在 ended | ✅ |
| III 順位以伺服器為準 | 得主經 `ScoringRule`（`winning_answers`） | ✅ |
| IV Guided Notes 動態定位 | 依匯入解析的座標寫回；三份夾具往返 | ✅ |
| V 測試先行與人工驗證 | 先寫匯出測試；真棧探針；人工步驟 | ✅ |
| VI 簡單與本機優先 | 不接 Google API | ✅ |
| VII 圖表優先 | 三張圖＋核對 | ✅ |
| VIII 繁體中文與資料衛生 | 中文檔名 RFC 5987 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/guided_notes.py   # fill、write_answers
server/quiz_server/results.py        # winning_answers
server/quiz_server/app.py            # GET /api/teacher/export、export_filename
server/tests/test_guided_notes_export.py、test_api_export.py
web/src/api.ts（teacherDownload）、web/src/pages/Teacher.tsx（匯出鈕）
probes/e2e_flow_probe.py、probes/results/2026-11-11-e2e-flow.txt
```

## Complexity Tracking

無違反憲章之處。
