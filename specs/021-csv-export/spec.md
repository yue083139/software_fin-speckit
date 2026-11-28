# Feature Specification: 匯出完整活動結果 CSV

- **Feature Branch**: `021-csv-export`
- **Created**: 2026-11-28
- **Status**: Implementing
- **需求編號**：X-02｜**parity**：`docs/parity.md` §4 `csv-export`｜**檔位**：B（只改 web，不改 API）
- **圖表**：`diagrams/021-csv-export-{component,class,sequence}.puml`

## User Scenarios & Testing

### User Story 1 - 老師下載完整活動結果 (Priority: P1)

活動結束後，老師可下載 CSV，完整保留每題每組的答案與結果；未作答的組別亦須列出。

**Independent Test**: 使用含兩題、兩組、有作答與未作答的假 `TeacherView` 產生 CSV，逐列核對欄位與伺服器結果。

**Acceptance Scenarios**:

1. **Given** 活動已結束，**When** 老師下載 CSV，**Then** 每題 × 每組皆有一列，答案、順位、得主、判定和分數與結果表一致。
2. **Given** 某組未送出某題，**When** 老師匯出，**Then** 該題組合仍有一列，答案與順位空白且本題得分為 0。
3. **Given** 活動尚未結束，**When** 老師查看活動控制，**Then** CSV 下載按鈕不可用。

### Edge Cases

- 題組答案在同一儲存格保留子題標籤。
- 答案含逗號、雙引號、換行時保持欄位完整。
- 答案以 `=`, `+`, `-`, `@`（前可有空白）開頭時以文字匯出。
- 來源名稱含檔名非法字元時清理檔名。

## Requirements

- **FR-001**: CSV MUST 僅能在活動結束後下載。
- **FR-002**: CSV MUST 依序包含題號、組別、答案、順位、是否得主、判定結果、本題得分、活動總分；每題每組恰一列。
- **FR-003**: 未作答列 MUST 保留，答案與順位空白、本題得分為 0。
- **FR-004**: 結果欄 MUST 使用伺服器 view 既有值，不得於前端重算順位、得主或得分。
- **FR-005**: CSV MUST 使用 UTF-8 BOM、CRLF 及標準 CSV 引號跳脫；題組答案須含標籤，公式前綴答案須以文字輸出。
- **FR-006**: 檔名 MUST 為來源名稱去副檔名後加 `_活動結果.csv`。

## Success Criteria

- **SC-001**: CSV 測試覆蓋完整列數、未作答列、結果欄、題組、跳脫、公式安全及檔名。
- **SC-002**: OpenSpec／SpecKit web 測試、lint、typecheck 通過，兩組共用文件與程式相符。
- **SC-003**: 人工驗證手冊場次 L 通過。
