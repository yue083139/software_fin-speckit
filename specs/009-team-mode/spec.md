# Feature Specification: 組隊模式——一組多台裝置、代表作答

**Feature Branch**: `009-team-mode`
**Created**: 2026-11-14
**Status**: Draft（v1.0）
**Input**: User description: "第三期做組隊模式"（負責人 2026-11-14）；TRD §6 裁定「代表作答：組內任一人送出即代表全組，其餘組員看得到組內草稿；不採分數平均」（2026-11-12）
**需求編號**：X-04（`docs/trd-game-modes.md` M4）｜**parity**：`docs/parity.md` §4 `team-mode`｜**檔位**：S（作答隔離：新增送往學生端的草稿通道；`contracts/` 增端點與欄位；組別憑證口徑改變）
**圖表**：`diagrams/009-team-mode-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 老師開啟組隊，組員以邀請碼加入同一組 (Priority: P1)

準備階段老師勾選「組隊（一組多台裝置）」。每組第一位組員選組後，畫面顯示 6 碼邀請碼；其他組員在首頁選同一組並輸入邀請碼才能加入。每組最多 6 台。

**Why this priority**: 沒有邀請碼，任何人選一個已有人的組別就能讀到該組草稿與送出——第一期「一組一台」擋掉的冒用會重新打開。

**Independent Test**: 開組隊 → 第1組 A 裝置加入、看到邀請碼 → B 裝置不帶碼加入被拒 403 → 帶碼加入成功 → 老師畫面第1組 2 台。

**Acceptance Scenarios**:

1. **Given** 準備階段，**When** 老師開啟組隊，**Then** 所有已加入裝置失效，老師與公開資訊的 `team_play` 為 true。
2. **Given** 組隊、第1組已有一台，**When** 另一台不帶或帶錯邀請碼選第1組，**Then** 回 403「邀請碼不正確」，台數不變。
3. **Given** 同上，**When** 帶正確邀請碼（大小寫不拘、可有前後空白），**Then** 取得第1組憑證。
4. **Given** 第1組已有 6 台，**When** 第 7 台帶正確碼加入，**Then** 回 409「此組裝置已滿（最多 6 台）」；並發加入不超過 6 台。
5. **Given** 搶答中，**When** 老師切換組隊，**Then** 回 409。
6. **Given** 組隊、第1組 3 台，**When** 老師釋放第1組，**Then** 3 台全部失效，舊邀請碼不能再用。

---

### User Story 2 - 組內任一人送出即代表全組 (Priority: P1)

同組任一台送出某題就算該組送出；其他組員的畫面立即顯示「已送出」。同組多台同時送出同一題只有一筆成功。

**Independent Test**: 第1組三台並發送出第 3 題 → 恰一筆 200、其餘 409。

**Acceptance Scenarios**:

1. **Given** 搶答中，**When** 第1組三台同時送出第 3 題，**Then** 恰一筆成功，其餘回 409「本組已送出這一題，不可修改」。
2. **Given** A 裝置送出第 3 題，**When** B 裝置看畫面，**Then** 第 3 題顯示已送出及答案。

---

### User Story 3 - 組員看得到組內草稿 (Priority: P2)

搶答中組員輸入答案時，同組其他裝置看到「組內草稿」，可按「套用」帶入自己的輸入欄。草稿只給本組看，不計分、不匯出。

**Independent Test**: A 裝置打字 → B 裝置看到草稿；第2組的連線收不到任何訊息。

**Acceptance Scenarios**:

1. **Given** 組隊搶答中，**When** 第1組 A 裝置把第 3 題草稿改為「草稿一」，**Then** 第1組 B 裝置收到含「草稿一」的狀態。
2. **Given** 同上，**When** 第1組更新草稿，**Then** 第2組的連線收不到任何訊息，所有內容不含第1組草稿。
3. **Given** 組隊關閉，**When** 學生送草稿，**Then** 回 409。
4. **Given** 第1組已送出第 3 題，**When** 再送第 3 題草稿，**Then** 回 409。
5. **Given** 時間計分模式，**When** 送非開放中題目的草稿，**Then** 回 409「這一題目前沒有開放作答」。

### Edge Cases

- 組隊是活動設定，可與經典搶答、只計對錯、時間計分任一模式搭配，不改任何計分與揭曉規則。
- 開關值不變時不撤銷憑證；改組數照舊撤銷所有憑證並清除邀請碼。
- 判定中與已結束的學生畫面不帶草稿；老師畫面永遠不帶草稿。
- 公開資訊只多 `team_play`，不含台數與邀請碼。
- 草稿可空白（組員清掉）；格式錯誤回 422 且訊息不回顯內容。

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: 老師 MUST 能在 `preparing` 開關組隊（`POST /api/teacher/team-play {enabled}`）；其他階段 409；值改變時撤銷所有憑證與邀請碼；重置保留。
- **FR-002**: 組隊時同組第二台起 MUST 帶相符邀請碼（403），每組最多 6 台（409）；邀請碼 6 碼、只出現在本組學生畫面與老師畫面。
- **FR-003**: 釋放 MUST 撤銷該組全部憑證並作廢邀請碼。
- **FR-004**: 送出規則 MUST 與 003 相同；同組並發送出同一題 MUST 恰一筆成功。
- **FR-005**: `POST /api/student/draft {question, answers}` MUST 只在組隊、`answering`、本組未送出該題（時間計分另限開放中那一題）時接受；草稿 MUST 只出現在本組 `answering` 階段的學生畫面。
- **FR-006**: 草稿 MUST 在該題送出、重置、重新匯入、釋放、切換組隊時清除；MUST NOT 計分或匯出。
- **FR-007**: 組隊關閉時所有行為 MUST 與 001–008 相同；`contracts/api.md` 只增不改。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 沒有正確邀請碼加入已有裝置的組別一律 403 且不發憑證（`test_join_requires_code`）。
- **SC-002**: 同組 3 台並發送出同一題 20 次，每次恰 1 筆成功、序號無重號（`test_concurrent_submit_same_team`）。
- **SC-003**: 他組草稿與邀請碼不出現在本組任何 payload，他組草稿更新不觸發本組推播（`test_isolation.py` 組隊負例）。
- **SC-004**: 三種模式下組隊開與關的計分結果相同（`test_team_play_does_not_change_scoring`）；001–008 全部測試照舊綠。
