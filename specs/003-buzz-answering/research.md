# Research: 003 buzz-answering

知識時點：2026-11-11。對標：實體搶答器以主持端收到訊號的先後裁定；Kahoot! 以伺服器量測作答時間（`docs/research/competitors.md`）。

## R1 送出流程與順位

- **Decision**：以憑證反查組別（403）→ 鎖內依序檢查階段（409）、題號（404）、未送出過（409）、答案（422）→ 讀 `next_seq` → 讓出點 → 寫回序號並記錄。
- **Rationale**：讓出點若放在配號之前，拿掉鎖時配號仍是原子操作，變異實錄會假綠（OpenSpec 組提案輪回驗實證）。
- **證偽欄｜可證偽**：`test_concurrent_same_question`、`test_concurrent_same_team_same_question`；變異實錄見 `verification.md`。

## R2 答案驗證

- **Decision**：去頭尾空白後非空、≤ 200 字、不含 Unicode `Cc` 類別字元。
- **Rationale**：openpyxl 寫入控制字元會拋 `IllegalCharacterError`，整場匯出失敗（OpenSpec 組提案輪紅隊以 openpyxl 3.1.5 實證）。
- **證偽欄｜可證偽**：`test_invalid_answers_are_422`。

## R3 判定規則策略

- **Decision**：`ScoringRule.rank(submissions, judgments=None, attrs=None)`、`team_scores(teams, ranked)`；`ClassicBuzzRule` 依 `seq` 排名、得主 1 分。
- **Rationale**：`docs/trd-game-modes.md` T-02 預留，第二期模式只新增規則類別。
- **證偽欄｜可證偽**：`test_scoring.py`（含預留輸入不影響經典結果）。

## R4 作答隔離

- **Decision**：`student_view` 非 `ended` 只含本組 `my_submissions`（題號＋答案）；`ended` 才加 `results`；送出成功回應只回本組這筆；`RequestValidationError` 回固定文字；日誌只記組別、題號、序號。
- **Rationale**：FastAPI 預設 422 會把請求本體放進回應；推播時機會洩漏他組活動。
- **證偽欄｜可證偽**：`test_websocket_and_rest_do_not_leak`、`test_other_team_submit_sends_nothing`、`test_spoofed_team_param`、`test_non_ended_phases_isolated`、`test_logs_do_not_contain_answers`。
