# Research: 009 team-mode

知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，2026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論時間」，隊員分數平均；Quizlet Live 隨機分隊、每位隊員只看到部分選項。依 TRD §6 裁定只取「一隊多人、一人代表作答」。

**v1.1（提案輪評審）**：紅隊——釋放後下一台不需碼即可搶佔（改為釋放即換新碼、只在老師畫面）；全形輸入使 `compare_digest` 拋例外（改 NFKC 後以位元組比對）。架構——邀請碼常駐學生畫面且搶答中可加入（改為學生只在準備階段看得到、開始搶答換新碼）；契約身分表、join、release 屬語意補充（R7，呈負責人批准）；台數算憑證數（列為取捨）。

倉外行為探針：無。決策只依賴本倉既有的鎖、序號與依身分裁切的 view，不依賴第三方函式庫新行為、外部服務或瀏覽器新行為。

## R1 組隊是活動設定，不是模式

- **Decision**：`Activity.team_play: bool = False`；`set_team_play(enabled)` 鎖內、`preparing`（409）；值改變時撤銷所有憑證與邀請碼；值不變不撤銷；`reset` 保留；`configure_teams` 另清除邀請碼。
- **Rationale**：代表作答不改 TRD T-01 的四個面向（誰能作答、何時鎖題、如何計分、何時揭曉）；做成模式就得與三種模式各組合一次。
- **Alternatives**：第四種模式（TRD §3 原列法）——無法同時用時間計分＋組隊。
- **證偽欄｜屬取捨**（名稱與 TRD 模式表不一致）；可證偽部分：`test_team_mode.py::test_team_play_does_not_change_scoring`；001–008 全部測試在預設 `team_play=False` 下照舊綠。

## R2 憑證與邀請碼

- **Decision**：`_tokens`（憑證 → 組別）多對一。組隊關閉：同 001（已有憑證 ⇒ 409）。組隊開啟且該組**有邀請碼**（已有裝置或曾被釋放）⇒ `code` 經 NFKC、去空白、轉大寫後以位元組 `secrets.compare_digest` 比對，不符 403；再檢查 `MAX_DEVICES = 6`，滿 409（先比對碼：沒有正確碼的人不該知道該組幾台）。組隊開啟且**無邀請碼** ⇒ 發憑證並產生邀請碼（6 碼，字母表 `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`，`secrets.choice`，約 10⁹ 種，不設嘗試次數限制，屬取捨）。`start` 換新所有邀請碼；`release` 撤銷該組全部憑證、清草稿並換新碼（只在老師畫面）。讓出點夾在檢查與寫入之間。台數＝已發出憑證數，關分頁不釋放名額，只能整組釋放（屬取捨：單台釋放需裝置識別與在線偵測）。
- **Rationale**：沒有邀請碼，選一個已有人的組別就能讀到該組草稿與送出；常駐顯示的碼在搶答中被瞄到、或釋放後搶先以第一台加入，都會重新打開冒用。
- **證偽欄｜可證偽**：`test_join_requires_code`、`test_fullwidth_code_accepted`、`test_device_limit`、`test_concurrent_join_at_limit`、`test_concurrent_first_join_one_code`、`test_release_revokes_all_devices_and_code`、`test_code_rotates_on_start_and_hidden_from_students`、`test_toggle_revokes_only_on_change`。

## R3 送出：代表作答

- **Decision**：`submit` 不改；送出成功後清除該組該題草稿。
- **證偽欄｜可證偽**：`test_concurrent_submit_same_team`（3 台並發 20 次恰 1 筆成功、序號無重號）、`test_member_sees_team_submission`。

## R4 組內草稿

- **Decision**：`POST /api/student/draft`（`X-Team-Token`，`{question, answers}` ⇒ `{question}`，不回顯內容）。`set_draft` 在鎖內檢查與寫入。403 憑證無效；409 非組隊（「只有組隊模式可以共用草稿」）、非 `answering`、本組已送出、時間計分非開放中題；404 題號；422 長度≠子題數、超過 200 字、控制字元（訊息固定）；空白允許。`drafts: dict[組別, dict[題號, tuple]]`，最後寫入者為準；送出、匯入、重置、釋放、切換組隊、改組數時清除。草稿與邀請碼都不記日誌。前端送出時取消未送的草稿計時器，草稿請求失敗靜默。
- **證偽欄｜可證偽**：`test_draft_rules`；`test_isolation.py::test_team_draft_isolated`、`test_other_team_draft_sends_nothing`。

## R5 view 與作答隔離

- **Decision**：學生（有效憑證）`team_play`、`invite_code`（組隊且只在 `preparing`）、`drafts`（只在 `answering`、只含本組）；老師 `team_play`、`devices`（每組都列）、`invite_codes`（只列有碼的組，含釋放後待加入者；不含草稿）；公開資訊只增 `team_play`；無效憑證仍只回最少資訊。草稿更新只改本組 view，他組連線不推送。
- **證偽欄｜可證偽**：`test_isolation.py` 五則：`test_team_draft_isolated`、`test_other_team_draft_sends_nothing`、`test_drafts_only_in_answering`、`test_invalid_token_gets_no_team_fields`、`test_invite_code_not_sent_to_students_while_answering`。

## R6 web

- **Decision**：老師「組別」區塊組隊勾選框（準備階段）、每組「已加入（n 台）」與邀請碼；首頁組隊時已加入的組別不停用、多「邀請碼」輸入欄；學生頁顯示本組邀請碼；作答卡輸入後 400 毫秒送草稿，組內草稿與本機輸入不同時顯示「組內草稿：…」與「套用」（不覆蓋正在輸入的內容）。
- **證偽欄｜可證偽**：`web/src/pages/team.test.tsx`。

## R7 契約語意補充（v1.1，呈負責人批准）

- **Decision**：`contracts/api.md` 以下既有字句在組隊時語意改變（組隊關閉時與 001 相同）：①身分表「一組一台裝置」補「組隊時最多 6 台，第二台起憑邀請碼加入」；②`POST /api/student/join` 本體 `{team, code?}`，增 403「邀請碼不正確」，409 在組隊時改指「此組裝置已滿」；③`release` 組隊時撤銷全部裝置、清草稿並換新碼；④`teams` 另清除邀請碼與草稿。`docs/product-trd.md` §3 同批補「組隊時最多 6 台」。
- **證偽欄｜可證偽**：001 的 `test_join_once_per_team`、`test_concurrent_join_same_team_once` 不改仍綠；`test_single_device_without_team_play_unchanged`。
