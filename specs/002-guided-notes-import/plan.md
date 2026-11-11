# Implementation Plan: 匯入 Guided Notes 並動態辨識題號、題組與作答格

**Branch**: `002-guided-notes-import` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/002-guided-notes-import-{component,class,sequence}.puml`；`diagrams/system-component.puml` 的 guided_notes、sources

## Summary

1. **以表頭文字定位欄、以題號格縱向合併範圍定位題組**／代價：別名清單外的表頭寫法要加別名／可被三份版面不同夾具的測試證偽（research R1、R2）。
2. **上傳 xlsx 與 Google 試算表連結兩種來源**／代價：試算表須設「知道連結者可檢視」／可被探針證偽（`probes/results/2026-11-11-sheets-export.txt`：公開範本 200、不存在 id 404）。
3. **匯入時記下每個作答格的實際位置，匯出依此寫回**／代價：記憶體多存原檔／可被 005 的往返測試證偽；不以題號推算座標。
4. **連結下載逐跳限 Google 網域**／代價：手動處理轉址／可被「轉址到 127.0.0.1 的請求數為 0」測試證偽。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: openpyxl（解析）、httpx（下載，測試以 MockTransport 替身）、python-multipart（上傳）
**Storage**: 記憶體保存原檔位元組與解析結果
**Testing**: pytest、vitest；夾具 `tests/fixtures/guided-notes/{single,group,variant}.xlsx`
**Constraints**: 不寫死座標（憲章原則 IV）；測試不連網

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | R-02、X-01；與 parity §4 `guided-notes-import` 一致 | ✅ |
| II 作答隔離 | 學生 view 只含題號與子題標籤（`question_outline`），不含座標與原檔 | ✅ |
| III 順位以伺服器為準 | 不涉及 | N/A |
| IV Guided Notes 動態定位 | 表頭＋合併範圍定位；三份版面不同夾具；`git grep` 座標字面量零命中 | ✅ |
| V 測試先行與人工驗證 | 先寫 parse 與 API 測試；`verification.md` 人工步驟 | ✅ |
| VI 簡單與本機優先 | 只連 Google 匯出端點，免憑證 | ✅ |
| VII 圖表優先 | 三張圖＋實作後核對 | ✅ |
| VIII 繁體中文與資料衛生 | 夾具為課程範本與合成內容；不需金鑰 | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/002-guided-notes-import/
├── spec.md、plan.md、research.md、data-model.md、tasks.md、verification.md
└── contracts/README.md
```

### Source Code (repository root)

```text
server/quiz_server/guided_notes.py   # 類別圖 guided_notes、Slot、Question、ParsedNotes
server/quiz_server/sources.py        # 類別圖 sources
server/quiz_server/activity.py       # load_questions、require_preparing
server/quiz_server/views.py          # question_outline
server/quiz_server/app.py            # /api/teacher/import、/api/teacher/import-url
server/tests/test_guided_notes_parse.py、test_api_import.py
tests/fixtures/guided-notes/build_variant.py、variant.xlsx
web/src/pages/ImportPanel.tsx（含 QuestionList）、Teacher.tsx、Student.tsx
probes/openpyxl_writeback_probe.py、probes/results/*
```

**Structure Decision**: 沿用 001 的 web application 結構。

## Complexity Tracking

無違反憲章之處。
