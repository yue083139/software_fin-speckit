# Verification: 010 team-limit-50

## 提案輪評審

**受評基線**：`3cb0448..bf8f448`

**評審日期**：2026-11-27

**輪次**：S 檔提案定稿第 1 輪（本階段唯一全卡掃）

| 通道 | 回報 | 結論 | 實跑限制 |
|---|---|---|---|
| 紅隊 | `reviews/proposal-red.dispatch.review-red.md` | `CLEARED`；未發現產品行為、作答隔離、公平判定、契約或資料衛生問題 | 評審沙箱 venv 預檢未過，評審員未把測試與門禁認作通過 |
| 架構 | `reviews/proposal-arch.dispatch.review-arch.md` | `CLEARED`；兩項取捨與契約、單一伺服器狀態來源、驗收矩陣及任務自洽 | 評審沙箱 venv 預檢未過，評審員未把測試與門禁認作通過 |

### Followup 閉環

- 架構通道指出 `plan.md` 仍稱姊妹 repo 尚未同步；已在本輪後把 Constitution Check 與 Gate 結論更新為實際狀態。
- 紅隊無藥方。
- 兩通道皆為 `CLEARED`，提案輪沒有阻斷或重要項待回驗。

### 主會話真跑證據

```text
gate-parity: 0 處不一致
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 31 個圖檔，0 處問題
gate-agents: 0 處漂移
```

## 契約批准

負責人於 2026-11-27 在對話中針對「將 `POST /api/teacher/teams` 的 `{count}` 合法範圍由 2–12 改為 2–50，其餘端點、回應形狀、錯誤語意與每組六台上限不變」明確回覆：「是」。T003 已批准，可依 TDD 順序進入契約更新與實作。

## 實作前基線

### T004：既有 2–12 組回歸

```text
................................................                         [100%]
48 passed, 1 warning in 5.91s
```

執行範圍：`server/tests/test_phases.py`、`server/tests/test_api_skeleton.py`。唯一警告為既有 Starlette `httpx` deprecation，不影響結果。

### T007：產品常數

```text
MIN_TEAMS, MAX_TEAMS, DEFAULT_TEAMS = 2, 12, 4
MAX_DEVICES = 6
```

實作前只讀確認 `server/quiz_server/activity.py` 仍維持既有上限；此步未修改產品程式。

### 有意不改

- `specs/001-app-skeleton/` 與 `specs/004-results-view/`：保留各卡當時的 12 組歷史基線，由 010 規格覆蓋現行行為，不回溯改寫歷史提案。
- `docs/parity.md` 的 `app-skeleton` 列：保留該卡交付的 2–12 摘要；下一列 `team-limit-50` 明確記錄後續擴充。

## US1：50 組設定與加入

### 紅燈

新增 `team_names(50)`、2／12／13／50 設定、API 完整清單，以及第 13／50 組加入驗收後，在產品常數仍為 12 時執行：

```text
6 failed, 75 passed, 1 warning in 7.93s
```

六個失敗全部是 13 或 50 組收到 `組數須介於 2 到 12`／HTTP 422；證明驗收能抓到本卡要修的上限缺陷。

### 綠燈

只把 `server/quiz_server/activity.py` 的 `MAX_TEAMS` 由 12 改為 50 後：

```text
81 passed, 1 warning in 7.76s
```

`server/quiz_server/app.py` 無須修改；`TeamsBody` 與端點本來就委派給 `Activity.configure_teams`。

## US2：邊界、安全、容量、隔離與公平

新增拒絕不改狀態、撤銷 tokens／codes／drafts、300 台與第 301 台、逐組隔離及 50 組並發 20 輪驗收後：

```text
122 passed, 1 warning in 16.52s
```

這批驗收在 `MAX_TEAMS=50` 後直接全綠；既有 `_revoke_all`、每組 `MAX_DEVICES=6`、`student_view` fail-closed 與鎖內伺服器序號無須修改。

### 實作後容量探針

```text
環境：Windows-11-10.0.22631-SP0；Python 3.12.12
連線：300（50 組 × 6 台）
95% 收到更新：58.4 ms
最慢收到更新：58.5 ms
最終狀態一致：是（300/300）
```

原樣輸出另存於 `probes/results/2026-11-27-team-limit-50-capacity-implementation.txt`；Phase 0 原始結果未覆寫。

