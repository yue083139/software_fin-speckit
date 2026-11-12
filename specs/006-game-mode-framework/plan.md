# Implementation Plan: 遊戲模式框架、判定階段與「只計對錯」模式

**Branch**: `006-game-mode-framework` | **Date**: 2026-11-12 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/006-game-mode-framework-{component,class,sequence}.puml`；`diagrams/system-component.puml` 的 modes、judging

## Summary

1. **模式＝（判定規則, 是否需判定）的登記表，`Activity.rule` 改為 `mode.rule`**／代價：之後若模式差異超出這兩項要再加欄位（008 加 `sequential`）／可被「經典模式既有測試不改即綠」證偽。
2. **只計對錯：結束後進入 `judging`，全部判定完才能揭曉**／代價：老師必須判完每一筆（以參考答案建議與「採用全部建議」降低成本）／屬取捨：未判定就揭曉會把漏看的正確答案記為 0 分且無法回頭。
3. **得主＝最早送出的正確答案，正確者各 1 分**／代價：多組答對時匯出只寫回最早那組／可被規則表格式測試證偽；匯出程式不改。
4. **參考答案欄可選、只產生建議、永不送往學生**／代價：同義詞會被建議為錯誤／可被四階段學生 payload 負例證偽。
5. **`end()` 只接受 `answering`，`judging → ended` 只經 `reveal()`**／可被「判定中結束搶答 409」證偽。v1.2（實作期變異實錄）：判定模式下 `end()` 目標是 `judging`，`judging → judging` 不在轉移表，拿掉此前置條件仍 409——它是明寫的防線、非唯一防線，原「不擋即可繞過」不成立。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Storage**: 記憶體 `judgments: dict[題號, dict[組別, bool]]`
**Testing**: pytest（表格式規則、隔離負例、並發）、vitest
**Constraints**: 憲章原則 II、IV 不可協商；`contracts/api.md` 只增不改

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | X-04、TRD §6 裁定；parity §4 `game-mode-framework` 行為一致 | ✅ |
| II 作答隔離 | `judging` 學生 view 同 `answering`；參考答案與建議只在老師結果；判定不推播學生 | ✅ |
| III 順位以伺服器為準 | 得主依 `seq` 取最早正確者，不採信客戶端 | ✅ |
| IV Guided Notes 動態定位 | 參考答案欄以表頭別名定位；新夾具 `reference.xlsx`＋三份既有夾具 | ✅ |
| V 測試先行與人工驗證 | `test_judging.py`、`test_modes.py` 先寫；變異實錄兩則；人工步驟 | ✅ |
| VI 簡單與本機優先 | 不做同義詞比對；模式只兩種 | ✅ |
| VII 圖表優先 | 三張圖先行；實作後核對 | ✅ |
| VIII 繁體中文與資料衛生 | 夾具為合成內容；日誌不記答案 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/modes.py          # Mode、MODES
server/quiz_server/scoring.py        # Ranked.correct、AccuracyRule
server/quiz_server/judging.py        # normalize、suggest
server/quiz_server/guided_notes.py   # REFERENCE_ALIASES、Slot.reference
server/quiz_server/activity.py       # set_mode、end、judge、accept_suggestions、pending_judgments、reveal
server/quiz_server/results.py        # build(teacher=)
server/quiz_server/views.py          # mode、modes、pending_judgments、score_label
server/quiz_server/app.py            # /mode、/judge、/accept-suggestions、/reveal
server/tests/test_modes.py、test_judging.py（新）；test_scoring.py、test_isolation.py、test_results_view.py、test_guided_notes_parse.py、test_guided_notes_export.py（增）
tests/fixtures/guided-notes/build_reference.py、reference.xlsx
web/src/types.ts、pages/Teacher.tsx、Results.tsx、Student.tsx、judging.test.tsx
```

## Complexity Tracking

無違反憲章之處。
