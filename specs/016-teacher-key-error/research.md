# Research: 016-teacher-key-error（與 OpenSpec design D1–D3 一一對應，R_n＝D_n）

知識時點：2026-11-26。

## R1 金鑰錯誤先 accept、不送訊息、再以 4401 關閉
- Decision：`ws()` 金鑰錯誤分支 `await socket.accept()` 後 `await socket.close(code=4401)`，之前無 `current_view()`、不入連線清單、無推播迴圈。
- Rationale：瀏覽器在交握前被拒時只得 1006；student-qr 對 4403 已同法實測（真 WebSocket 用戶端收到 4403）。
- 證偽：`test_teacher_ws_bad_key_accepts_then_closes_4401`；實作前 3 failed。

## R2 4403 優先於 4401
- Decision：本機檢查在金鑰檢查之前（沿用 014 R2）。
- 證偽：`test_public_host_takes_precedence_over_bad_key`。

## R3 老師頁整頁提示（沿用 015-teacher-key-hidden）
- Decision：老師頁 `if (closedCode === 4401 || badKey) return <BadKeyNotice />;` 已由 015 實作（同名同文案）；`live.ts` 既有 4401 不重連。本功能不改元件，只補測試。

## 與 015-teacher-key-hidden 合流
- 015 先合入（SpecKit #28）；本功能 rebase 後 `Teacher.tsx` 以 dev 版為準，伺服器「先 accept 再 4401」是唯一行為變更。守門互補：M-001（本功能）、M-024（015）。
- 評審：對抗 CLEARED（990 條並發錯金鑰連線無洩漏；非並發測試改名 `test_good_connection_unaffected_after_bad_key`）；架構 NOT CLEARED(0B/1M/1m)＝合流問題，已落。
- 證偽：`qr.test.tsx`、`live.test.tsx` 新增例。
