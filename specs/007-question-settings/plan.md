# Implementation Plan: 題目設定——雙倍分數題

**Branch**: `007-question-settings` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/007-question-settings-{component,class,sequence}.puml`

## Summary

1. **倍率只有 1 與 2**／代價：不能設三倍／屬取捨：TRD 與 Kahoot 都只有雙倍。
2. **倍率是規則輸入（`QuestionAttrs`），由規則乘進分數**／代價：`ScoringRule.rank` 的 `attrs` 型別由 `Mapping` 改為資料類別／可被「倍率 1 與 2 恰為兩倍」表格式測試證偽。
3. **只在準備階段可設；重新匯入清除、重置保留**／屬取捨：搶答中改倍率對已作答組別不公平。
4. **學生看得到倍率；欄名由伺服器決定**（`score_label`）／前端不自行判斷。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Storage**: 記憶體 `attrs: dict[題號, QuestionAttrs]`
**Testing**: pytest、vitest
**Constraints**: `contracts/api.md` 只增不改

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | X-04；parity §4 `question-settings` | ✅ |
| II 作答隔離 | 倍率非他組資訊；既有隔離負例不變 | ✅ |
| III 順位以伺服器為準 | 倍率只改分數不改順位與得主 | ✅ |
| IV Guided Notes 動態定位 | 不讀寫 Guided Notes | ✅ |
| V 測試先行與人工驗證 | `test_question_settings.py`、`test_multiplier_doubles` 先寫 | ✅ |
| VI 簡單與本機優先 | 只有 1／2 兩值 | ✅ |
| VII 圖表優先 | 三張圖先行 | ✅ |
| VIII 繁體中文與資料衛生 | 介面文案「雙倍分數」 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/scoring.py        # QuestionAttrs；規則乘倍率
server/quiz_server/activity.py       # attrs、set_question、SettingsError
server/quiz_server/results.py        # 傳入 attrs
server/quiz_server/views.py          # questions[].multiplier、score_label
server/quiz_server/app.py            # POST /api/teacher/question-settings
server/tests/test_question_settings.py（新）、test_scoring.py（增）
web/src/pages/ImportPanel.tsx、AnswerForm.tsx、Results.tsx、settings.test.tsx
```

## Complexity Tracking

無違反憲章之處。
