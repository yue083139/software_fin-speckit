## 0 抬頭
評審對象＝`specs/010-team-limit-50/` 規格文件組 @ v1.0（spec、plan、tasks、diagrams 抬頭一致）
基線＝dev `3cb04488e4078a866312d681db869701977440bf`；本輪 commit＝`82edba8..cbfba80`（評審員自己 git show，不看我的描述）
通道＝架構；不告知輪次、不告知其他通道結論
約束＝禁改工作樹；禁跑會呼叫雲端 API 的指令（門禁由主 agent 統一真跑並附輸出）
知識時點＝2026-11-27

## 1 範圍
本輪＝全卡掃：規格文件組、三圖、凍結契約、產品實作、驗收與門禁現狀
本卡至今全卡掃次數＝1；本輪為 S 檔第 2 輪末輪

## 2 斷言清單
A-1 | 結論＝架構變更維持 Activity 為伺服器上限裁決來源，API、view 與結果模型不衍生第二份裁決規則 | 稿內落點＝`server/quiz_server/activity.py:20`、`server/quiz_server/app.py:39`、`diagrams/010-team-limit-50-component.puml`、`diagrams/010-team-limit-50-class.puml` | 理由＝領域上限由 Activity 裁決，API 另以 `StrictInt` 拒絕格式錯誤，既有 view 裁切不變 | 已自對碼＝產品程式改 `activity.py`、`app.py`、`Teacher.tsx`、`styles.css` | 請證偽
A-2 | 結論＝合法改組的生命週期仍原子撤銷 tokens、codes、drafts，拒絕路徑不改狀態 | 稿內落點＝`server/quiz_server/activity.py:231`、`server/tests/test_team_mode.py`、`server/tests/test_api_skeleton.py` | 理由＝容量擴張不得產生舊身分跨組存活 | 已自對碼＝`122 passed, 1 warning in 16.52s` | 請證偽
A-3 | 結論＝50 組乘每組六台的 300 連線仍沿用身分裁切與鎖內伺服器序號，沒有新增跨元件狀態 | 稿內落點＝`specs/010-team-limit-50/plan.md:11`、`server/tests/test_isolation.py`、`server/tests/test_submit.py`、`probes/results/2026-11-27-team-limit-50-capacity-implementation.txt` | 理由＝保留現有隔離與公平架構可降低核心風險 | 已自對碼＝`300/300` 最終一致；完整 server `246 passed` | 請證偽
A-4 | 結論＝三張圖與實作的元件、類別約束及設定與加入訊息序一致 | 稿內落點＝`specs/010-team-limit-50/verification.md:142`、`diagrams/010-team-limit-50-sequence.puml` | 理由＝Diagram First 要求實作後逐圖核對 | 已自對碼＝`gate-diagrams-syntax: 31 個圖檔語法通過` | 請證偽
A-5 | 結論＝兩組共用契約與 parity 登記已同步，SpecKit 與 OpenSpec 不產生功能口徑分叉 | 稿內落點＝`contracts/api.md:32`、`docs/parity.md`、`specs/010-team-limit-50/plan.md:37` | 理由＝共用需求與凍結契約必須逐位元一致 | 已自對碼＝`gate-parity: 0 處不一致` | 請證偽

## 3 上輪藥方落點
架構通道要求把姊妹 repo已同步事實回填 plan → `82edba8/specs/010-team-limit-50/plan.md:37` → `gate-parity: 0 處不一致`。架構末輪首驗藥方：把兩圖不存在的 `set_teams` 訂正為 `configure_teams`、移除學生畫面的完整組別欄位並訂正核對表 → `cbfba80/diagrams/010-team-limit-50-{class,sequence}.puml`、`cbfba80/specs/010-team-limit-50/verification.md` → `gate-diagrams: 31 個圖檔，0 處問題`；本次為同通道回驗。
紅隊通道無藥方。全倉差集掃描由評審員以 `git grep -n <模式> -- :/` 獨立完成；`.env` 不入庫且未改，無記憶檔。

## 4 有意不改
`server/quiz_server/app.py`、`views.py`、`Home.tsx`、`Results.tsx` | 既有委派、裁切與完整渲染已通過新增驗收，避免無需求的跨元件改動

## 5 未決呈裁
無

## 6 退出條件
本輪放行判據＝0 阻斷，核心生命週期、隔離、公平、契約、parity 與圖碼一致性的重要項全部有稿內落點
輪次上限按 `CLAUDE.md` 分檔表，本輪觸頂即停；上限後只有「淨回歸／使原修復失效／假綠掩蓋原病」三類可阻塞，其餘進 followup

## 7 返回格式
一句話結論；每條發現五行：哪兒（file:line）／什麼錯／會怎樣（具體後果）／怎麼修／證據（指令 → 輸出）；
編號與符號只進「哪兒」「證據」兩欄，術語首現即解釋；「外包檢查」：指出 §2 哪條其實是問句或稿內無落點；「我查閱的檔案」；
末行 `CLEARED` / `NOT CLEARED(nB/nM/nm)`（B＝阻斷 M＝重要 m＝次要）。

## 8 預算
讀取面＝全卡掃：`git diff 82edba8 cbfba80`、規格文件組、三圖、凍結契約、驗收矩陣與門禁現狀
返回長度＝60 行上限
續用還是新起＝新起；實作末輪須與作者會話隔離
