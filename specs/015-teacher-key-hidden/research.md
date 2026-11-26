# 015 teacher-key-hidden — research（v1.0）

> 與 OpenSpec 組 `openspec/changes/teacher-key-hidden/design.md` D1–D3 一一對應（R_n＝D_n）。知識時點：2026-11-26。

## R1 自網址移除：`history.replaceState`

- 決策：`takeTeacherKey()` 解析 hash，有 `key` ⇒ 存 sessionStorage、刪 `key`、`history.replaceState(history.state, "", pathname+search+"#/teacher"+其餘參數)`；無 ⇒ 回 sessionStorage 值或 `""`。`App` 以 `useMemo(..., [hash])` 重算。
- 理由：取代目前紀錄項、不觸發 `hashchange`；hash 本就不隨請求外送（不在 Referer、伺服器日誌）。不保證瀏覽器「記錄」頁與自動完成不留最初貼上的網址（瀏覽器行為）。
- 替代方案：cookie session（需改伺服器與契約，超出 B 檔）；只存記憶體（重新整理即失效，老師體驗差）。

## R2 存放：本分頁 sessionStorage

- 決策：鍵 `qz_teacher_key`；不寫 localStorage、cookie；學生憑證另一鍵，互不讀取。
- 屬取捨：同源腳本可讀 sessionStorage；但金鑰原本就在 `location.href`，風險面不增；前端無 `dangerouslySetInnerHTML`。

## R3 金鑰錯誤即清除

- 決策：REST 401（開頁查 Google 狀態最先發出）或 4401 ⇒ `clearTeacherKey()` 並顯示既有錯誤頁。
- 理由：伺服器對錯誤金鑰 WebSocket 交握前拒絕（student-qr followup），靠 REST 401 讓提示顯示得出來。
