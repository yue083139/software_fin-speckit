# Tasks: 匯出完整活動結果 CSV

**Input**: `specs/021-csv-export/` 與 `diagrams/021-csv-export-*.puml`

## Phase 0: 前置

- [x] T000 三張圖 `make diagrams`、`make gate-diagrams` 綠。
- [x] T001 `docs/parity.md` §4 登記、§5 記變更；更新 M-034 與人工驗證場次 L。

## Phase 1: User Story 1 (P1)

- [x] T010 [US1] 測試先行：`web/src/resultsCsv.test.ts` 驗證列數、欄位、未作答、題組標籤、CSV 跳脫、公式答案與檔名。
- [x] T011 [US1] 新增 CSV 建構與下載 helper，資料使用伺服器 teacher view。
- [x] T012 [US1] 老師活動控制區新增結束後可用的「下載完整結果 CSV」按鈕。
- [x] T013 [US1] OpenSpec 組同步相同行為與驗收；確認共用文件與 web 程式一致。

## Phase 2: 驗證

- [x] T020 `npm --prefix web test`、`run lint`、`run typecheck` 通過。
- [x] T021 `make gate-pr`、`make gate-parity SIBLING=../software_fin-openspec` 通過。
- [x] T022 圖表一致性核對並記錄 `verification.md`。
- [x] T023 人工驗證場次 L；使用者回報通過，repo／commit 待補。
