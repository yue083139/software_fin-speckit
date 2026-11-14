# 第三期評審紀錄：team-mode（2026-11-14）

- 對象：S 檔卡 `team-mode`（兩組同批：OpenSpec change `team-mode`、SpecKit `009-team-mode`）。
- 方式：提案輪＋實作輪各一輪，紅隊與架構兩通道互不知情（`.claude/agents/finder-tail-{red,arch}.md`＋`review-dispatch` 骨架）；藥方由各自開方的通道回驗。
- 結論：
  - 提案輪（v1.0）：紅隊 `NOT CLEARED(0B/1M/1m)`、架構 `NOT CLEARED(0B/2M/2m)`；藥方併入 v1.1。
  - 實作輪（末輪，含藥方回驗）：紅隊 `CLEARED`（另以兩則變異自證守門測試會紅）；架構 `CLEARED`（另 1 次要：SpecKit R6 與組件圖未寫「邀請碼只在準備階段」，已修）。兩通道閉環。

## 提案輪發現與藥方

| 通道 | 等級 | 發現 | 藥方落點 |
|---|---|---|---|
| 紅隊 | 重要 | 釋放後該組回到「無裝置」，任何人不帶碼即可以第一台搶佔，新碼還顯示在冒用者畫面 | 釋放即換新碼、只在老師 view；有碼就須帶碼（design D2；`test_release_revokes_all_devices_and_code`） |
| 紅隊 | 次要 | 全形輸入使 `compare_digest` 拋例外、回 500 | NFKC 後以位元組比對（`normalize_code`；`test_fullwidth_code_accepted`） |
| 架構 | 重要 | 邀請碼常駐學生畫面且搶答中可加入，瞄到 6 碼即可冒用 | 學生只在準備階段看得到；開始搶答換新所有碼（design D2、D5；`test_code_rotates_on_start_and_hidden_from_students`、`test_invite_code_not_sent_to_students_while_answering`） |
| 架構 | 重要 | 契約身分表、join、release 的語意改變被寫成「純新增」，繞過負責人批准 | design D7／research R7 逐條列四處語意補充，**呈負責人批准** |
| 架構 | 次要 | 同紅隊次要 | 同上 |
| 架構 | 次要 | 台數算憑證數、關分頁不釋放名額、只能整組釋放 | 列為取捨並寫明理由（design D2、research R2） |

## followup（不阻塞）

- 準備階段已憑碼加入的冒用者，開始搶答換碼後憑證不撤銷；老師可從台數看出並釋放整組（已寫入 design D2 殘餘風險）。
- 時間計分下 `set_draft` 只看回合是否關閉、不比對時限；時限到與計時器關閉之間的數毫秒仍收草稿，只有本組看得到，不影響判定。
- 首頁只在載入時讀一次公開資訊，老師切換組隊後學生要重新整理首頁（同第一期）。

## 呈負責人

1. `contracts/api.md` 四處語意補充（身分表一組多台；join 帶 `code`、403、組隊時 409 指已滿；release 換新碼；改組數清碼與草稿）——我傾向批准：組隊關閉時與第一期完全相同。
2. 人工驗證（P-05）：`docs/manual-verification.md` 場次 E，交組員執行。
