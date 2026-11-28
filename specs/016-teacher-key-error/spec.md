# Feature Specification: 老師金鑰錯誤時顯示提示

**Feature Branch**: `016-teacher-key-error`
**Created**: 2026-11-26
**Status**: Approved（v1.1，評審後、與 `015-teacher-key-hidden` 合流；與 OpenSpec 組 `openspec/changes/teacher-key-error/` 同批）
**Input**: `014-student-qr` verification followup——老師 WebSocket 金鑰錯誤在交握前就被拒，瀏覽器只拿到 1006，「老師金鑰錯誤」提示顯示不出來；負責人 2026-11-26 指示開小卡處理。
**需求編號**：R-01｜**parity**：`docs/parity.md` §4 `teacher-key-error`｜**檔位**：B（介面提示與 WebSocket 關閉時機）
**圖表**：`diagrams/016-teacher-key-error-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 錯金鑰開老師頁看得到原因 (Priority: P1)

老師用錯的金鑰（或網址少了 key）開老師頁，畫面整頁顯示「老師金鑰錯誤」與重開方式，不再一直停在「連線中…」。

**Why this priority**: 課堂與 Demo 中老師貼錯網址時無從得知原因。

**Independent Test**: 以 TestClient 開 `role=teacher&key=wrong` 的 WebSocket：能完成交握、第一則即為 4401 關閉；前端收到 4401 顯示提示且不重連。

**Acceptance Scenarios**:

1. **Given** 伺服器在本機執行，**When** 以錯金鑰開老師 WebSocket，**Then** 先完成交握、不收到任何訊息，關閉碼為 4401。
2. **Given** 以通道公開網址開老師 WebSocket 且金鑰錯誤，**When** 連線，**Then** 關閉碼為 4403（本機檢查優先）。
3. **Given** 老師頁收到 4401，**When** 等待 5 秒，**Then** 不再開新連線，畫面顯示「老師金鑰錯誤」。

### Edge Cases

- 錯金鑰連線關閉後，正確金鑰的老師連線照常收到推播。
- REST 401（需要老師金鑰）由 `015-teacher-key-hidden` 改為整頁 `BadKeyNotice`，本功能不再改。

## Requirements *(mandatory)*

- **FR-001**: 老師 WebSocket 金鑰錯誤 MUST 先完成交握、MUST NOT 送出任何訊息，再以 4401 關閉。
- **FR-002**: Host 不是本機時 MUST 先以 4403 關閉。
- **FR-003**: 老師頁收到 4401 MUST 不重連並整頁顯示「老師金鑰錯誤」與重開方式。

## Success Criteria *(mandatory)*

- **SC-001**: `server/tests/test_api_host.py` 新增三例全綠；改回交握前關閉時紅。
- **SC-002**: `web/src/live.test.tsx`、`web/src/pages/qr.test.tsx` 新增例全綠，web 連跑兩次。
