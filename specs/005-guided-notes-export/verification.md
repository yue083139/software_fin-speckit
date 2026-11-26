# Verification: 005 guided-notes-export

## 門禁（2026-11-11，本機 Windows）

```
$ make gate-pr
All checks passed!
All checks passed!
122 passed, 1 warning in 17.01s
51 passed in 7.46s
 Test Files  3 passed (3)
      Tests  13 passed (13)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 16 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## 真棧實錄（第一期整體流程）

```
# 2026-11-11 真棧探針：QUIZ_TEACHER_KEY=e2e-key-000000 python -m quiz_server --port 8765；uv run --project server python probes/e2e_flow_probe.py http://127.0.0.1:8765 e2e-key-000000 tests/fixtures/guided-notes/group.xlsx
# 第一次執行：WebSocket 握手 HTTP 404，伺服器日誌「No supported WebSocket library detected」⇒ server 依賴補 websockets 後重跑如下
首頁 200
匯入 200 {'source': 'group.xlsx', 'count': 4}
重複加入第1組 409
第2組初始 preparing
開始 200
第2組收到 answering
第1組送出第3題 200 {'question': 3, 'answers': ['甲組祕密答案']}
第2組在他組送出後 1 秒內收到 0 則訊息
第2組送出第1題（題組） 200
結束 200
第2組看到結果 {'team': '第2組', 'answers': ['CPU', '作業系統']} {'team': '第1組', 'answers': ['甲組祕密答案']} {'第1組': 1, '第2組': 1, '第3組': 0, '第4組': 0}
匯出 200 attachment; filename="guided-notes-result.xlsx"; filename*=UTF-8''group-%E6%90%B6%E7%AD%94%E7%B5%90%E6%9E%9C.xlsx
匯出檔填入的格 [('G11', '甲組祕密答案'), ('G5', '（1）CPU'), ('G6', '（2）作業系統')]

