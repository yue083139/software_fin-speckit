# Verification: 002 guided-notes-import

## 門禁（2026-11-11，本機 Windows）

```
$ make gate-pr
All checks passed!
All checks passed!
77 passed, 1 warning in 1.78s
51 passed in 5.51s
 Test Files  1 passed (1)
      Tests  7 passed (7)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 7 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## SC-002：解析程式無寫死座標

```
$ git grep -nE '"[A-Z]{1,2}[0-9]+"' -- server/quiz_server
（無輸出，退出碼 1）
```

## 圖碼一致核對（憲章原則 VII）

> 本表行號以本功能實作提交 `454bc07` 當下的程式為準（後續功能會移動行號）；交付版（最終分支）的行號見 `specs/005-guided-notes-export/verification.md`「交付版圖碼核對」。

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `GuidedNotesError`、`Slot`、`Question`（`is_group`）、`ParsedNotes` | `server/quiz_server/guided_notes.py:22`、`:27`、`:36`（`:41`）、`:46` | 一致 |
| class | `NUMBER_ALIASES`、`ANSWER_ALIASES` | `guided_notes.py:15`、`:16` | 一致 |
| class | `parse_workbook`、`_find_header`、`_parse_sheet`、`_as_number` | `guided_notes.py:102`、`:64`、`:118`、`:82` | 一致 |
| class | `SourceError`、`check_upload`、`export_url`、`_allowed_hop`、`download_sheet` | `server/quiz_server/sources.py:15`、`:19`、`:26`、`:43`、`:50` | 一致 |
| class | `Activity.questions`、`require_preparing`、`load_questions` | `server/quiz_server/activity.py:37`、`:96`、`:100` | 一致 |
| component | `views.question_outline`（學生只看題號與標籤） | `server/quiz_server/views.py:11` | 一致 |
| component／sequence | `POST /api/teacher/import`、`/import-url`（先 `require_preparing` 再下載） | `server/quiz_server/app.py:114`、`:122` | 一致 |
| component | ImportPanel、QuestionList、teacherUpload | `web/src/pages/ImportPanel.tsx`、`web/src/api.ts` | 一致 |
| sequence | loop 最多 5 跳、每跳 `_allowed_hop` | `sources.py` `download_sheet` 的 `for _ in range(MAX_REDIRECTS + 1)` | 一致 |

偏離：無。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應場次執行，結果回填本段）。步驟：

1. `make dev`，開老師頁。
2. 依序上傳 `tests/fixtures/guided-notes/single.xlsx`、`group.xlsx`、`variant.xlsx`，題目清單分別為 6 題、4 題（第 1、2 題為 2 子題）、5 題（第 2 題 3 子題、第 4 題 2 子題）。
3. 貼上課程「題組＋單題範本」的 Google 試算表連結，結果與上傳 group.xlsx 相同。
4. 學生分頁準備中只看到題號清單。

結果：＿＿＿（執行人／日期／看到什麼）
