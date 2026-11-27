# Implementation Plan: 018-results-podium

**Branch**: `018-results-podium` | **Date**: 2026-11-27 | **Spec**: `specs/018-results-podium/spec.md`
**藍圖**：`diagrams/018-results-podium-{component,class,sequence}.puml`（憲章原則 VII）

## Summary

1. **只用結束後 view 既有的 `team_scores`，不改伺服器**（R1）：老師頁以 `phase === "ended"` 決定是否畫，學生端 `StudentResults` 本來只在 `ended` 渲染／可被 `podium.test.tsx`「搶答中不顯示」證偽。
2. **名次口徑同伺服器 `results.leaderboard`**（R2）：同分同名次、下一名跳號，同名次依組別順序，只取前三／可被 `podiumPlaces` 四例證偽。
3. **0 分不上台、沒有組別得分整塊不顯示**（R3）／可被「沒有組別得分就不顯示領獎台」證偽。
4. **學生端標出本組**（R4）／可被「學生結果標出本組」證偽。

**矩陣落點**：M-028（R-04、R-08、X-04）守門 `web/src/pages/podium.test.tsx`。
**merge 三問第三問**：結果檢視（R-04／R-08）的收尾呈現，對標 Kahoot 結束領獎台，提升 Demo 與課堂參與感（X-04）；只改前端，範圍成本小。

## Technical Context
React 19＋antd 5＋TypeScript。新增 `web/src/pages/Podium.tsx`；`Teacher.tsx`、`Results.tsx` 各加一行掛載；`styles.css` 加領獎台樣式（只用 `--qz-*` 變量）。不改 server、contracts。

## Constitution Check
- 作答隔離：不新增送往學生端的資料，學生端只用 `ended` 才有的 `team_scores` ✅
- 順位以伺服器為準：不涉搶答先後；名次只是把伺服器分數排成畫面，口徑同 `leaderboard` ✅
- 圖表優先：三張圖先於實作 ✅；實作後核對見 `verification.md`
- 兩組一致：web 與 OpenSpec 組逐字相同 ✅

## 程式與圖對照
| 圖元素 | 程式 |
|---|---|
| Podium／podiumPlaces | `web/src/pages/Podium.tsx` |
| TeacherPanel（ended 才掛載） | `web/src/pages/Teacher.tsx` `TeacherPanel` |
| StudentResults（傳 team 標本組） | `web/src/pages/Results.tsx` `StudentResults` |
| useLiveView／view.team_scores | `web/src/live.ts`、伺服器 `views.py`（不改） |
