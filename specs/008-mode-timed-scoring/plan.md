# Implementation Plan: 時間計分模式——逐題開放、伺服器計時、每題揭曉後排行榜

**Branch**: `008-mode-timed-scoring` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/008-mode-timed-scoring-{component,class,sequence}.puml`

## Summary

1. **逐題開放，同時至多一題進行中**／代價：失去「各組自選題目」（經典與只計對錯保留）；學生持紙本學習單可事先備好答案，速度分量到「誰先備好」（v1.1 紅隊，呈負責人）／屬取捨：作答秒數需共同起點（T-04）。
2. **截止判斷在送出路徑以伺服器單調時鐘比對（只讀一次），計時器迴圈直到關閉、只負責推送「已關閉」**／代價：多一個背景任務／可被假時鐘「時限＋0.001 秒送出 409」測試與變異實錄證偽。
3. **不採「全員送出即關閉」**：會讓學生推知他組已送出（作答隔離）／屬取捨。
4. **計分以整數 `(2001 × T − 作答毫秒) // (2 × T)` 精確實作四捨五入**：Python `round` 為銀行家捨入（探針 `round(2.5)=2`），浮點寫法有 5129 例少 1 分（v1.1 紅隊）／可被 TRD §4 三案例與點五案例證偽。
5. **揭曉後公開累積名次（不含他組分數），答案與他組分數只在 `ended` 公開**／代價：名次變化仍可推知他組本題大致對錯與相對快慢；同名次時可知對方累積分數與本組相同／屬取捨（負責人 2026-11-12 裁定「公開累積排名」；v1.1 兩通道：公開分數可反推秒數）。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增（`asyncio.create_task` 計時器）
**Storage**: 記憶體 `rounds: dict[題號, Round]`
**Testing**: pytest（可注入假時鐘）、vitest、真棧探針 `probes/timed_flow_probe.py`
**Constraints**: 憲章原則 II、III 不可協商

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | X-04、TRD M2；parity §4 `mode-timed-scoring` | ✅ |
| II 作答隔離 | 學生只拿本組 `revealed` 與已揭曉題排行榜；三種回合狀態負例；不因全員送出關閉 | ✅ |
| III 順位以伺服器為準 | 作答秒數與截止只用伺服器單調時鐘；得主依 `seq` | ✅ |
| IV Guided Notes 動態定位 | 匯出沿用 005 | ✅ |
| V 測試先行與人工驗證 | 假時鐘測試、變異實錄、真棧探針、人工步驟 | ✅ |
| VI 簡單與本機優先 | 不做連勝加分、亂序出題 | ✅ |
| VII 圖表優先 | 三張圖先行 | ✅ |
| VIII 繁體中文與資料衛生 | 日誌不記答案 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/modes.py          # Mode.sequential、timed
server/quiz_server/scoring.py        # QuestionAttrs.time_limit、timed_points、TimedRule
server/quiz_server/activity.py       # Round、rounds、open_next、close_question、close_due、reveal_question、clock 注入
server/quiz_server/views.py          # round、revealed、leaderboard
server/quiz_server/app.py            # open-next、close-question、reveal-question；設定 API time_limit
server/tests/test_timed_mode.py（新）；test_scoring.py、test_isolation.py、test_question_settings.py、test_modes.py（增）
probes/timed_flow_probe.py、probes/results/
web/src/pages/Teacher.tsx、Student.tsx、timed.test.tsx
```

## Complexity Tracking

無違反憲章之處。
