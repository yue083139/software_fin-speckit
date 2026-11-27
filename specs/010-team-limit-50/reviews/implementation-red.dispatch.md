## 0 抬頭
評審對象＝`specs/010-team-limit-50/` 規格文件組 @ v1.0（spec、plan、tasks、diagrams 抬頭一致）
基線＝dev `3cb04488e4078a866312d681db869701977440bf`；本輪 commit＝`82edba8..76acaeb`（評審員自己 git show，不看我的描述）
通道＝紅隊；不告知輪次、不告知其他通道結論
約束＝禁改工作樹；禁跑會呼叫雲端 API 的指令（門禁由主 agent 統一真跑並附輸出）
知識時點＝2026-11-27

## 1 範圍
本輪＝全卡掃：規格文件組、三圖、凍結契約、產品實作、驗收與門禁現狀
本卡至今全卡掃次數＝1；本輪為 S 檔第 2 輪末輪

## 2 斷言清單
A-1 | 結論＝組數唯一上限來源已由 12 提高為 50，2、12、13、50 合法而 1、51 與格式錯誤保持拒絕且不改狀態 | 稿內落點＝`server/quiz_server/activity.py:20`、`server/tests/test_api_skeleton.py`、`server/tests/test_phases.py` | 理由＝邊界與拒絕原子性由同一常數及契約測試鎖定 | 已自對碼＝`81 passed, 1 warning in 7.76s` | 請證偽
A-2 | 結論＝50 組沒有削弱每組六台、作答隔離與伺服器順位公平 | 稿內落點＝`server/tests/test_team_mode.py`、`server/tests/test_isolation.py`、`server/tests/test_submit.py` | 理由＝300 台、第 301 台拒絕、其他 49 組答案負例及 20 輪並發皆有永久驗收 | 已自對碼＝`122 passed, 1 warning in 16.52s`；`最終狀態一致：是（300/300）` | 請證偽
A-3 | 結論＝學生選組、老師管理與結果畫面完整保留第 50 組，桌面及 768 px 內容寬皆可在 30 秒內操作 | 稿內落點＝`web/src/pages/team-limit.test.tsx`、`web/src/pages/Teacher.tsx:165`、`web/src/styles.css:10`、`specs/010-team-limit-50/verification.md:152` | 理由＝元件驗收、捲動樣式與真 UI 操作共同覆蓋 | 已自對碼＝`Test Files  8 passed (8)`；`Tests  36 passed (36)`；人工各步 8–18 秒 | 請證偽
A-4 | 結論＝凍結 API 契約只改 `{count}` 合法範圍，不改端點、回應形狀、錯誤語意與每組六台上限 | 稿內落點＝`contracts/api.md:32`、`specs/010-team-limit-50/contracts/api-change.md` | 理由＝負責人明確批准且產品端點仍委派既有 Activity | 已自對碼＝`gate-parity: 0 處不一致`；負責人原文「是」 | 請證偽

## 3 上輪藥方落點
架構通道要求把姊妹 repo 已同步事實回填 plan → `82edba8/specs/010-team-limit-50/plan.md:37` → `gate-parity: 0 處不一致`
紅隊通道首驗藥方：`TeamsBody.count` 改為 `StrictInt`，並補 `50.0`、`"50"` 皆回 422 且狀態不變的負例 → `76acaeb/server/quiz_server/app.py:39`、`76acaeb/server/tests/test_api_skeleton.py:136` → `35 passed, 1 warning in 4.25s`。本次為同通道回驗。全倉差集掃描由評審員以 `git grep -n <模式> -- :/` 獨立完成；`.env` 不入庫且未改，無記憶檔。

## 4 有意不改
`server/quiz_server/app.py`、`views.py`、`Home.tsx`、`Results.tsx` | 既有委派、裁切與完整渲染已通過新增驗收，避免無需求的產品改動

## 5 未決呈裁
無

## 6 退出條件
本輪放行判據＝0 阻斷，產品行為、作答隔離、順位公平、凍結契約與圖碼一致性的重要項全部有稿內落點
輪次上限按 `CLAUDE.md` 分檔表，本輪觸頂即停；上限後只有「淨回歸／使原修復失效／假綠掩蓋原病」三類可阻塞，其餘進 followup

## 7 返回格式
一句話結論；每條發現五行：哪兒（file:line）／什麼錯／會怎樣（具體後果）／怎麼修／證據（指令 → 輸出）；
編號與符號只進「哪兒」「證據」兩欄，術語首現即解釋；「外包檢查」：指出 §2 哪條其實是問句或稿內無落點；「我查閱的檔案」；
末行 `CLEARED` / `NOT CLEARED(nB/nM/nm)`（B＝阻斷 M＝重要 m＝次要）。

## 8 預算
讀取面＝全卡掃：`git diff 82edba8 76acaeb`、規格文件組、三圖、凍結契約、驗收矩陣與門禁現狀
返回長度＝60 行上限
續用還是新起＝新起；實作末輪須與作者會話隔離
