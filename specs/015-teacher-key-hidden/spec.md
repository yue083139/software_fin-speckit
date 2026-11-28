# Feature Specification: 老師金鑰不留在網址列

**Feature Branch**: `015-teacher-key-hidden`
**Created**: 2026-11-26
**Status**: Draft（v1.1，評審藥方已落；與 OpenSpec 組 `openspec/changes/teacher-key-hidden/` 同批）
**Input**: 負責人 2026-11-26 整合驗證時：「現在金鑰會顯示在 url，可以隱藏嗎」。設計已定：老師頁載入時從 `#/teacher?key=…` 讀出金鑰 → `history.replaceState` 改成 `#/teacher` → 金鑰存本分頁 sessionStorage；重新整理從 sessionStorage 取；網址帶新 key 以網址為準；401／4401 清除並顯示既有錯誤提示；不寫 localStorage、cookie；終端機仍印完整網址。
**需求編號**：R-01、X-04｜**parity**：`docs/parity.md` §4 `teacher-key-hidden`｜**檔位**：B（老師進場流程的介面變更；不碰判定、隔離、契約、憑證）
**圖表**：`diagrams/015-teacher-key-hidden-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 開老師頁後網址不含金鑰 (Priority: P1)

老師貼上終端機印的完整網址，老師頁正常載入，網址列只剩 `#/teacher`；錄影或投影時不會露出金鑰。

**Why this priority**: Demo 影片要錄老師頁；金鑰外露等於公開老師權限。

**Independent Test**: `web/src/route.test.ts`。

**Acceptance Scenarios**:

1. **Given** 網址 `#/teacher?key=<金鑰>`，**When** 老師頁載入，**Then** 網址變 `#/teacher`、`location.href` 不含金鑰、上一頁不回到含金鑰的網址，老師頁正常運作（瀏覽器「記錄」頁與自動完成仍可能保留最初貼上的網址，屬瀏覽器行為）。
2. **Given** 已載入，**When** 同分頁重新整理，**Then** 以本分頁 sessionStorage 的金鑰照常運作。
3. **Given** 已存舊金鑰，**When** 網址帶新 key，**Then** 以網址為準並覆寫。

### User Story 2 - 金鑰錯誤時清除並提示 (Priority: P2)

**Independent Test**: `web/src/pages/teacherkey.test.tsx`。

**Acceptance Scenarios**:

1. **Given** 存的金鑰錯誤，**When** 伺服器回 401「需要老師金鑰」（或 WebSocket 4401），**Then** 清除本分頁金鑰並顯示整頁「老師金鑰錯誤」（`BadKeyNotice`，與 `teacher-key-error` 同名同文案）。
2. **Given** 金鑰正確但未登入 Google，**When** 匯出到 Google 試算表回 401「請先以 Google 帳號登入」，**Then** 金鑰保留、顯示 Google 訊息。
3. **Given** 先以錯誤金鑰開啟，**When** 同分頁貼上正確網址，**Then** 錯誤頁消失、網址不含金鑰。
4. **Given** 已在老師頁，**When** 同分頁重貼同一完整網址，**Then** 網址仍被改回 `#/teacher`。

### Edge Cases

- 關分頁後新開 `#/teacher`（無 key、無存值）⇒ 金鑰為空，伺服器回 401 ⇒ 顯示錯誤提示。
- 網址其他查詢參數保留，只移除 `key`。
- 伺服器對錯誤金鑰的 WebSocket 在交握前以 HTTP 403 拒絕（瀏覽器只見 1006）⇒ 由開頁的 REST 401 路徑顯示提示，不改伺服器。

## Requirements *(mandatory)*

- **FR-001**: 老師頁 MUST 只在網址首次帶入金鑰時讀取，讀取後 MUST 以 `history.replaceState` 自網址移除，不新增瀏覽紀錄項。
- **FR-002**: 金鑰 MUST 只存於該分頁 sessionStorage（`qz_teacher_key`），MUST NOT 寫入 localStorage 或 cookie。
- **FR-003**: 網址帶新金鑰時 MUST 以網址為準。
- **FR-004**: 只有 401「需要老師金鑰」或 4401 MUST 清除已存金鑰並顯示整頁金鑰錯誤；其他 401（Google）MUST NOT 清除。金鑰一換老師頁 MUST 重新掛載。
- **依賴**：`teacher-key-error` 在本功能之後合入（伺服器 4401 先 accept 由它做）。
- **FR-005**: 伺服器、`contracts/api.md`、終端機輸出 MUST 不變。

## Success Criteria *(mandatory)*

- **SC-001**: `npm --prefix web test` 中 `route.test.ts`、`teacherkey.test.tsx` 全綠；`git grep -n localStorage -- web/src ':!*.test.*'` 無輸出。
- **SC-002**: 人工驗證 `docs/manual-verification.md` 場次 G 全數符合。
