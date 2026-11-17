# Research: 010 guided-notes-sheets-sync（v1.2）

知識時點：2026-11-17。倉外行為探針：`probes/google_sheets_probe.py`，原樣輸出 `probes/results/2026-11-17-google-sheets.txt`（負責人帳號、「題組＋單題」範本在負責人雲端硬碟的副本、試算表 id 遮蔽；登入、讀取、複製、寫入四步皆 OK）。v1.2 新增的 `openid email`、換新、撤銷三步待負責人重跑探針後回填（tasks T004）。本檔 R1–R7 與 OpenSpec 組 `openspec/changes/guided-notes-sheets-sync/design.md` D1–D7 一一對應、口徑相同。

**v1.2（提案輪評審，紅隊＋架構雙通道，皆 CLEARED 0 阻斷）**：架構——`prompt=consent` 未寫進稿、`openid email`／換新／撤銷未探針（R1）；匯入後原檔被改、匯出時才複製會用舊座標寫錯格（R3，兩通道同抽）；兩組口徑缺分頁名跳脫、錯誤碼先後（R3、R7）；R-05「原 Guided Notes」的解讀未落需求（R4）；「框線相同」無探針。紅隊——state 未綁瀏覽器（R1）；撤銷權杖放網址、回呼回顯參數（R1、R6）；`formattedValue` 讀題號與 xlsx 不等價（R2）。**負責人 2026-11-17 裁**：匯入時就複製；加 cookie 綁定；契約改動批准；副本名稱、R5 套 xlsx 路徑照傾向。

背景：現行連結匯入 `server/quiz_server/sources.py:39`「`out = f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=xlsx"`」下載 xlsx 後以 openpyxl 解析；匯出 `server/quiz_server/app.py:220`「`data = write_answers(act.source_bytes, act.notes, results.winning_answers(act))`」產生 xlsx，老師手動「取代試算表」。課程補充說明判此路不符。

## R1 認證：OAuth 2.0 授權碼流程＋PKCE，網頁應用程式用戶端，cookie 綁定

- **Decision**：重新導向 URI 固定 `http://127.0.0.1:8000/api/google/callback`；`GOOGLE_CLIENT_ID`、`GOOGLE_CLIENT_SECRET` 只經環境變數（`__main__.py` 啟動時讀 repo 根目錄 `.env`，不覆蓋既有環境變數），未設定時 Google 功能停用、xlsx 備援照常。`POST /api/teacher/google/login`（需老師金鑰）產生一次性 `state`（`secrets.token_urlsafe(32)`）與 PKCE `code_verifier`（S256），有效 10 分鐘；回 `{url}` 並設 cookie `qz_gstate`＝`sha256(state)` 十六進位（`HttpOnly`、`SameSite=Lax`、`Path=/api/google`、`Max-Age=600`）。授權網址帶 `access_type=offline`、**`prompt=consent`**（Google 只在顯示同意畫面時發 refresh token）。`GET /api/google/callback` 不需老師金鑰，`state` 須為伺服器發出、未過期、未用過，且 `sha256(state)` 等於 cookie；任一不符或帶 `error` ⇒ 400 固定文案、`state` 作廢；成功回固定文案「登入完成，可關閉此分頁」並清 cookie，**不回顯任何查詢參數**。權杖只存 `GoogleSession`；過期前 60 秒換新；沒有 refresh token 或換新失敗 ⇒ 過期後 401「Google 登入已過期，請重新登入」並設未登入。email 取自 `id_token` 酬載。登出 `POST https://oauth2.googleapis.com/revoke`，**權杖放表單本體**，失敗也清空本機。權限範圍 `openid email https://www.googleapis.com/auth/spreadsheets https://www.googleapis.com/auth/drive`。
- **Rationale**：負責人裁定 OAuth 與 cookie 綁定；cookie 擋「看到投影授權網址的人用自己帳號先完成授權」的登入 CSRF；回呼不導回含老師金鑰的網址、不回顯參數，避免金鑰外洩與反射型 XSS。
- **Alternatives**：服務帳號（負責人不採）；`google-auth-oauthlib`（不採，屬取捨：沿用既有 httpx 與 `MockTransport` 替身測法、兩組程式逐字相同較易維持）。
- **證偽欄｜可證偽**：探針步驟 1「回呼 state 相符：True」「換權杖 HTTP 200；有 refresh_token：True；scope：https://www.googleapis.com/auth/drive https://www.googleapis.com/auth/spreadsheets；expires_in：3599」（探針已帶 `prompt=consent`）。另實測：帳號不在測試使用者名單時 Google 不導回回呼，故 `state` 須自帶過期。待重跑：`id_token` 含 email、refresh 換新 200、撤銷 200（T004）。

