# Feature Specification: 揭曉領獎台時灑彩帶

**Feature Branch**: `020-podium-confetti`
**Created**: 2026-11-27
**Status**: Draft（v1.0；與 OpenSpec 組 `openspec/changes/podium-confetti/` 同批）
**Input**: 負責人 2026-11-27 授權成員自行開卡、兩組同步；成員提議「揭曉領獎台時灑彩帶動畫」。
**需求編號**：R-04、R-08、X-04｜**parity**：`docs/parity.md` §4 `podium-confetti`｜**檔位**：B（只改 web 畫面）
**圖表**：`diagrams/020-podium-confetti-{component,class,sequence}.puml`

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 揭曉時有慶祝感 (Priority: P1)

活動結束、領獎台出現時，從領獎台卡片上方灑下彩色彩帶，約 3 秒內落下淡出；老師頁與學生結果頁都有。

**Why this priority**: 領獎台是揭曉的高潮，靜態畫面缺少慶祝感，Demo 收尾也較平淡。

**Independent Test**: 渲染 `Podium`（有組別得分），卡片內有 36 片彩帶且 `aria-hidden`；以新分數重繪後仍是同一批元素。

**Acceptance Scenarios**:

1. **Given** 活動結束且有組別得分，**When** 領獎台出現，**Then** 卡片內灑一次彩帶，且不擋住按鈕。
2. **Given** 經典搶答結束、領獎台已出現，**When** 老師按「答錯」使名次改變，**Then** 領獎台更新但不再灑彩帶。
3. **Given** 所有組別 0 分，**When** 活動結束，**Then** 沒有領獎台也沒有彩帶。

### Edge Cases

- 重新整理頁面：領獎台重新出現，再灑一次。
- 系統設定減少動態效果：領獎台照常顯示、沒有彩帶。

## Requirements *(mandatory)*

- **FR-001**: 領獎台出現時 MUST 在卡片內灑一次彩帶；MUST NOT 擋住點擊；MUST 對讀屏軟體隱藏。
- **FR-002**: 同一個領獎台因分數更新重繪時 MUST NOT 重播彩帶。
- **FR-003**: 彩帶顏色 MUST 只使用 `--qz-*` 主題變量。
- **FR-004**: 沒有領獎台時 MUST NOT 有彩帶；減少動態效果時 MUST NOT 顯示彩帶。
- **FR-005**: MUST NOT 新增 npm 依賴、伺服器欄位或改變送往學生端的資料。

## Success Criteria *(mandatory)*

- **SC-001**: `web/src/pages/podium.test.tsx`「領獎台彩帶」4 例全綠，web 連跑兩次；拿掉彩帶、每次重繪換新元素、改用色值常量時各自轉紅。
- **SC-002**: `server/`、`contracts/`、`web/package.json` 無變更。
