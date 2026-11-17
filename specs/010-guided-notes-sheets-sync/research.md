# Research: 010 guided-notes-sheets-sync

知識時點：2026-11-17。倉外行為探針：`probes/google_sheets_probe.py`，原樣輸出 `probes/results/2026-11-17-google-sheets.txt`（負責人帳號、「題組＋單題」範本在負責人雲端硬碟的副本、試算表 id 遮蔽；登入、讀取、複製、寫入四步皆 OK）。本檔 R1–R7 與 OpenSpec 組 `openspec/changes/guided-notes-sheets-sync/design.md` D1–D7 一一對應、口徑相同。

背景：現行連結匯入 `server/quiz_server/sources.py:39`「`out = f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=xlsx"`」下載 xlsx 後以 openpyxl 解析；匯出 `server/quiz_server/app.py:220`「`data = write_answers(act.source_bytes, act.notes, results.winning_answers(act))`」產生 xlsx，老師手動「取代試算表」。課程補充說明判此路不符。

## R1 認證：OAuth 2.0 授權碼流程＋PKCE，網頁應用程式用戶端

- **Decision**：用戶端類型「網頁應用程式」，重新導向 URI 固定 `http://127.0.0.1:8000/api/google/callback`；`GOOGLE_CLIENT_ID`、`GOOGLE_CLIENT_SECRET` 只經環境變數（`.env`，已在 `.gitignore`），未設定時 Google 功能停用、xlsx 備援照常。`POST /api/teacher/google/login`（需老師金鑰）產生一次性 `state`（`secrets.token_urlsafe(32)`）與 PKCE `code_verifier`，有效 10 分鐘，回傳授權網址；web 以新分頁開啟。`GET /api/google/callback?code&state` 不需老師金鑰（瀏覽器導回帶不了標頭），只接受伺服器發出、未過期、未用過的 `state`，否則 400；成功後回「登入完成，可關閉此分頁」，老師頁輪詢 `GET /api/teacher/google`。權杖只存 `GoogleSession`（伺服器記憶體），`access_type=offline` 取 refresh token，過期前 60 秒自動換新；登出呼叫撤銷端點並清空。權限範圍：`spreadsheets`、`drive`、`openid email`（顯示帳號）。
- **Rationale**：負責人裁定 OAuth；回呼不導回含老師金鑰的網址，避免金鑰出現在導向紀錄。
- **Alternatives**：服務帳號（負責人不採）；`google-auth-oauthlib`（不採：沿用既有依賴 httpx 手寫三支 REST 呼叫，測試沿用 `MockTransport` 替身，兩組程式逐字相同較易維持——屬取捨）。
- **證偽欄｜可證偽**：探針步驟 1「回呼 state 相符：True」「換權杖 HTTP 200；有 refresh_token：True；scope：https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets；expires_in：3599」。另實測：帳號不在測試使用者名單時 Google 顯示「已封鎖存取權：未完成 Google 驗證程序」且不導回回呼，故 `state` 須自帶過期。

## R2 讀取：Sheets API 格狀資料 → Grid → 既有解析

- **Decision**：`GET https://sheets.googleapis.com/v4/spreadsheets/{id}?includeGridData=true&fields=properties.title,sheets(properties(title,sheetId),merges,data.rowData.values.formattedValue)`（連結帶 `gid` 則只取該分頁）。解析器改吃最小介面 `Grid`（`title`、`cell(row, col)`、`max_row`、`max_column`、`merges`），openpyxl 工作表與 Sheets 格狀資料各一個轉接器；002 的表頭與題組定位規則一字不改。`formattedValue` 為顯示字串（題號讀成 `"1"`），既有 `_as_number` 已接受。試算表 id 解析沿用 `sources.py` 的網址驗證，但不再組下載網址。
- **證偽欄｜可證偽**：探針步驟 2「API 解析：[(1, ['G5', 'G6']), (2, ['G8', 'G9']), (3, ['G11']), (4, ['G13'])]」與「夾具解析」逐字相同（合併數 13）。（R5 實施前的座標；R5 後第 1、2 題變 H 欄，兩條路徑同步變。）

## R3 寫回：複製整份試算表，寫入副本