## R2 讀取：Sheets API 格狀資料 → Grid → 既有解析

- **Decision**：`GET https://sheets.googleapis.com/v4/spreadsheets/{id}?includeGridData=true&fields=properties.title,sheets(properties(title,sheetId),merges,data.rowData.values(formattedValue,effectiveValue))`（連結帶 `gid` 只取該分頁；找不到 ⇒ 400「找不到連結指定的分頁」）。儲存格值：`effectiveValue.numberValue` ⇒ 數字（整數值轉 `int`）、`stringValue` ⇒ 字串、`boolValue` ⇒ 布林，都沒有 ⇒ `formattedValue`，全無 ⇒ 空；與 openpyxl 讀 xlsx 型別一致。解析器改吃最小介面 `Grid`（`title`、`cell(row, col)`、`max_row`、`max_column`、`merges`），openpyxl 與 Sheets 各一轉接器；002 定位規則一字不改。試算表 id 解析沿用 `sources.py` 網址驗證，不再組下載網址。
- **證偽欄｜可證偽**：探針步驟 2「API 解析：[(1, ['G5', 'G6']), (2, ['G8', 'G9']), (3, ['G11']), (4, ['G13'])]」與「夾具解析」逐字相同（合併數 13）；`test_google_sheets.py` 以四份夾具轉出的格狀資料替身守住等價，含「題號 `formattedValue`＝"1.00"、`numberValue`＝1」負例。

## R3 複製與寫回：匯入時就複製，解析與寫入都對同一份副本

- **Decision**：**匯入時**①讀原試算表標題 ②Drive `POST https://www.googleapis.com/drive/v3/files/{id}/copy`，名稱「<原標題>-搶答結果」③對**副本**做 R2 讀取與解析 ④解析失敗 ⇒ 盡力刪除副本並回 400。成功 ⇒ `source_sheet_id`＝副本 id、匯入回應帶 `sheet_url`。**匯出時** `POST …/spreadsheets/{copyId}/values:batchUpdate`，`valueInputOption=RAW`，每格 `{range: "'<分頁>'!<A1>", values: [[文字]]}`，分頁名中的 `'` 以 `''` 跳脫；座標取自解析同一份副本時記下的 `Slot.cell`。只在 `ended`；回 `{url}`。原試算表只在匯入時讀標題與複製各一次。重新匯入再複製一份新副本，舊副本不刪。
- **Rationale**：負責人裁定；與 xlsx 路徑「寫回匯入快照」語意一致，原檔在匯入後被改不會讓答案錯位。
- **Alternatives**：匯出時才複製並重讀核對（不採：老師改過原檔就匯不出）；Sheets `create`＋`sheets.copyTo`（探針可行但分頁名被改、只帶單一分頁，留作日後須發布時的退路）。
- **證偽欄｜可證偽**：探針步驟 3「3A Drive files.copy：HTTP 200」「副本 … 合併與原檔相同：True」；步驟 4「副本讀回：'=1+1'」。`test_google_sheets.py`：匯入請求序「標題 → copy → 讀副本」、寫回只打副本 id、原檔 id 匯入後 0 次請求、分頁名含 `'` 的範圍跳脫。**屬取捨**：每次匯入都多一份副本；匯入後改原檔不反映（須重新匯入）；搶答期間手改副本版面仍可能錯位（殘餘風險，README 提示）；`drive` 受限範圍「測試中」實測可用。

## R4 來源與備援

- **Decision**：匯入 ①「從 Google 試算表匯入」（需登入，R2＋R3）②上傳 xlsx（不變）；刪除 `export_url`、`download_sheet`。匯出：Google 來源 ⇒「匯出到 Google 試算表」＋「下載 xlsx（備援，不含格式）」（由副本格狀資料轉成的工作簿，只含值與合併）；上傳來源 ⇒ 只有「下載 xlsx」，寫回 Google 試算表回 409。R-05「匯出至原 Guided Notes」解讀：負責人裁「先複製再寫」，副本為原 Guided Notes 的完整複本，視為達成 R-05，同批寫進 `docs/requirements.md` §4；`eval/acceptance/matrix.yaml` M-006 聲明分路徑寫。
- **證偽欄｜屬取捨**：公開連結下載正是課程補充說明點名的做法；xlsx 只當網路或授權失敗時的備援。

