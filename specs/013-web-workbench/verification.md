# Verification: 013 web-workbench（v1.1）

知識時點：2026-11-26；分支 `013-web-workbench`。web（含 `package.json`、`package-lock.json`、`vite.config.ts`）與 OpenSpec 組 `feat/web-workbench` 逐字相同（先原樣套用 OpenSpec `git diff 50c3605 d451dc9 -- web`，再同步 v1.1 修正檔；以 `cmp` 逐檔比對 0 處不同——`make gate-parity` 的共用清單不含 web 程式，故另以 `cmp` 核對）。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 元素／訊息 | 程式落點 |
|---|---|---|
| component | theme.ts（palette・quizTheme・cssVars） | `web/src/theme.ts` |
| component | styles.css 讀 `--qz-*` | `web/src/styles.css`（無任何色值常量） |
| component | main.tsx ConfigProvider（zh_TW、quizTheme）、React 19 補丁 | `web/src/main.tsx` |
| component | ui.tsx（Btn・PhaseTag・Section・Backdrop・GlassHeader）、Shell.tsx | `web/src/ui.tsx`、`web/src/Shell.tsx` |
| component | Teacher（頂欄＋Menu＋內容卡＋StudentLink） | `web/src/pages/Teacher.tsx` `Teacher`、`TeacherPanel`、`StudentLink`、`NAV` |
| component | Student・AnswerForm、Home、Results・Round、ImportPanel・GooglePanel | `web/src/pages/*.tsx` 同名檔 |
| class | `TeacherView.student_url?` | `web/src/types.ts` |
| class | `TestUtils.btn`／`allBtn` | `web/src/test-utils.ts` |
| sequence | 導覽點擊 → `scrollIntoView(id)` | `Teacher.tsx` `Menu onClick` |
| sequence | 開始搶答 → `POST /api/teacher/start` → PhaseTag 更新 | `PhaseControls` `act("start")`；`GlassHeader` 內 `PhaseTag` |
| sequence | 學生送出 → `POST /api/student/submit` | `AnswerForm` `send` → `studentSubmit` |

## 門禁實錄

- `npm --prefix web test` 連跑三次全量（OpenSpec 組同一份 web）：
  - 第 1 次：`Tests  41 passed (41)`
  - 第 2 次：`Tests  41 passed (41)`
  - 第 3 次：`Tests  41 passed (41)`
- 修前實錄：`× 只顯示進行中那一題與倒數`「AssertionError: expected '10 秒' to match /1[45] 秒/」；`Test timed out in 5000ms`。
- `make gate`、`make gate-parity SIBLING=../wt-os-web`：見提交時實錄（本檔末）。

## 評審紀錄

- 提案輪架構通道：CLEARED（0B/1M/3m）——逾時、D5／R5 文案範圍、`styles.css` 寫死色值、註解檔名，藥方併入 v1.1。
- 實作輪對抗通道：NOT CLEARED（0B/1M/0m）——倒數測試截止起算點，已修。
- followup（不改）：xlsx 上傳改成 antd `Upload` 後「選檔不送出、按『上傳 xlsx』才送」這條路徑沒有元件測試；主人 @yue083139。

## 人工驗證（需求 P-05）

狀態：**待執行**（負責人，整合後的本地棧）。

## 提交時門禁實錄

- `make gate`：`278 passed`（server）、`58 passed`（ops）、`Tests  41 passed (41)`（web）；`gate-zh-hant: 0 處簡體字`、`gate-secrets: 0 findings`、`gate-speckit: 憲章 v1.0.0，0 處問題`、`gate-diagrams: 37 個圖檔，0 處問題`、`gate-agents: 0 處漂移`、`gate-diagrams-syntax: 37 個圖檔語法通過`；其內建 `gate-parity`（預設比對 `../software_fin-openspec` 工作樹，該樹不在本卡分支）`1 處不一致`＝`docs/parity.md` 本卡狀態列。
- `make gate-parity SIBLING=../wt-os-web`（OpenSpec 組本卡分支）：`gate-parity: 0 處不一致`。
