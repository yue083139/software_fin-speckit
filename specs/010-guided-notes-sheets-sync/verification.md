# Verification: 010 guided-notes-sheets-sync（v1.2）

知識時點：2026-11-17；本機 Windows 11、分支 `010-guided-notes-sheets-sync`。server、web/src、contracts 與 OpenSpec 組 `feat/guided-notes-sheets-sync` 逐字相同（`make gate-parity` 0 處不一致）。

## 圖碼一致核對（憲章原則 VII）

| 圖 | 圖上元素／訊息 | 程式落點 | 結果 |
|---|---|---|---|
| component | GooglePanel 登入／登出・登入狀態 | `web/src/pages/GooglePanel.tsx`；`Teacher.tsx` 輪詢 `googleStatus` | 一致 |
| component | ImportPanel 從 Google 試算表匯入（需登入）・上傳 xlsx 備援 | `web/src/pages/ImportPanel.tsx` `googleReady` | 一致 |
| component | PhaseControls 匯出到 Google 試算表・下載 xlsx（備援） | `web/src/pages/Teacher.tsx` `exportSheet` | 一致 |
| component | app.py `/api/teacher/google*`・`/api/google/callback`・import-url・export-sheet・export | `server/quiz_server/app.py` | 一致 |
| component | GoogleSession PKCE・state 一次性 10 分鐘＋cookie 綁定・權杖只在記憶體 | `server/quiz_server/google_auth.py` `STATE_TTL`、`COOKIE_NAME`、`state_digest` | 一致 |
| component | google_sheets import_copy・write_answers → Sheets／Drive | `server/quiz_server/google_sheets.py` | 一致 |
| class | `GoogleSession.status／begin／complete(state, code, cookie, error)／token／logout` | `google_auth.py` | 一致 |
| class | `GoogleConfigError` 400、`GoogleAuthError` 401、`GoogleCallbackError` 回呼 400、`GoogleApiError` 502、`SheetNotFoundError` 400 | `google_auth.py`、`google_sheets.py`；`app.py` 例外處理器 | 一致 |
| class | `Grid`、`OpenpyxlGrid`、`SheetsGrid`、`parse_grids`、`grids_to_xlsx` | `guided_notes.py`、`google_sheets.py` | 一致 |
| class | `Activity.source_sheet_id`、`source_bytes` | `server/quiz_server/activity.py` | 一致 |
| sequence | login → `{url}`＋Set-Cookie → 回呼比對 state 與 cookie → 換權杖 → 固定文案頁 | `app.google_login`、`app.google_callback`、`GoogleSession.complete`；`test_api_google.py` | 一致 |
| sequence | 匯入：require_preparing → 解析 id → 原檔標題 → files.copy → 讀副本 → 解析；失敗刪副本 | `app.import_url`、`google_sheets.import_copy`；`test_import_copies_first_then_reads_the_copy`、`test_parse_failure_deletes_copy` | 一致 |
| sequence | 寫回：非 ended 409 → batchUpdate（副本、RAW、`'` 跳脫）→ `{url}` | `app.export_sheet`、`google_sheets.write_answers`；`test_write_targets_only_the_copy_with_raw`、`test_sheet_name_quote_is_escaped` | 一致 |

偏離：實作中把類別圖的 `begin()` 回傳、`import_copy` 參數與回傳、例外類別、`grids_to_xlsx` 依程式補齊（圖改，行為不變）。

## 門禁（`make gate`，退出碼 0）

```
All checks passed!
All checks passed!
261 passed, 1 warning in 27.83s
58 passed in 7.13s
 Test Files  8 passed (8)
      Tests  38 passed (38)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 31 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 31 個圖檔語法通過
gate-parity: 0 處不一致
```

變異實錄與 OpenSpec 組共用（同一份程式），見 OpenSpec repo `openspec/changes/guided-notes-sheets-sync/verification.md`。

## 真棧

`probes/results/2026-11-17-sheets-sync-real-stack.txt`：登入 → 從 Google 試算表匯入（複製後讀副本）→ 兩組作答 → 結束 → 匯出到 Google 試算表；副本答案在 H 欄、G 欄標籤不變、「=1+1」為文字；原試算表未被寫入。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 場次 A2 第 6 步、A5 第 16～18 步重驗）。

結果：＿＿＿（執行人／日期／看到什麼）
