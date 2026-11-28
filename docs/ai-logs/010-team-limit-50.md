# AI 對話紀錄：010-team-limit-50

- 日期：2026-11-27
- 工具：Codex
- 卡名：`team-limit-50`
- 分支：`010-team-limit-50`
- 檔位：S

## 使用者目標與裁定

使用者要求把課堂搶答系統的組別上限提高到 50 組，建立 `010-team-limit-50` 規格與分支，依序完成 specify、clarify、plan、tasks、analyze 與 implement。澄清時指定 Demo 不會使用目前這台電腦。凍結契約變更送出確認後，使用者以「是」明確批准 `POST /api/teacher/teams` 合法範圍由 2–12 改為 2–50。

## 主要工作紀錄

1. 建立 Issue #38、功能分支、規格文件組與 component／class／sequence 三張 PlantUML 圖。
2. 完成提案輪紅隊與架構評審，兩通道皆為 `CLEARED`。
3. 先新增邊界、狀態不變、300 台、隔離、公平與 UI 驗收，再將唯一產品上限 `MAX_TEAMS` 改為 50。
4. 更新凍結 API 契約、產品說明、老師端輸入範圍與 50 組清單捲動樣式。
5. 同步共用文件到 OpenSpec 姊妹 repo，parity 為 0 處不一致。
6. 完成 server 246 項、ops 51 項、web 36 項測試，以及圖表、繁體中文、秘密掃描、SpecKit、agents 與圖表語法門禁。

## 驗證與評審

- 300 台容量探針：300/300 最終一致，p95 58.4 ms，最慢 58.5 ms。
- 圖碼一致性：架構實作輪首驗抓到 Activity 方法名稱與學生畫面欄位漂移；訂正 PlantUML、重生 PNG 並由同通道回驗 `CLEARED`。
- 人工 UI 驗收：以 VS Code Simple Browser 完成第 50 組加入、釋放、重新加入、作答與結果定位；另將 webview 調為 768 px 內容寬，確認 50 組結果完整換行且可操作。各步均低於 30 秒，T033 與 M-022 完成。
- 實作輪紅隊首驗抓到 API 會自動轉型數字字串與整數浮點數；改用 `StrictInt` 並補負例後，同通道回驗 `CLEARED`。
- 實作輪紅隊與架構通道最終皆為 `CLEARED`；最終 `make gate` 為 server 248 項、ops 51 項、web 36 項測試全綠，parity 0 處不一致。
- 非阻塞 followup：組件圖可更精確畫出前端經 API／WebSocket 到 `app.py`，再由 `view_for` 產生畫面的路徑；主人為 @yue083139，另立卡處理並在本卡 PR 首屏登記。

## 安全自檢

紀錄不含真實學生姓名、學號、權杖或金鑰；測試資料皆為合成資料。

- 合流補記（2026-11-28）：dev 已占用 M-020 至 M-030，本卡矩陣落點統一調整為 M-031 至 M-033；兩組 PR #45、#39 均已建立，待修正 OpenSpec base 並互連說明。Edge 人工驗證完成紀錄以 OpenSpec verification.md 為準。

