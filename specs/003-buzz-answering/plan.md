# Implementation Plan: 開放／結束搶答、以組送出、伺服器判定最快組、作答隔離

**Branch**: `003-buzz-answering` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/003-buzz-answering-{component,class,sequence}.puml`；`diagrams/system-component.puml` 的 scoring、results

## Summary

1. **順位＝伺服器在活動鎖內配發的遞增序號，讀序號與寫序號之間有讓出點**／代價：不補償網路延遲／可被並發 50 輪測試與「拿掉鎖必紅」變異實錄證偽。
2. **全部題目同時開放，每組每題只能送出一次**／代價：不能修改已送出的答案／屬取捨：「最快」必須以第一次送出為準。
3. **判定寫成 `ScoringRule` 策略**（預留判定結果與題目屬性輸入、分數輸出）／代價：多一層介面／可被規則單元測試證偽。
4. **學生 view 在 `ended` 前只含自己組，他組送出不推播**／代價：學生不知道某題是否已被搶／屬取捨：「某題已被搶」本身就是他組作答狀況（R-09）。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: FastAPI（`RequestValidationError` 自訂處理器）、pytest-timeout（WebSocket 測試防掛起）
**Storage**: 記憶體 `submissions: dict[題號, list[Submission]]`
**Testing**: pytest（隔離負例擷取原始傳輸內容）、vitest
**Constraints**: 憲章原則 II、III 不可協商

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | R-03、R-06、R-07、R-09、R-10、X-01；parity §4 `buzz-answering` 已定行為一致 | ✅ |
| II 作答隔離 | `student_view` 非 ended 只含本組；三通道（WebSocket、成功回應、錯誤回應）＋日誌負例；他組送出 0 則推播；冒用參數負例 | ✅ |
| III 順位以伺服器為準 | 鎖內配號、讓出點、並發測試、變異實錄 | ✅ |
| IV Guided Notes 動態定位 | 子題數取自 002 的解析結果 | ✅ |
| V 測試先行與人工驗證 | `test_scoring.py`、`test_submit.py`、`test_isolation.py` 先寫 | ✅ |
| VI 簡單與本機優先 | 經典規則；遞補、計分模式留第二期 | ✅ |
| VII 圖表優先 | 三張圖＋核對 | ✅ |
| VIII 繁體中文與資料衛生 | 日誌不記答案 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/scoring.py        # 類別圖 Submission、Ranked、ScoringRule、ClassicBuzzRule
server/quiz_server/activity.py       # submit、clean_answers、AlreadySubmittedError、AnswerError、start 前置條件
server/quiz_server/results.py        # build（ended 時給學生；004 擴充）
server/quiz_server/views.py          # student_view 隔離
server/quiz_server/app.py            # /api/student/submit、RequestValidationError 處理器
server/tests/test_scoring.py、test_submit.py、test_isolation.py；conftest.py（ready_activity、loaded_client）
web/src/pages/AnswerForm.tsx、Student.tsx、answer.test.tsx
```

**Structure Decision**: 沿用 001。

## Complexity Tracking

無違反憲章之處。
