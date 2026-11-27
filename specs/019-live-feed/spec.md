# Feature Specification: 搶答中老師頁即時搶答快訊

**Feature Branch**: `019-live-feed`
**Created**: 2026-11-27
**Status**: Approved（v1.1，評審 CLEARED、已合入 `dev` SpecKit #42；與 OpenSpec 組 `openspec/changes/archive/2026-11-27-live-feed/` 同批）
**Input**: 負責人 2026-11-27 授權成員自行開卡、兩組同步；成員提議「搶答中老師頁右上角跳出『第2組 搶下第 3 題！』」。
**需求編號**：R-04、X-04｜**parity**：`docs/parity.md` §4 `live-feed`｜**檔位**：B（只改 web 老師頁）
**圖表**：`diagrams/019-live-feed-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師即時看到誰搶下題目 (Priority: P1)

搶答中有組別送出時，老師頁右上角跳出快訊「第2組 搶下第 3 題！」或「第1組 送出第 3 題」，3 秒後自動消失；老師投影時全班一起感受搶答節奏。

**Why this priority**: 新送出原本只是作答狀況表多一格，投影時不易察覺。

**Independent Test**: 以假老師 view 渲染 `useLiveFeed`，換成多一筆送出的 view，右上角出現對應快訊；第一個 view 不出快訊。

**Acceptance Scenarios**:

1. **Given** 經典搶答中，**When** 第2組第一個送出第 3 題，**Then** 老師頁跳出「第2組 搶下第 3 題！」。
2. **Given** 第2組已送出第 3 題，**When** 第1組也送出第 3 題，**Then** 跳出「第1組 送出第 3 題」。
3. **Given** 只計對錯模式，**When** 第1組第一個送出第 2 題，**Then** 跳出「第1組 送出第 2 題」（不說搶下）。
4. **Given** 搶答中已有送出，**When** 老師重新整理老師頁，**Then** 已有的送出不再跳出快訊。
5. **Given** 老師頁斷線期間有組別送出，**When** 重新連上，**Then** 斷線期間的送出不補跳，之後的新送出照常跳出。

### Edge Cases

- 結束後老師按答對／答錯、重置活動：不跳快訊（只在搶答中）。
- 同時大量送出：最多疊 4 則，舊的先收；作答狀況表仍完整。
- 學生頁：沒有快訊（學生搶答中本來就看不到他組送出）。

## Requirements *(mandatory)*

- **FR-001**: 搶答中有新送出時，老師畫面 MUST 跳出快訊；經典搶答第 1 順位 MUST 說「搶下」，其餘 MUST 說「送出」。
- **FR-002**: 老師頁開啟、重新整理或斷線重連後收到的第一個新畫面 MUST NOT 跳出快訊，斷線期間的送出 MUST NOT 補跳；非搶答中 MUST NOT 跳出快訊。
- **FR-003**: 快訊 MUST NOT 含答案內容。
- **FR-004**: 學生畫面 MUST NOT 有快訊；MUST NOT 新增伺服器欄位或改變送往學生端的資料。

## Success Criteria *(mandatory)*

- **SC-001**: `web/src/pages/livefeed.test.tsx` 9 例全綠，web 連跑兩次；拿掉基準判斷、階段判斷、經典判斷、斷線清基準、`stale` 判斷時各自轉紅。
- **SC-002**: 伺服器、`contracts/` 無變更（`git diff origin/dev -- server contracts` 為空）。
