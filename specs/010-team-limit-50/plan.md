# Implementation Plan: 組別上限提高至 50 組

**Branch**: `010-team-limit-50` | **Date**: 2026-11-27 | **Spec**: [spec.md](spec.md)
**Input**: `specs/010-team-limit-50/spec.md` v1.0
**藍圖**：`diagrams/010-team-limit-50-{component,class,sequence}.puml`

## Summary

1. **只把組別合法上限由 12 提高為 50，最小值 2 與預設值 4 不變**／代價：狀態內容與畫面節點增多／可被 1、2、12、13、50、51 的邊界測試證偽（research R1）。
2. **沿用既有組別身分、鎖、伺服器序號與依身分裁切的 view，不另建容量專用路徑**／代價：每次狀態變更仍由各連線重算 view／可被 50 組並發順位與跨組答案隔離測試證偽（R2）。
3. **組隊模式維持每組 6 台，組合上限為 300 條學生連線**／代價：單機更新工作量隨連線數線性增加／可被 300 連線真棧探針與容量驗收證偽（R3）。
4. **50 組清單與結果沿用完整渲染及捲動，不新增搜尋或分頁**／代價：頁面較長、結果表較寬／可被 768 px 視窗於 30 秒內操作第 50 組的人工與前端測試證偽（R4）。
5. **2 秒只作具環境紀錄的效能觀測目標；最終一致、隔離與容量正確性才阻塞**／代價：慢機器不因單一延遲數字擋合入／可被探針輸出的 p95、最慢值與 300/300 一致計數證偽（R5）。

**契約批准點**：`contracts/api.md` 的 `POST /api/teacher/teams` 本體範圍須由 2–12 改為 2–50，屬凍結契約語意變更；提案輪後須由負責人明確批准才可實作（research R6、[contracts/api-change.md](contracts/api-change.md)）。

**矩陣落點**：`eval/acceptance/matrix.yaml` 新增 M-020～M-022（組數邊界與撤銷、300 台容量與隔離、50 組 UI 可操作性）。

## Technical Context

**Language/Version**: Python 3.12（實測 3.12.12）、TypeScript 6.0.3
**Primary Dependencies**: FastAPI、Uvicorn、websockets、React、Vite；不新增相依套件
**Storage**: 既有單一處理序記憶體 `Activity`；不新增資料庫、快取或快照格式
**Testing**: pytest、Vitest、Testing Library；真 Uvicorn＋websockets 容量探針；人工瀏覽器驗證
**Target Platform**: 本機單一伺服器與同機瀏覽器模擬；Windows／Linux／macOS 開發環境
**Project Type**: FastAPI WebSocket 後端＋React 單頁前端
**Performance Goals**: 300 條學生連線皆最終收到一致狀態；記錄 95% 與最慢更新時間，以 2 秒為非阻塞觀測目標
**Constraints**: 作答隔離 fail-closed；順位只依伺服器接收序；合法改組數撤銷所有憑證、邀請碼與草稿；每組仍最多 6 台；不新增搜尋、分頁、資料庫或對外部署
**Scale/Scope**: 單一活動 2–50 組、組隊時最多 50×6＝300 台學生裝置；老師連線不計入學生裝置上限

## Constitution Check

### Phase 0 前

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | 對應 R-01、R-11；`docs/parity.md` 已登記 `team-limit-50`；OpenSpec 同名卡與共用檔同步列為送審前阻塞項 | ⚠️ 本 repo 已登記；姊妹 repo 尚待同步，未完成前不得送審 |
| II 作答隔離 | 仍只經 `student_view`；新增 50 組／300 台下每組 payload 不含其他 49 組答案的傳輸負例 | ✅ |
| III 順位以伺服器為準 | 不改鎖與序號；新增 50 組同題並發 20 次的唯一順位與恰一得主測試 | ✅ |
| IV Guided Notes 動態定位 | 不讀寫 Guided Notes 結構或作答格 | ✅ |
| V 測試先行與人工驗證 | 先新增邊界、隔離、並發與 UI 驗收；實作後寫 `verification.md` 與圖碼核對 | ✅ |
| VI 簡單與本機優先 | 只改常數、契約、文案與必要 UI；不增資料庫、佇列、搜尋或分頁 | ✅ |
| VII 圖表優先 | 010 三張 PlantUML 與 PNG 已先產生；plan 以其組件、類別、訊息序為藍圖 | ✅ |
| VIII 繁體中文與資料衛生 | 文件與 UI 使用繁體中文；探針只用合成組名與假憑證，不輸出 token 或答案 | ✅ |

**Gate 結論**：設計本身無憲章違反；parity 同步是流程阻塞項，不影響 Phase 0／1 設計產物，但未完成前不得派提案評審或呈批。

### Phase 1 後重檢

- `research.md` R1～R6 已把容量、隔離、UI、效能觀測與契約批准點寫死，無 `NEEDS CLARIFICATION`。
- `data-model.md` 不新增實體或持久化，只調整 `MAX_TEAMS` 約束並保留所有生命週期規則。
- `contracts/api-change.md` 只提案修改既有組數範圍與錯誤邊界；負責人批准前不改凍結件。
- `quickstart.md` 覆蓋邊界、撤銷、300 台探針、隔離、並發、UI 與全量門禁。
- parity 姊妹 repo 同步仍為唯一未綠流程項；完成後本節可全數轉為 ✅。

## Project Structure

### Documentation (this feature)

```text
specs/010-team-limit-50/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-change.md
├── checklists/
│   └── requirements.md
└── tasks.md                  # 下一階段由 $speckit-tasks 產生

diagrams/
├── 010-team-limit-50-component.puml/.png
├── 010-team-limit-50-class.puml/.png
└── 010-team-limit-50-sequence.puml/.png
```

### Source Code (repository root)

```text
server/
├── quiz_server/
│   ├── activity.py           # MAX_TEAMS：12 → 50；既有 configure_teams／join／鎖不改語意
│   ├── app.py                # 端點結構不變；沿用 TeamsBody 與錯誤轉換
│   └── views.py              # 不改裁切規則；50 組／300 台隔離回歸
└── tests/
    ├── test_api_skeleton.py  # 2、12、13、50、51；撤銷與階段錯誤
    ├── test_phases.py        # Activity 邊界與改組數生命週期
    ├── test_team_mode.py     # 50×6 加入與第 301 台拒絕
    ├── test_submit.py        # 50 組並發順位
    └── test_isolation.py     # 50 組／300 台傳輸隔離

web/src/
├── pages/
│   ├── Home.tsx              # 完整 1–50 組選擇與捲動
│   ├── Teacher.tsx           # 組數 2–50 文案與 input 上限
│   ├── Results.tsx           # 50 組結果的既有橫向捲動回歸
│   └── team-limit.test.tsx   # 50 組與第 50 組操作驗收（新）
└── styles.css                # 只在既有 grid/table 捲動不足時做最小調整

contracts/api.md              # 批准後把 teams count 2–12 改為 2–50
docs/product-trd.md           # 使用者可設組數口徑 2–50
eval/acceptance/matrix.yaml   # M-020～M-022
probes/team_limit_50_capacity_probe.py
probes/results/2026-11-27-team-limit-50-capacity.txt
```

**Structure Decision**: 沿用既有 server／web 雙元件結構；不新增服務、資料層或共用套件。功能修改集中在組數約束、契約／文件口徑、邊界與規模驗收，以及必要的既有 UI 捲動修正。

## Complexity Tracking

無架構複雜度違反。parity 尚未同步是流程阻塞，不以複雜設計合理化；送審前必須補齊姊妹 repo 同名卡與共用檔。
