# web — 元件規範

- React＋Vite＋TypeScript，npm 管理依賴（`npm --prefix web ci`）；`npm --prefix web test`（vitest）、`run lint`（ESLint）、`run typecheck`。
- 畫面只顯示伺服器推來的 view，**不在前端判定順位、不在前端過濾他組資料**：學生看不到的資料，伺服器就不該送（`CLAUDE.md`「作答隔離」）。
- 所有介面文案用繁體中文；老師金鑰只放在網址參數與記憶體，不寫入 localStorage。
- 元件測試以假 view 物件渲染，不連真 server。
