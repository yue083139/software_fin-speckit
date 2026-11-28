# Verification: 021-csv-export

## 自動驗證結果

- OpenSpec web 全套：19 files、110 tests passed；lint、typecheck 通過。
- SpecKit web 全套：19 files、111 tests passed；lint、typecheck 通過。
- 兩組 CSV 與老師頁針對測試：各 6 tests passed。
- `make gate-diagrams`：67 個圖檔，0 處問題。
- `make gate-diagrams-syntax`：67 個圖檔語法通過。
- `make gate-speckit`：憲章 v1.0.0，0 處問題。
- SpecKit `make gate-pr`：通過；伺服器 388 tests、ops 58 tests、web 111 tests 皆通過，所有文件與圖表門禁通過。
- `make gate-parity SIBLING=../software_fin-openspec`：0 處不一致。

## 圖表一致性核對

| 圖元素 | 程式 |
|---|---|
| Teacher 工作檯只在 ended 提供下載 | `web/src/pages/Teacher.tsx` `PhaseControls` |
| 匯出 helper 使用 TeacherView、題目 × 組別展開 | `web/src/resultsCsv.ts` `buildResultsCsv` |
| Blob 與來源檔名下載 | `web/src/resultsCsv.ts` `downloadResultsCsv` |

## 人工驗證

2026-11-28 使用者回報 `docs/manual-verification.md` 場次 L 全部步驟通過；驗收 repo／commit 尚未提供。
