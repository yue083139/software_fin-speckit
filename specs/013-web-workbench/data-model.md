# Data Model: 013 web-workbench

對照 `diagrams/013-web-workbench-class.puml`。本卡不改伺服器資料模型，只有前端型別與元件。

| 實體 | 欄位／介面 | 說明 |
|---|---|---|
| `TeacherView`（增） | `student_url?: string` | `student-qr` 卡提供的學生公開網址；無則用本頁網址 |
| `theme.palette`（新） | 主色、文字三階灰、發絲線、光暈四色等 | 顏色單一出處 |
| `theme.quizTheme`（新） | antd `ThemeConfig` | token 與元件覆寫 |
| `theme.cssVars()`（新） | → `Record<string, string>` | 注入 `--qz-*` |
| `ui.Btn`（新） | antd `ButtonProps` | 預設不插空白 |
| `ui.PhaseTag`（新） | `{ phase }` | 階段膠囊 |
| `ui.Section`（新） | `{ id?, title?, extra?, children }` | 內容卡；`id` 供導覽捲動 |
| `ui.Backdrop`、`ui.GlassHeader`、`Shell`（新） | — | 背景光暈、玻璃頂欄、頁面外殼 |
| `Teacher.StudentLink`（新） | `{ url }` | 學生連結＋QR code |
| `test-utils.btn`／`allBtn`（新） | `(text) → HTMLButtonElement` | 取文字外層 `<button>` |
