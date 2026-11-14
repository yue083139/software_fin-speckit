# Research: 009 team-mode

知識時點：2026-11-14。對標（`docs/research/competitors.md` §1，2026-11-11 查）：Kahoot! Team mode 讓一隊共用一台裝置並給「討論時間」，隊員分數平均；Quizlet Live 隨機分隊、每位隊員只看到部分選項。依 TRD §6 裁定只取「一隊多人、一人代表作答」。

倉外行為探針：無。決策只依賴本倉既有的鎖、序號與依身分裁切的 view，不依賴第三方函式庫新行為、外部服務或瀏覽器新行為。

## R1 組隊是活動設定，不是模式

- **Decision**：`Activity.team_play: bool = False`；`set_team_play(enabled)` 鎖內、`preparing`（409）；值改變時撤銷所有憑證與邀請碼；值不變不撤銷；`reset` 保留；`configure_teams` 另清除邀請碼。
- **Rationale**：代表作答不改 TRD T-01 的四個面向（誰能作答、何時鎖題、如何計分、何時揭曉）；做成模式就得與三種模式各組合一次。
- **Alternatives**：第四種模式（TRD §3 原列法）——無法同時用時間計分＋組隊。
- **證偽欄｜屬取捨**（名稱與 TRD 模式表不一致）；可證偽部分：`test_team_mode.py::test_team_play_does_not_change_scoring`；001–008 全部測試在預設 `team_play=False` 下照舊綠。

## R2 憑證與邀請碼

- **Decision**：`_tokens`（憑證 → 組別）多對一。組隊關閉：同 001（已有憑證 ⇒ 409）。組隊開啟：該組無裝置 ⇒ 發憑證並產生邀請碼（6 碼，字母表 `ABCDEFGHJKLMNPQRSTUVWXYZ23456789`，`secrets.choice`，約 10⁹ 種，本機模擬不設嘗試次數限制）；已有裝置 ⇒ `code` 轉大寫去空白後 `secrets.compare_digest` 比對，不符 403；再檢查 `MAX_DEVICES = 6`，滿 409。先比對邀請碼再檢查上限：沒有正確碼的人不該知道該組幾台。`release` 撤銷該組全部憑證並刪除邀請碼。讓出點夾在檢查與寫入之間。
- **Rationale**：沒有邀請碼，選一個已有人的組別就能讀到該組草稿與送出。
- **證偽欄｜可證偽**：`test_join_requires_code`、`test_device_limit`、`test_concurrent_join_at_limit`、`test_release_revokes_all_devices_and_code`、`test_toggle_revokes`。

## R3 送出：代表作答

- **Decision**：`submit` 不改；送出成功後清除該組該題草稿。
- **證偽欄｜可證偽**：`test_concurrent_submit_same_team`（3 台並發 20 次恰 1 筆成功、序號無重號）、`test_member_sees_team_submission`。

## R4 組內草稿

- **Decision**：`POST /api/student/draft`（`X-Team-Token`，`{question, answers}` ⇒ `{question}`，不回顯內容）。403 憑證無效；409 非組隊、非 `answering`、本組已送出、時間計分非開放中題；404 題號；422 長度≠子題數、超過 200 字、控制字元（訊息固定）；空白允許。`drafts: dict[組別, dict[題號, tuple]]`，最後寫入者為準；送出、匯入、重置、釋放、切換組隊時清除。不記日誌內容。
- **證偽欄｜可證偽**：`test_draft_rules`；`test_isolation.py::test_team_draft_isolated`、`test_other_team_draft_sends_nothing`。

## R5 view 與作答隔離

- **Decision**：學生（有效憑證）`team_play`、`invite_code`（組隊時）、`drafts`（只在 `answering`、只含本組）；老師 `team_play`、`devices`、`invite_codes`（不含草稿）；公開資訊只增 `team_play`；無效憑證仍只回最少資訊。草稿更新只改本組 view，他組連線不推送。
- **證偽欄｜可證偽**：`test_isolation.py` 三則（他組草稿與邀請碼不在本組 WebSocket／REST 成功與錯誤回應／公開資訊；他組草稿更新時本組 seq 不跳號；判定中與已結束學生 view 無 `drafts` 鍵）。

## R6 web

- **Decision**：老師「組別」區塊組隊勾選框（準備階段）、每組「已加入（n 台）」與邀請碼；首頁組隊時已加入的組別不停用、多「邀請碼」輸入欄；學生頁顯示本組邀請碼；作答卡輸入後 400 毫秒送草稿，組內草稿與本機輸入不同時顯示「組內草稿：…」與「套用」（不覆蓋正在輸入的內容）。
- **證偽欄｜可證偽**：`web/src/pages/team.test.tsx`。
