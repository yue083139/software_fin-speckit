# Implementation Plan: Guided Notes 直接串接雲端 Google Sheets 讀寫

**Branch**: `010-guided-notes-sheets-sync` | **Date**: 2026-11-17 | **Spec**: [spec.md](spec.md)
**藍圖**：`diagrams/010-guided-notes-sheets-sync-{component,class,sequence}.puml`

## Summary

1. **老師以 Google 帳號 OAuth 登入，伺服器直接以 Sheets API 讀寫**：授權碼＋PKCE、權杖只放伺服器記憶體／代價：須建 OAuth 用戶端、「測試中」只放行登記帳號／可被探針四步任一失敗證偽（已實測全 OK，research R1）。
2. **讀取：Sheets 值＋合併範圍轉成 Grid，沿用 002 定位規則**／代價：只取值與合併，不取格式／可被「API 讀到的題目與作答格與 xlsx 夾具不同」證偽（探針步驟 2 相同，R2）。
3. **寫回：Drive `files.copy` 複製整份，再以 `RAW` 寫入副本，原檔不動**／代價：老師雲端多一份檔、需 `drive` 受限範圍／可被「副本合併不同、=1+1 變公式、原檔被寫」證偽（探針步驟 3、4，R3）。
4. **保留上傳／下載 xlsx 當備援，移除公開連結下載**／屬取捨（R4）。
5. **題組子題答案寫入標籤右側、仍在作答表頭欄寬內的空白格**（PR #18 followup）／代價：`group.xlsx` 答案從 G 欄移到 H 欄／可被三份夾具往返測試證偽（R5）。

**矩陣落點**：M-003（R-02）、M-006（R-05）聲明補「直接讀寫雲端 Google Sheets」、守門加 `server/tests/test_google_sheets.py`、`server/tests/test_api_google.py`；新增一行「Google 權杖永不送往學生端、永不寫入日誌」，守門 `server/tests/test_isolation.py`。

**merge 三問第三問**：2026-11-17 課程公告明訂須直接串接雲端 Google Sheets 讀寫；現行 xlsx 往返不符，不改即 R-02、R-05 不達標。期限 2026-11-30。

## Technical Context

**Language/Version**: Python 3.12、TypeScript
**Primary Dependencies**: 無新增（httpx 既有）
**Storage**: 記憶體 `GoogleSession`（權杖、`state` 表）、`Activity.source_sheet_id`
**Testing**: pytest（Google 端點以 `httpx.MockTransport` 替身，不連網）、vitest；真棧以探針與人工驗證
**Constraints**: `contracts/api.md` 改動須負責人批准（R7）；OpenSpec 組同批，server／web 程式逐字相同

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | R-02、R-05 依課程補充說明；parity §4 `guided-notes-sheets-sync`；OpenSpec 組同批 change | ✅ |
| II 作答隔離 | 學生 view 不含 Google 欄位；新增權杖不外洩負例 | ✅ |
| III 順位以伺服器為準 | 不涉判定 | ✅ |
| IV Guided Notes 動態定位 | Grid 沿用表頭與合併定位；R5 以表頭合併欄寬判斷，不寫死欄位；三份夾具 | ✅ |
| V 測試先行與人工驗證 | 驗收測試先寫；人工驗證場次 A2、A5 改寫重驗 | ✅ |
| VI 簡單與本機優先 | 單一老師、權杖不落地、不用服務帳號與 SDK | ✅ |
| VII 圖表優先 | 三張圖先行 | ✅ |
| VIII 繁體中文與資料衛生 | 權杖不入日誌；gate-secrets 加三種形狀 | ✅ |

## Project Structure

### Source Code (repository root)

```text
server/quiz_server/google_auth.py（新）   # GoogleSession：PKCE、state、換權杖、換新、撤銷
server/quiz_server/google_sheets.py（新） # read_grid、SheetsGrid、copy_and_write
server/quiz_server/guided_notes.py        # Grid、OpenpyxlGrid、parse_grids、R5 子題填空格
server/quiz_server/sources.py             # 刪 export_url、download_sheet；保留 check_upload、sheet_id 解析
server/quiz_server/activity.py            # source_sheet_id、load_notes
server/quiz_server/app.py                 # R7 端點
server/quiz_server/__main__.py            # 讀 .env
server/tests/test_google_sheets.py（新）、test_api_google.py（新）、test_isolation.py（增）、
  test_guided_notes_parse.py／test_guided_notes_export.py（改 group 座標）、test_api_import.py（刪公開下載）
web/src/pages/ImportPanel.tsx、Teacher.tsx、GooglePanel.tsx（新）、google.test.tsx（新）
web/src/api.ts、types.ts
ops/gate_secrets.py、ops/tests
contracts/api.md、docs/requirements.md §4、docs/product-trd.md、README.md、.env.example、docs/manual-verification.md
```

## Complexity Tracking

無違反憲章之處。
