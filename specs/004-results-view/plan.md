# Implementation Plan: 老師即時作答狀況與結果、學生結束後檢視結果

**Branch**: `004-results-view` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/004-results-view-{component,class,sequence}.puml`

## Summary

1. **老師頁＝題號 × 組別矩陣，即時顯示答案、順位、得主與得題數**／代價：組數多時表格寬（≤ 12 組可接受，加橫向捲動）／可被老師 view 測試證偽。
2. **學生在 `ended` 才收到結果**／代價：結束瞬間 payload 較大（本機可忽略）／可被「answering 無結果欄、ended 有且正確」測試證偽。
3. **結果一律經 `ScoringRule`，老師與學生同源**／可被一致性測試證偽。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Testing**: pytest（`test_results_view.py`）、vitest（`results.test.tsx`）
**Constraints**: 憲章原則 II（結束前無結果）

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | R-04、R-08；parity §4 `results-view` | ✅ |
| II 作答隔離 | 學生 `results`、`team_scores` 只在 ended；003 的隔離測試仍覆蓋 answering | ✅ |
| III 順位以伺服器為準 | 前端不重算；結果只經規則 | ✅ |
| IV Guided Notes 動態定位 | 不涉及 | N/A |
| V 測試先行與人工驗證 | 先寫 `test_results_view.py` | ✅ |
| VI 簡單與本機優先 | 整場結束揭曉 | ✅ |
| VII 圖表優先 | 三張圖＋核對 | ✅ |
| VIII 繁體中文與資料衛生 | 介面繁中 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/results.py   # build、team_scores
server/quiz_server/views.py     # teacher_view board、student_view results
server/tests/test_results_view.py
web/src/pages/Results.tsx       # Board、StudentResults
web/src/pages/Teacher.tsx、Student.tsx、results.test.tsx
```

## Complexity Tracking

無違反憲章之處。