# 第二個發現：uvicorn INFO 等級印出「WebSocket /ws?role=student&token=…」與「…role=teacher&key=…」接受紀錄（access_log=False 擋不到）。
# __main__.py 改 log_level="warning" 後重跑探針，伺服器輸出全文（金鑰以 <老師金鑰> 代替）：
老師頁：http://127.0.0.1:8765/#/teacher?key=<老師金鑰>
學生頁：http://127.0.0.1:8765/
# grep -c 'token=' 伺服器輸出 ⇒ 0
```

## 兩組程式一致

```
$ diff -r --strip-trailing-cr -x __pycache__ -x .venv -x uv.lock -x .pytest_cache -x .ruff_cache software_fin-openspec/server software_fin-speckit/server
（無輸出）
$ diff -r software_fin-openspec/web/src software_fin-speckit/web/src
（無輸出）
$ diff software_fin-openspec/contracts/api.md software_fin-speckit/contracts/api.md
（無輸出）
```

## 圖碼一致核對（憲章原則 VII）

| 圖 | 元素 | 程式落點 | 一致／偏離 |
|---|---|---|---|
| class | `guided_notes.fill`、`write_answers`（`data_type = "s"`） | `server/quiz_server/guided_notes.py:162`、`:169` | 一致 |
| class | `results.winning_answers` | `server/quiz_server/results.py:31` | 一致 |
| class | `app.XLSX_MEDIA`、`export_filename`、`GET /api/teacher/export` | `server/quiz_server/app.py:56`、`:59`、`:163` | 一致 |
| component | teacherDownload、匯出鈕 | `web/src/api.ts:48`、`web/src/pages/Teacher.tsx` | 一致 |
| sequence | 非 ended 或未匯入 409；loop 每題每子題 fill 後寫入 | `app.py:163` 起、`guided_notes.py:169` 起 | 一致 |

偏離：無。

## 交付版圖碼核對（001–005 全部圖，最終分支行號）

由腳本以正則逐一定位每個圖上元素的定義行，任一找不到即失敗；腳本只保證「找得到」，不保證「找對位置」，故經評審抽查 22 列並更正 1 列（2026-11-11 產生於 `005-guided-notes-export`）。各功能 verification.md 的表保留其實作提交當下的行號作為歷史紀錄。

| 圖 | 元素 | 程式落點 | 一致 |
|---|---|---|---|
| 001 class | `Phase` | `server/quiz_server/phases.py:8` | 一致 |
| 001 class | `check_transition` | `server/quiz_server/phases.py:27` | 一致 |
| 001 class | `TeamTakenError` | `server/quiz_server/activity.py:20` | 一致 |
| 001 class | `Activity` | `server/quiz_server/activity.py:52` | 一致 |
| 001 class | `Activity._checkpoint` | `server/quiz_server/activity.py:73` | 一致 |
| 001 class | `Activity.team_of` | `server/quiz_server/activity.py:87` | 一致 |
| 001 class | `Activity.join` | `server/quiz_server/activity.py:99` | 一致 |
| 001 class | `Activity.release` | `server/quiz_server/activity.py:111` | 一致 |
| 001 class | `Activity.start` | `server/quiz_server/activity.py:178` | 一致 |
| 001 class | `views.teacher_view` | `server/quiz_server/views.py:18` | 一致 |
| 001 class | `views.student_view` | `server/quiz_server/views.py:32` | 一致 |
| 001 class | `app.create_app` | `server/quiz_server/app.py:68` | 一致 |
| 001 sequence | `POST /api/student/join` | `server/quiz_server/app.py:116` | 一致 |
| 001 sequence | `WebSocket /ws（每連線送出迴圈）` | `server/quiz_server/app.py:207` | 一致 |
| 001 sequence | `view 相同不送` | `server/quiz_server/app.py:219` | 一致 |
| 001 component | `__main__ log_level=warning` | `server/quiz_server/__main__.py:23` | 一致 |
| 002 class | `Slot` | `server/quiz_server/guided_notes.py:27` | 一致 |
| 002 class | `Question` | `server/quiz_server/guided_notes.py:36` | 一致 |
| 002 class | `ParsedNotes` | `server/quiz_server/guided_notes.py:46` | 一致 |
| 002 class | `parse_workbook` | `server/quiz_server/guided_notes.py:102` | 一致 |
| 002 class | `export_url` | `server/quiz_server/sources.py:26` | 一致 |
| 002 class | `_allowed_hop` | `server/quiz_server/sources.py:43` | 一致 |
| 002 class | `download_sheet` | `server/quiz_server/sources.py:50` | 一致 |
| 002 class | `Activity.load_questions` | `server/quiz_server/activity.py:132` | 一致 |
| 002 component | `views.question_outline` | `server/quiz_server/views.py:13` | 一致 |
| 002 sequence | `POST /api/teacher/import-url` | `server/quiz_server/app.py:155` | 一致 |
| 003 class | `Submission` | `server/quiz_server/scoring.py:11` | 一致 |
| 003 class | `ScoringRule` | `server/quiz_server/scoring.py:29` | 一致 |
| 003 class | `ClassicBuzzRule` | `server/quiz_server/scoring.py:38` | 一致 |
| 003 class | `clean_answers` | `server/quiz_server/activity.py:32` | 一致 |
| 003 class | `Activity.submit` | `server/quiz_server/activity.py:152` | 一致 |
| 003 sequence | `submit 內讓出點` | `server/quiz_server/activity.py:161`（`submit` 自 :152 起；檔內其他 `_checkpoint()` 屬其他方法） | 一致 |
| 003 component | `POST /api/student/submit` | `server/quiz_server/app.py:122` | 一致 |
| 003 component | `RequestValidationError 不回顯本體` | `server/quiz_server/app.py:94` | 一致 |
| 004 class | `results.build` | `server/quiz_server/results.py:7` | 一致 |
| 004 class | `results.team_scores` | `server/quiz_server/results.py:25` | 一致 |
| 004 component | `student_view 只在 ended 加 results` | `server/quiz_server/views.py:48` | 一致 |
| 004 class | `Board` | `web/src/pages/Results.tsx:8` | 一致 |
| 004 class | `StudentResults` | `web/src/pages/Results.tsx:76` | 一致 |
| 005 class | `guided_notes.fill` | `server/quiz_server/guided_notes.py:162` | 一致 |
| 005 class | `guided_notes.write_answers` | `server/quiz_server/guided_notes.py:169` | 一致 |
| 005 class | `data_type = "s"` | `server/quiz_server/guided_notes.py:183` | 一致 |
| 005 class | `results.winning_answers` | `server/quiz_server/results.py:31` | 一致 |
| 005 class | `app.export_filename` | `server/quiz_server/app.py:59` | 一致 |
| 005 sequence | `GET /api/teacher/export` | `server/quiz_server/app.py:163` | 一致 |
| 005 component | `teacherDownload` | `web/src/api.ts:48` | 一致 |

## 人工驗證（需求 P-05）

狀態：**待執行**（交組員，照 `docs/manual-verification.md` 對應場次執行，結果回填本段）。步驟同 OpenSpec 組 `openspec/changes/archive/2026-11-12-guided-notes-export/verification.md`：匯出檔名、Excel 開啟確認作答格與框線、上傳回 Google 試算表確認答案在原填空格。

結果：＿＿＿（執行人／日期／看到什麼）