### 完整 server 回歸

```text
246 passed, 1 warning in 36.30s
```

三種遊戲模式、既有 2–12 組流程與組隊模式全數通過。

## US3：50 組介面

### 紅燈

訂正測試自身的「已送出數」斷言後，50 組元件測試只剩一項預期失敗：

```text
Test Files  1 failed (1)
Tests       1 failed | 2 passed (3)
Expected max="50"；Received max="12"
```

學生選組與結果表原本就完整渲染第 50 組；真缺陷是老師組數輸入仍限制為 12。實作將該 input 與文案改為 50，並為選組、管理與結果容器補足捲動樣式；`Home.tsx` 與 `Results.tsx` 無須改動元件結構。

### 綠燈

```text
Test Files  1 passed (1)
Tests       3 passed (3)

Test Files  8 passed (8)
Tests       36 passed (36)

✓ built in 431ms
```

`team-limit.test.tsx`、完整 web 測試與 production build 均通過；第 50 組選取、老師釋放與結果定位已有元件層驗收。

## 圖碼一致性核對

| 圖表 | 圖中約束 | 程式錨點與結論 |
|---|---|---|
| component | Teacher、Home、Results 經 API 與 server 活動模型協作 | `web/src/pages/Teacher.tsx:142`「team-list」、`web/src/pages/Home.tsx:5`「TeamPicker」、`web/src/pages/Results.tsx:58`「table-wrap」、`server/quiz_server/app.py:188`「/api/teacher/teams」均存在，組件及依賴方向一致。 |
| class | `MIN_TEAMS=2`、`MAX_TEAMS=50`；設定組數委派 `Activity.configure_teams`；學生畫面只帶自身 `team` 與 `team_valid`；改組數撤銷狀態 | `server/quiz_server/activity.py:20`「MIN_TEAMS, MAX_TEAMS, DEFAULT_TEAMS = 2, 50, 4」、`server/quiz_server/activity.py:231`「configure_teams」、`server/quiz_server/views.py:73`「student_view」、`server/quiz_server/app.py:39`「TeamsBody」一致；每組裝置上限既有邏輯未改。 |
| sequence | 準備階段設定 50、建立第 1–50 組、加入第 50 組；51 拒絕且狀態不變 | `server/quiz_server/activity.py:103`「team_names」、`server/quiz_server/activity.py:184`「join」、`server/quiz_server/activity.py:232`「MIN_TEAMS <= count <= MAX_TEAMS」及 API 測試的狀態不變斷言一致。 |

架構末輪首驗發現類別圖與時序圖曾把 Activity 方法誤寫成 `set_teams`，且類別圖多畫學生端完整組別清單；已訂正為 `configure_teams`，並把學生畫面限縮為自身 `team` 與 `team_valid`。結論：訂正後三張圖的元件、類別約束與訊息順序均與實作一致。

## 人工瀏覽器驗證

- 驗證者：Codex（Computer Use），使用者於操作當下明確允許釋放第 50 組
- 日期：2026-11-27
- 環境：Windows 11、VS Code Simple Browser、本機 `make dev`、`http://127.0.0.1:8000`；老師金鑰為只供本次本機驗收的合成值
- 測試資料：`tests/fixtures/guided-notes/single.xlsx`，6 題合成 Guided Notes

| 步驟 | 實際觀察 | 耗時 |
|---|---|---:|
| 老師在準備階段將組數由 4 改為 50 | 顯示「組數（2–50）」；管理清單可捲到「第50組：未加入」 | 13 秒 |
| 學生選組清單捲到第 50 組並加入 | 進入學生頁，顯示「組別：第50組」「目前階段：準備中」 | 12 秒 |
| 老師釋放第 50 組 | 老師管理清單由「第50組：已加入」回到「第50組：未加入」 | 18 秒 |
| 第 50 組重新加入並在搶答中送出第 1 題 | 學生頁顯示「已送出：人工驗收答案」 | 10 秒 |
| 結束活動後定位結果 | 顯示「第50組 1」及「搶答成功：第50組（人工驗收答案）」 | 8 秒 |
| 將 VS Code 左側分隔線調至 webview 內容寬 768 px | 50 組總覽完整換行且可垂直捲動；第 50 組得分與第 1 題成功結果仍可見，無裁切或水平溢出阻擋操作 | 8 秒 |

