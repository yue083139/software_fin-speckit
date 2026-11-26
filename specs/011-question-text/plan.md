# Implementation Plan: 匯入題目敘述，開放作答後顯示給學生

**Branch**: `011-question-text` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/011-question-text-{component,class,sequence}.puml`

## Summary

1. **題目欄為可選欄，以表頭別名定位，逐子題讀取**：別名「題目／題目敘述／問題／題幹／question」；每個子題取所在那一列的題目欄值（題組每個子題各有一段）／代價：沒有題目欄的檔照常匯入、敘述為空字串／可被四份夾具證偽（R1）。
2. **學生只在開放作答後收到敘述**：準備階段不送；逐題模式只送已開放過的題；`ended` 全送；老師任何階段都有／屬取捨：時間計分若提早給敘述，各組可在計時前先想答案（R2）。
3. **契約只增欄位**：`questions[].prompts`（與 `labels` 對齊）；學生看不到的題不帶此鍵（fail-closed）／可被 `test_isolation.py` 新增負例證偽（R3）。
4. **寫回與匯出不變**：敘述只讀不寫／可被既有匯出往返測試證偽（R4）。

**矩陣落點**：M-003（R-02）聲明不變，守門加 `test_guided_notes_parse.py::test_prompts_*`；新增 M-021（X-04）「題目敘述只在開放作答後送給學生」，守門 `server/tests/test_isolation.py::test_prompts_hidden_until_open`、`test_prompts_sequential_only_opened`。

**merge 三問第三問**：R-02 寫「不要求匯入題目敘述」，本功能屬 X-04；負責人 2026-11-26 驗證時指出學生只見題號無從作答。期限 2026-11-30，影片須與程式一致，故在錄影前做。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Storage**: `Slot.prompt`（記憶體，隨匯入結果）
**Testing**: pytest（四份夾具＋openpyxl 合成負例）、vitest
**Constraints**: `contracts/api.md` 改動須負責人批准（R3）；OpenSpec 組同批，server／web 程式逐字相同

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | X-04；parity §4 `question-text`；OpenSpec 組同批 change | ✅ |
| II 作答隔離 | 敘述來自老師檔案、非他組資料；學生端依階段 fail-closed；新增負例 | ✅ |
| III 順位以伺服器為準 | 不涉判定 | ✅ |
| IV Guided Notes 動態定位 | 題目欄以表頭別名定位，不寫死欄位；四份夾具 | ✅ |
| V 測試先行與人工驗證 | 驗收測試先寫；人工驗證場次 A 加一步 | ✅ |
| VI 簡單與本機優先 | 只增一個可選欄與一個 view 欄位 | ✅ |
| VII 圖表優先 | 三張圖先行 | ✅ |
| VIII 繁體中文與資料衛生 | 日誌不記敘述與答案 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/guided_notes.py   # QUESTION_ALIASES、表頭找題目欄、Slot.prompt
server/quiz_server/views.py          # question_outline(a, teacher) 依 R2 帶 prompts
server/tests/test_guided_notes_parse.py（增）、test_isolation.py（增）、test_api_skeleton.py（增）
web/src/types.ts、pages/AnswerForm.tsx、Student.tsx、Teacher.tsx、Results.tsx
web/src/pages/answer.test.tsx（增）、results.test.tsx（增）
contracts/api.md、eval/acceptance/matrix.yaml、docs/manual-verification.md 場次 A
```

## Complexity Tracking

無違反憲章之處。
