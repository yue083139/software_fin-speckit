# Research: 019-live-feed（與 OpenSpec design D1–D4 一一對應，R_n＝D_n）

知識時點：2026-11-27。

## 對標
- Kahoot 主持人畫面：題目進行中即時顯示已作答人數的跳動（依公開產品操作經驗）；「某某搶下第 N 題」通知是常見的課堂遊戲化手法。
- 裁剪：只做文字快訊，不做音效與動畫。

## R1 前端比對前後兩次老師 view，不改伺服器
- Decision：`feedEvents(prev, next)` 對 `next.board` 每題每個 `ranking` 項，若 `prev` 同題沒有該組 ⇒ 一則事件，`key＝<題號>-<組別>`。老師 view 任何階段都帶完整 `board`（`server/quiz_server/views.py`「"board": results.build(a, teacher=True)」）。
- Rationale：不新增 view 欄位 ⇒ 作答隔離與契約不受影響，不升 S 檔。
- 證偽：「經典搶答第 1 順位是『搶下』，之後是『送出』」「沒有新送出不出通知」。

## R2 第一個 view 只當基準
- Decision：`useLiveFeed` 以 `useRef` 記上一個 view，`prev === null` 時只更新基準；重新整理會重掛元件 ⇒ 不重跳；斷線重連時元件不重掛，只跳斷線期間的新送出。
- 證偽：「第一次收到 view 只當基準，不出通知」「新送出時右上角跳出通知，開頁時不跳」；變異拿掉 `prev === null` ⇒ 2 failed。

## R3 只在搶答中；經典第 1 順位才說「搶下」
- Decision：`next.phase !== "answering"` ⇒ 不出；`mode.key === "classic"`（無 mode 視為經典）且 `rank === 1` ⇒「搶下」，其餘「送出」。
- Rationale：判定類模式第 1 順位不一定得分；結束後的答對／答錯檢查不是新送出。
- 證偽：「非經典模式一律『送出』」「不在搶答中不出通知」；對應變異各 1 failed。

## R4 文案不含答案
- Decision：只用 `team` 與 `number`，`answers` 不進文案。
- Rationale：老師頁常投影給全班，答案在結束前曝光等於破壞搶答。
- 證偽：「文案不含答案」。