每項均低於 30 秒。截圖證據為本次 Computer Use 對話中的六張可視觀察：老師端第 43–50 組清單、學生端第 41–50 組按鈕、第 50 組學生身分、送出成功、第 50 組結果，以及 768 px 結果版面。視窗最後已還原原本最大化配置。

判定：T033 通過；本卡驗收落點合流後編為 M-033，狀態為 `covered`。

## 門禁執行紀錄

第一次在沙箱內執行時，`uv` 因既有快取／`.venv` 的 Windows 權限失敗；改以可寫的暫存虛擬環境 `C:\Users\user\AppData\Local\Temp\software_fin_gate_010` 重跑，產品程式與門禁內容未變更。原樣關鍵輸出：

```text
gate-diagrams: 31 個圖檔，0 處問題
gate-parity: 0 處不一致
All checks passed!
246 passed, 1 warning in 38.74s
51 passed in 16.44s
Test Files  8 passed (8)
Tests       36 passed (36)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 31 個圖檔語法通過
gate-parity: 0 處不一致
```

唯一 warning 是既有 Starlette `httpx` deprecation。T033、T034 已補齊，故 T035 完成。

## 實作輪評審與藥方回驗

| 通道 | 首驗 | 藥方與回驗 | 最終結論 |
|---|---|---|---|
| 紅隊 | 發現 `TeamsBody.count` 使用非嚴格整數，`"50"` 與 `50.0` 可能被自動轉型，造成格式錯誤驗收假綠 | 改用 `StrictInt`，補兩種格式皆回 422 且活動狀態完全不變的負例；定點測試 `35 passed, 1 warning`；同通道回驗 | `CLEARED` |
| 架構 | 發現類別圖與時序圖把 `Activity.configure_teams` 誤寫為不存在的 `set_teams`，且類別圖誤畫學生端完整組別清單 | 訂正兩張 PlantUML 與 PNG，學生畫面限縮為自身 `team`、`team_valid`，同步訂正圖碼核對表；`gate-diagrams: 31 個圖檔，0 處問題`；同通道回驗 | `CLEARED` |

架構通道另列非阻塞 followup：`diagrams/010-team-limit-50-component.puml` 可更精確畫出前端經 API／WebSocket 到 `app.py`，再由 `view_for` 產生畫面的實際資料路徑。此項不改產品行為，不在末輪追加修稿；主人為 @yue083139，另立卡處理，且本卡開 PR 時須寫入首屏 followup。

## 最終門禁重跑

兩項藥方落地後重新執行完整 `make gate`：

```text
All checks passed!
248 passed, 1 warning in 27.68s
51 passed in 16.60s
Test Files  8 passed (8)
Tests       36 passed (36)
gate-zh-hant: 0 處簡體字
gate-secrets: 0 findings
gate-speckit: 憲章 v1.0.0，0 處問題
gate-diagrams: 31 個圖檔，0 處問題
gate-agents: 0 處漂移
gate-diagrams-syntax: 31 個圖檔語法通過
gate-parity: 0 處不一致
```

## 都綠否

| S 檔必要項目 | 狀態 | 證據 |
|---|---|---|
| 提案輪紅隊 | 綠 | `proposal-red.dispatch.review-red.md`：`CLEARED` |
| 提案輪架構 | 綠 | `proposal-arch.dispatch.review-arch.md`：`CLEARED` |
| 實作輪紅隊 | 綠 | 首驗藥方已落地，同通道回驗 `implementation-red.dispatch.review-red.md`：`CLEARED` |
| 實作輪架構 | 綠 | 首驗藥方已落地，同通道回驗 `implementation-arch.dispatch.review-arch.md`：`CLEARED` |
| 先寫驗收再實作 | 綠 | 邊界、狀態不變、容量、隔離、公平及 UI 紅燈／綠燈證據已記錄 |
| 人工驗證 | 綠 | 第 50 組加入、釋放、作答、結果與 768 px 操作各步均低於 30 秒 |
| 完整 `make gate` | 綠 | server 248、ops 51、web 36；其餘門禁全部 0 問題 |
| parity | 綠 | `gate-parity: 0 處不一致` |
| 圖碼一致性 | 綠 | 藥方訂正後架構回驗 `CLEARED`，31 張圖語法與配對門禁通過 |

都綠

