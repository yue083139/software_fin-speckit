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

## 人工驗證（需求 P-05）

狀態：**待負責人執行**。步驟同 OpenSpec 組 `openspec/changes/guided-notes-export/verification.md`：匯出檔名、Excel 開啟確認作答格與框線、上傳回 Google 試算表確認答案在原填空格。

結果：＿＿＿（執行人／日期／看到什麼）
