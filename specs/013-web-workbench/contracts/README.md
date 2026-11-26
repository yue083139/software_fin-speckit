# 013 web-workbench 介面契約

**本卡不改契約**：[`/contracts/api.md`](../../../contracts/api.md) 的 REST 端點、錯誤碼、WebSocket 訊息與老師／學生 view 欄位全部不變。

前端型別 `TeacherView.student_url?: string` 為 `student-qr` 卡預留；該欄位由 `student-qr` 卡在契約中新增，本卡只在前端以可選欄位讀取，伺服器未提供時用本頁網址。
