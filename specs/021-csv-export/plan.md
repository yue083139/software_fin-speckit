# Implementation Plan: 021-csv-export

**Branch**: `021-csv-export` | **Date**: 2026-11-28 | **Spec**: `specs/021-csv-export/spec.md`

**藍圖**：`diagrams/021-csv-export-{component,class,sequence}.puml`

## Summary

1. **前端使用既有老師 view 產出 CSV**：不加 API、不改 frozen contract；排名與分數直接取自伺服器 `board`、`team_scores`，不在匯出重算。
2. **每題 × 每組輸出一列**：含未作答組別與總分；題組答案附子題標籤；可由測試逐列核對。
3. **UTF-8 BOM、CRLF、CSV 引號跳脫與公式前綴防護**：方便 Excel 開啟並避免答案被當成公式；可由特殊字元輸入測試證偽。
4. **僅活動結束後提供下載**：與 xlsx／Google Sheets 匯出階段一致；由假 view 的 UI 測試證偽。

**矩陣落點**：M-034（X-02），守門 `web/src/resultsCsv.test.ts` 與人工驗證場次 L。

**merge 三問第三問**：直接補齊選做需求 X-02，僅改前端呈現、不新增依賴或 API 成本。

## Technical Context

React＋TypeScript；新增純函式 CSV serializer 與 Blob 下載 helper，老師頁活動控制按鈕在 ended 才可用。無新增套件。

## Constitution Check

- 結果與順位：只格式化老師 view 的伺服器結果，不另行判定。
- 作答隔離：不增學生端 view、通道或資料。
- 圖表優先：實作後核對圖表與程式，記錄於 `verification.md`。
- 兩組一致：OpenSpec 與 SpecKit 的 web、共用文件逐字一致。
