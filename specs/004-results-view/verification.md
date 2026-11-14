# Verification: 004 results-view

## 門禁（2026-11-11，本機 Windows）

```
$ make gate-pr
All checks passed!
All checks passed!
110 passed, 1 warning in 12.36s
51 passed in 7.78s
 Test Files  3 passed (3)
      Tests  12 passed (12)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 13 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## 圖碼一致核對（憲章原則 VII）

> 本表行號以本功能實作提交 `4a15b14` 當下的程式為準（後續功能會移動行號）；交付版（最終分支）的行號見 `specs/005-guided-notes-export/verification.md`「交付版圖碼核對」。

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `results.build`、`results.team_scores`（經規則） | `server/quiz_server/results.py:7`、`:25` | 一致 |
| class／component | `teacher_view` 加 `board`、`team_scores` | `server/quiz_server/views.py:27`、`:28` | 一致 |
| class／component | `student_view` ended 才加 `results`、`team_scores` | `views.py:50` | 一致 |
| class | `Board`、`StudentResults`（只顯示） | `web/src/pages/Results.tsx:8`、`:76` | 一致 |
| sequence | 送出後推播老師 board；學生搶答中內容不變不推送；結束後推播 results | `app.py` 送出迴圈（001）＋ `views.py` | 一致 |

偏離：無。

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/archive/2026-11-12-results-view/verification.md`：三組各搶不同題，老師表即時更新、得主格變色；搶答中學生頁無結果；結束後三個學生頁與老師表一致。

結果：＿＿＿（執行人／日期／看到什麼）
