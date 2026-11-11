# Research: 001 app-skeleton

知識時點：2026-11-11。對標：Kahoot!、Mentimeter 皆由主持端推進、參與者被動跟隨階段（`docs/research/competitors.md`）。

每條決策附證偽欄（`docs/discipline-precedents.md` 提案品質准入第 2 條）。

## R1 狀態集中在 Activity，所有變更經同一把鎖，檢查與寫入之間有讓出點

- **Decision**：`Activity` 持有組別、階段、憑證；每個改變狀態的方法在 `asyncio.Lock` 內執行，並在「檢查」與「寫入」之間 `await self._checkpoint()`。
- **Rationale**：單一事件迴圈下，臨界區內若沒有讓出點，並發測試等於循序執行，拿掉鎖也全綠（假綠）。
- **Alternatives**：不加讓出點（測試證偽不了鎖）；多處理序（本機不需要）。
- **證偽欄｜可證偽**：`test_concurrent_transitions_serialized`、`test_concurrent_join_same_team_once`；變異實錄（鎖換成 `nullcontext`）兩者皆紅。

## R2 每連線各算各的 view，內容不變就不送

- **Decision**：WebSocket 每條連線一個送出迴圈：等待版本改變 → 計算 view → 與上次送出的相同就跳過；訊息帶每連線自己的 `seq`，不外露全域版本號。
- **Rationale**：若他組送出就推播給所有人，即使內容不變，學生也能從推播時機與版本號跳號得知「有人剛送出」，違反 R-09。
- **Alternatives**：廣播同一份 payload（作答隔離無法保證）；只推「有變更」訊號再讓前端拉（時機一樣洩漏）。
- **證偽欄｜可證偽**：`test_per_connection_seq_increments_by_one`；003 的 `test_other_team_submit_sends_nothing`。

## R3 老師金鑰

- **Decision**：啟動時 `secrets.token_urlsafe(16)`（可由環境變數 `QUIZ_TEACHER_KEY` 指定）；REST 標頭、WebSocket 參數；`secrets.compare_digest` 比對；uvicorn `log_level="warning"`。
- **Rationale**：uvicorn 在 INFO 等級會把含查詢字串的 WebSocket 網址印到終端機，`access_log=False` 擋不到（真棧探針實證）。
- **證偽欄｜可證偽**：`test_teacher_api_requires_key`、`test_teacher_ws_requires_key`；`probes/results/2026-11-11-e2e-flow.txt` 末段 `token=` 行數 0。

## R4 組別憑證

- **Decision**：`POST /api/student/join` 發憑證、一組一台；WebSocket 與送出都以憑證反查組別；老師可釋放；改組數撤銷全部。
- **Rationale**：只靠網址上的組別名稱時，改參數即可讀到他組答案（OpenSpec 組提案輪紅隊實證，`docs/parity.md` §5）。
- **Alternatives**：組別名稱＋共用口令（全組共用仍可外流）；帳號系統（超出本機模擬範圍）。
- **證偽欄｜可證偽**：`test_join_once_per_team`、`test_release_allows_rejoin_and_revokes_old_token`、`test_bad_token_gets_minimal_view`。屬取捨：同組只能一台裝置。

## R5 依賴：uvicorn 須搭配 websockets

- **Decision**：server 依賴加 `websockets`。
- **Rationale**：uvicorn 本身沒有 WebSocket 實作，真瀏覽器連 `/ws` 會得 404；FastAPI TestClient 不經 uvicorn，單元測試測不到。
- **證偽欄｜可證偽**：`probes/results/2026-11-11-e2e-flow.txt` 第一次執行的 404 與補依賴後的完整流程。