## R5 題組子題填空格（PR #18 followup，負責人裁定併入本卡）

- **Decision**（xlsx 與 Google 兩條路徑同一規則）：作答格不屬合併範圍、含非佔位符標籤，且同列右側相鄰格仍在**作答表頭合併範圍欄寬內**、空白且不屬合併範圍 ⇒ 右側格為填空格：`Slot.cell`＝右側格、`Slot.label=""`、`Slot.placeholder=False`、`Slot.display`＝標籤格文字；否則維持現行。欄寬取自表頭合併範圍，不寫死欄位。
- **影響**：`group.xlsx` 第 1、2 題作答格 `G5/G6/G8/G9` → `H5/H6/H8/H9`；single、variant、reference 不變（variant 子題作答格為合併範圍「H11:I11, H12:I12, H13:I13 … H17:I17, H18:I18」；紅隊以暫存腳本跑四份夾具實證）。
- **證偽欄｜可證偽**：`test_guided_notes_parse.py` 新增 group 子題座標與 display 斷言；`test_guided_notes_export.py` 斷言 `G5`「（1）」不變、`H5` 為答案。**屬取捨**：只看右側相鄰一格。

## R6 作答隔離與憑證

- **Decision**：學生、老師 view 不增 Google 欄位；狀態只經 `GET /api/teacher/google`。日誌不記授權碼、權杖、client secret、`state`；Google 錯誤 ⇒ 502，只轉 Google 錯誤 JSON 的 `error.status`（無則「Google 服務錯誤」）；httpx 例外在 `google_sheets`／`google_auth` 內攔下轉 `GoogleApiError`，不讓帶網址的例外訊息進 traceback。`ops/gate_secrets.py` 加 `GOCSPX-`、`ya29.`、`1//` 形狀，夾具「前綴＋0×n」放行。
- **證偽欄｜可證偽**：`test_isolation.py`「以假權杖完成登入、匯入、寫回、換新、登出（含撤銷失敗）後，學生 WebSocket／REST 完整 payload 與 caplog 不含權杖、授權碼、client secret」；`test_api_google.py`「回呼帶 `error=<script>` 時回應本文不含該字串」；gate-secrets 變異實錄。

## R7 契約（負責人 2026-11-17 批准）

- **Decision**：錯誤判斷先後一律 **老師金鑰 401 → 階段／來源 409 → 參數 400 → Google 登入 401 → Google 端 502**，Google 登入檢查前不發對外請求。新增 `GET /api/teacher/google`（`{configured, signed_in, email}`）、`POST /api/teacher/google/login`（`{url}`＋cookie；400「伺服器未設定 Google OAuth 用戶端」）、`GET /api/google/callback`（HTML；400「登入失敗，請回老師頁重新登入」）、`POST /api/teacher/google/logout`（`{signed_in: false}`）、`POST /api/teacher/export-sheet`（`{url}`；409「搶答結束後才能匯出」「尚未匯入題目」「題目不是從 Google 試算表匯入，請改用下載 xlsx」；401「請先以 Google 帳號登入」「Google 登入已過期，請重新登入」；502）；`POST /api/teacher/import-url` 改為需登入、匯入時複製後讀副本（`{source, count, sheet_url}`；409 非 preparing；400 連結不符／分頁不存在／解析錯誤；401；502）；`GET /api/teacher/export` 不變。
- **證偽欄｜屬取捨**：匯入端點沿用舊名，web 改動最小；先後以「先擋不需對外請求的錯」為原則。

## 已裁事項（負責人 2026-11-17）

| 事項 | 裁定 |
|---|---|
| 匯入後原檔被改的座標錯位 | 匯入時就複製（R3） |
| 登入 CSRF | 加 cookie 綁定（R1） |
| 契約改動 | 批准（R7） |
| 副本名稱 | 「<原標題>-搶答結果」，重複匯入產生多份 |
| R5 套 xlsx 上傳路徑 | 套 |
