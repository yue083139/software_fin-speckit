# Implementation Plan: 組隊模式——一組多台裝置、代表作答

**Branch**: `009-team-mode` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/009-team-mode-{component,class,sequence}.puml`

## Summary

1. **組隊是與模式正交的活動設定**（`team_play`）／代價：與 TRD 模式表名稱不一致／可被「三種模式 × 組隊開關計分相同」證偽；屬取捨（research R1）。
2. **同組第二台起須輸入 6 碼邀請碼，學生只在準備階段看得到，開始搶答與釋放都換新碼**／代價：組員多輸入一次，搶答中加入要問老師／可被「無碼、錯碼、舊碼 403 且不發憑證」證偽（R2）。
3. **每組每題仍只送一次，任一人送出代表全組**，判定沿用 003 的鎖與序號／可被「同組並發送出恰一筆成功」證偽（R3）。
4. **組內草稿只在 `answering` 送給本組**，老師與他組永遠拿不到／可被「他組草稿不在本組 payload、不觸發本組推播」證偽（R4、R5）。
5. **切換組隊、改組數、釋放都撤銷相關憑證與邀請碼**／代價：準備階段切換後要重新加入／屬取捨（R1、R2）。

**v1.1**：提案輪兩通道藥方已併入（research 開頭）；**契約四處語意補充已由負責人 2026-11-14 批准**（R7）。

**矩陣落點**：M-017（組隊加入與邀請碼）、M-018（代表作答）、M-019（組內草稿隔離）。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增
**Storage**: 記憶體 `team_play`、`_codes: dict[組別, 邀請碼]`、`drafts: dict[組別, dict[題號, tuple]]`
**Testing**: pytest、vitest
**Constraints**: `contracts/api.md` 新增為主，四處語意補充（R7）；組隊關閉時行為與 001–008 相同

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | X-04；parity §4 `team-mode`；OpenSpec 組同批 `team-mode` change | ✅ |
| II 作答隔離 | 草稿只進本組 view、邀請碼只在準備階段給本組；新增五則傳輸內容負例 | ✅ |
| III 順位以伺服器為準 | 送出沿用 003 的鎖與序號；同組並發測試 | ✅ |
| IV Guided Notes 動態定位 | 不讀寫 Guided Notes | ✅ |
| V 測試先行與人工驗證 | `test_team_mode.py`、隔離負例先寫；人工驗證場次 E | ✅ |
| VI 簡單與本機優先 | 不做聊天、隊長、分數平均 | ✅ |
| VII 圖表優先 | 三張圖先行 | ✅ |
| VIII 繁體中文與資料衛生 | 草稿不記日誌 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/activity.py       # team_play、set_team_play、join(team, code)、邀請碼、drafts
server/quiz_server/views.py          # team_play、devices、invite_codes、invite_code、drafts
server/quiz_server/app.py            # POST /api/teacher/team-play、/api/student/draft；join 本體 code
server/tests/test_team_mode.py（新）、test_isolation.py（增）
web/src/pages/Home.tsx、Student.tsx、AnswerForm.tsx、Teacher.tsx、team.test.tsx（新）
web/src/api.ts、types.ts
```

## Complexity Tracking

無違反憲章之處。
