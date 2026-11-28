# Research: 010 team-limit-50

知識時點：2026-11-27。此卡是既有容量約束擴充，不依賴新第三方函式庫、外部服務或瀏覽器新語意；唯一需要提案期實測的倉外／效能行為是 300 條真 WebSocket 連線的本機觀測，已由 `probes/team_limit_50_capacity_probe.py` 探針完成。

## 事實基線（原樣輸出）

```text
Python 3.12.12
Version 6.0.3
```

來源依序為 `uv run --project server python --version` 與 `npm.cmd --prefix web exec -- tsc --version`。依賴名稱與鎖定版本另以 `server/pyproject.toml`、`web/package.json`、`web/package-lock.json` 為準，不在本稿重抄未實測版本。

## R1 組數邊界只改上限

- **Decision**：`MIN_TEAMS=2`、`DEFAULT_TEAMS=4` 不變，`MAX_TEAMS` 由 12 改為 50；`team_names` 仍依數字產生 `第1組`…`第50組`。1、51、非整數與格式錯誤拒絕且不改狀態。
- **Rationale**：使用者只要求提高上限；維持最小值、預設值與命名避免無關行為變更。
- **Alternatives considered**：改預設為 50（每場都產生長清單，超出需求）；自訂組名（另成資料模型與 UX 功能）；只把前端上限改 50（契約與伺服器仍拒絕）。
- **證偽欄｜可證偽**：`uv run --project server pytest -q server/tests/test_phases.py server/tests/test_api_skeleton.py`；實作期須輸出 2、12、13、50 成功與 1、51 失敗的測試計數，且把現有「13 失敗」「20 回 422」斷言訂正為新邊界。

## R2 沿用單一 Activity、鎖、序號與 view 裁切

- **Decision**：不新增容量專用狀態或分流。組數設定仍在 `Activity` 鎖內檢查階段、建立清單、撤銷所有 token／邀請碼／草稿並 bump 版本；加入、作答、順位與學生資料仍走既有方法及 `student_view`。
- **Rationale**：50 組只擴大既有集合；另建路徑會製造兩套身分、隔離與順位口徑。
- **Alternatives considered**：50 組改用另一個 endpoint 或批次狀態（契約分裂）；只撤銷被刪除的組別 token（違反既有「改組數全部重進」規則）；客戶端自行排序或裁切（可能與伺服器真實身分不一致）。
- **證偽欄｜可證偽**：`uv run --project server pytest -q server/tests/test_submit.py server/tests/test_isolation.py`；新增 50 組同題並發 20 次、每次序號無重號且恰一得主，以及每組 payload 不含其他 49 組答案的負例。

## R3 組隊組合上限為 300 台

- **Decision**：`MAX_DEVICES=6` 不變；50 組皆開組隊時支援 300 台同時加入並保持連線，第 301 台若加入已滿組別仍 409。容量驗收使用合成 token 與真 WebSocket，不使用真實學生資料。
- **Rationale**：組別上限與既有每組裝置上限必須可組合，否則同時開啟兩項已承諾功能會出現未定義缺口。
- **Alternatives considered**：只驗 50 台（無法證明組隊組合）；新增全活動裝置上限（使用者未要求且改契約）；引入訊息佇列或多處理序（本機單棧需求不支撐）。
- **證偽欄｜可證偽**：`uv run --project server python probes/team_limit_50_capacity_probe.py` 原樣輸出：

```text
環境：Windows-11-10.0.22631-SP0；Python 3.12.12
連線：300（50 組 × 6 台）
95% 收到更新：51.7 ms
最慢收到更新：51.9 ms
最終狀態一致：是（300/300）
```

探針只繞過現行 `configure_teams` 的 12 組檢查，其他 join、token 反查、view 裁切、changed 通知與 Uvicorn／WebSocket 路徑皆使用產品碼。單次輸出不代表其他電腦保證值，只證明現行架構沒有立即需要拆服務的證據。

## R4 UI 完整渲染並以捲動到達

- **Decision**：首頁組別 grid、老師組別清單與結果 table 仍完整渲染 50 組；沿用或補足水平／垂直捲動。組數 input 的 `max` 與文案改為 50。不新增搜尋、分頁、虛擬清單或自訂排序。
- **Rationale**：50 個選項仍屬本機課堂可直接瀏覽規模；保留完整清單最符合「第 50 組可在 30 秒內找到並操作」且改動最小。
- **Alternatives considered**：搜尋（增加空結果與拼字 UX）；分頁（老師難以同時掌握全部組別）；虛擬清單（測試與可及性複雜度高，50 筆無證據需要）。
- **證偽欄｜屬取捨**：選擇完整清單而非搜尋／分頁屬 UX 取捨；可驗證部分由 `npm --prefix web test -- team-limit.test.tsx` 與人工 768 px 視窗計時守住，要求 30 秒內完成第 50 組加入、釋放與結果定位。

## R5 效能只觀測，正確性阻塞

- **Decision**：300 連線時記錄測試環境、95% 更新時間與最慢值，以 2 秒為觀測目標但不阻塞；300/300 最終一致、無跨組答案及每組不超過 6 台仍阻塞。
- **Rationale**：Demo 不使用目前開發機，且未訂最低硬體規格；把單機延遲當合入門檻會造成不可重現的假紅，但正確性與隔離不應因環境放寬。
- **Alternatives considered**：固定目前開發機（Demo 不使用）；訂最低硬體（負責人未選）；完全不量測（失去容量退化訊號）。
- **證偽欄｜屬取捨**：延遲不阻塞屬明確取捨；觀測流程由 `probes/team_limit_50_capacity_probe.py` 與 `verification.md` 原樣輸出守住，最終一致與隔離另由自動測試阻塞。

## R6 凍結契約與 parity

- **Decision**：`contracts/api.md` 只改 `POST /api/teacher/teams` 的 `{count}` 範圍 2–12→2–50；成功回應、401／409／422、撤銷 token／邀請碼／草稿語意不變。`docs/product-trd.md` 與兩 repo `docs/parity.md` 同步 2–50；負責人明確批准後才改凍結件與實作。
- **Rationale**：這是既有端點的合法值集合擴大，無需新端點或欄位；契約、UI、伺服器及兩組 repo 必須使用同一口徑。
- **Alternatives considered**：新增 `/teams-large`（無必要的契約分裂）；只改實作不改契約（契約違背）；回溯改寫 `app-skeleton` 歷史規格（抹掉當時基線，改由 010 規格覆蓋較清楚）。
- **證偽欄｜可證偽**：`git grep -n "2–12\|2 到 12\|MAX_TEAMS\|max={12}" -- :/` 求出所有引用點；實作 PR 必須逐一修改或列入「有意不改」，並以 `make gate-parity SIBLING=../software_fin-openspec` 證明兩組共用檔一致。
