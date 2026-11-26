# 015 teacher-key-hidden 介面契約

本功能不改 [`/contracts/api.md`](../../../contracts/api.md)：老師仍以標頭 `X-Teacher-Key` 與 WebSocket 查詢參數 `key` 帶金鑰；只改前端金鑰從哪裡取（網址首次帶入後改由本分頁 sessionStorage）。