- **Decision**：Drive `POST https://www.googleapis.com/drive/v3/files/{id}/copy`，名稱「<原標題>-搶答結果」；再 `POST …/spreadsheets/{copyId}/values:batchUpdate`，`valueInputOption=RAW`，每個作答格一筆 `{range: "'<分頁>'!<A1>", values: [[文字]]}`（分頁名中的 `'` 以 `''` 跳脫），座標取自匯入時記下的 `Slot.cell`。只在 `ended`；回 `{url}`。重複匯出產生多份副本、不覆蓋。
- **Alternatives**：Sheets `spreadsheets.create`＋`sheets/{sheetId}:copyTo`——探針可行但分頁名變「「學習單」的副本」且只帶單一分頁，不採；好處是只需 `spreadsheets` 範圍，留作日後須發布時的退路。
- **證偽欄｜可證偽**：探針步驟 3「3A Drive files.copy：HTTP 200」「副本 … 合併與原檔相同：True」；步驟 4「副本讀回：'=1+1'；原檔同格：None（原檔應未被寫入）」——`RAW` 寫入以 `UNFORMATTED_VALUE` 讀回仍是字串。**屬取捨**部分：`drive` 為受限範圍，「測試中」實測可用，本專題不發布。

## R4 來源與備援

- **Decision**：匯入 ①「從 Google 試算表匯入」（需登入，R2）②上傳 xlsx（不需登入，不變）；刪除 `export_url`、`download_sheet`。匯出：來源為 Google 試算表 ⇒「匯出到 Google 試算表」（R3）＋「下載 xlsx（備援，不含格式）」，後者由格狀資料轉成的工作簿產生（只含值與合併）；來源為上傳 xlsx ⇒ 只有「下載 xlsx」。
- **證偽欄｜屬取捨**：公開連結下載正是課程補充說明點名的做法；xlsx 只當網路或授權失敗時的備援。

## R5 題組子題填空格（PR #18 followup，負責人裁定併入本卡）

- **Decision**：匯入時，作答格不屬合併範圍、含非佔位符標籤，且同列右側相鄰格仍在**作答表頭合併範圍欄寬內**、空白且不屬合併範圍 ⇒ 右側格為填空格（`Slot.cell`、`Slot.label=""`），標籤格文字作子題顯示標籤；否則維持現行（佔位符取代、或接在標籤後）。欄寬取自表頭合併範圍，不寫死欄位。
- **影響**：`group.xlsx` 第 1、2 題作答格 `G5/G6/G8/G9` → `H5/H6/H8/H9`；single 不變（作答格 `G:H` 本身合併）；variant 不變——`probes/guided_notes_structure_probe.py tests/fixtures/guided-notes/variant.xlsx` 原樣輸出子題作答格為合併範圍「H11:I11, H12:I12, H13:I13 … H17:I17, H18:I18」。
- **證偽欄｜可證偽**：`test_guided_notes_parse.py` 新增 group 子題座標斷言；`test_guided_notes_export.py` 斷言 `G5`「（1）」不變、`H5` 為答案。**屬取捨**部分：只看右側相鄰一格，不處理標籤與填空格隔欄的版面。

## R6 作答隔離與憑證

- **Decision**：學生 view 不含任何 Google 欄位；Google 狀態只經 `GET /api/teacher/google`（需老師金鑰），不放進老師 view。日誌不記授權碼、權杖、client secret；Google 錯誤只轉 `status` 字串。`ops/gate_secrets.py` 加 `GOCSPX-`（用戶端密鑰）、`ya29.`（access token）、`1//`（refresh token）形狀，夾具「前綴＋0×n」放行。
- **證偽欄｜可證偽**：`test_isolation.py` 新增「老師以假權杖登入後，學生 WebSocket／REST 完整 payload 與 caplog 不含權杖字串」；gate-secrets 變異實錄（植入真形狀字串 ⇒ 紅）。

## R7 契約（須負責人批准）

- **Decision**：`contracts/api.md` 新增 `GET /api/teacher/google`（`{configured, signed_in, email}`）、`POST /api/teacher/google/login`（`{url}`；400 未設定）、`GET /api/google/callback`（HTML；400 state 不符）、`POST /api/teacher/google/logout`、`POST /api/teacher/export-sheet`（`{url}`；401 未登入、409 非 ended 或非 Google 來源、502 Google 錯誤）；`POST /api/teacher/import-url` 語意改為需登入、以 Sheets API 讀取（401 未登入、502 Google 錯誤）；`GET /api/teacher/export` 不變。
- **證偽欄｜屬取捨**：匯入端點沿用舊名，web 改動最小。

## 未決呈裁

| 事項 | 我傾向 | 阻塞 |
|---|---|---|
| 副本名稱 | 「<原標題>-搶答結果」，重複匯出產生多份 | 不阻塞 |
| R5 是否套到 xlsx 上傳路徑 | 套，同一份學習單兩條路徑同一結果 | 不阻塞 |
| 契約改動（R7） | 照上表 | **阻塞實作** |
