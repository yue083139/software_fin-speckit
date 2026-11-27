# Verification: 018-results-podium（v1.0）

## 門禁實錄

本機（Windows 11，無 `make`）依 `Makefile` 的 `gate-pr` 逐項執行，2026-11-27，分支 `018-results-podium`（自 `origin/dev` `f9aeec8`）：

```
uv run --project server pytest -q server/tests → 367 passed, 1 warning
npm --prefix web test                          → Tests  90 passed (90)
npm --prefix web run lint                      → 無輸出（exit 0）
npm --prefix web run typecheck                 → 無輸出（exit 0）
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-agents: 0 處漂移
diagrams（PlantUML 1.2026.9，Microsoft OpenJDK 21）→ 018 三張圖轉 PNG
gate-diagrams-syntax: 55 個圖檔語法通過
gate-diagrams: 55 個圖檔，0 處問題
```

web 第二次 `npm --prefix web test`：`Tests  90 passed (90)`。web 與 OpenSpec 組 `feat/results-podium` 逐字相同（`git diff --no-index` 兩邊 `web/src` 無差異）。

## 變異實錄（錯時會紅）

於 OpenSpec 組同一份 web 程式執行（兩邊 web 逐字相同）：

| 變異 | 結果 |
|---|---|
| `Teacher.tsx` 拿掉 `view.phase === "ended" &&` | `podium.test.tsx` 1 failed：「搶答中不顯示」 |
| `Podium.tsx` 的 `s > 0` 改 `s >= 0` | 2 failed：「沒有組別得分 ⇒ 空」「沒有組別得分就不顯示領獎台」 |

## 圖表一致性核對（憲章原則 VII）

| 圖 | 圖元素 | 程式 | 一致 |
|---|---|---|---|
| component | Teacher.tsx →（ended 時）Podium | `Teacher.tsx`「view.phase === "ended" && <Podium」 | ✅ |
| component | Results.tsx → Podium（傳 team） | `Results.tsx`「<Podium scores={scores} scoreLabel={scoreLabel} team={team} />」 | ✅ |
| component | server views 不改 | `git diff origin/dev -- server contracts` 為空 | ✅ |
| class | PodiumPlace（rank／score／teams） | `Podium.tsx` `interface PodiumPlace` | ✅ |
| class | Podium：podiumPlaces、STAND_ORDER [2,1,3] | `Podium.tsx` `podiumPlaces`、`STAND_ORDER` | ✅ |
| sequence | 結束 ⇒ 老師 view（ended、team_scores）⇒ Podium | `views.py` teacher_view `team_scores`；`TeacherPanel` | ✅ |
| sequence | 學生 view ended 才帶 team_scores ⇒ Podium 標本組 | `views.py`「if a.phase is Phase.ENDED」；`Student.tsx` → `StudentResults` | ✅ |
| sequence | 檢查答錯 ⇒ 新 team_scores ⇒ 重新計算 | `Podium` 每次渲染由 props 計算，無內部狀態 | ✅ |

## 評審紀錄

- 架構通道（全卡掃）：待派。
- 對抗通道（diff）：待派。

## 人工驗證（需求 P-05）

狀態：**已執行**（`docs/manual-verification.md` 場次 I）。

結果：✅ 第 1～4 步全部符合（jinny／2026-11-27／`018-results-podium` `4e4eaf4`，Windows 11 本機瀏覽器）。第 1 步首次操作時第2組誤送第 2 題（第1組較快得該題），第2組 0 分未上台，符合 FR-002「0 分不上台」；重置後依步驟重做，亞軍、冠軍位置正確。學生頁「本組」標籤、判錯後同分並列、重置後消失、全部 0 分不顯示皆符合。第 5 步（選做）未執行。
