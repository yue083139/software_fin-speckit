# Implementation Plan: 前後端骨架、身分進場與活動階段同步

**Branch**: `001-app-skeleton` | **Date**: 2026-11-11 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-app-skeleton/spec.md`
**藍圖**（憲章原則 VII）：`diagrams/system-component.puml`、`diagrams/001-app-skeleton-{component,class,sequence}.puml`

## Summary

首屏決策摘要（每行「選了 X／代價 Y／可被 Z 證偽」）：

1. **伺服器是唯一狀態來源，WebSocket 每連線各自計算 view、內容不變就不送**／代價：每次變更 O(連線數) 次序列化（本機 ≤ 20 連線可忽略）／可被「老師切階段所有連線收到」與「他組動作本連線 0 則訊息」測試證偽。
2. **階段狀態機預留 `judging`**（`docs/trd-game-modes.md` T-03）／代價：一個目前用不到的狀態／可被轉移表窮舉測試證偽。
3. **老師身分＝啟動時產生的老師金鑰**／代價：每次重啟要重新複製網址／屬取捨：本機模擬不做帳號，但學生不能打開老師頁。
4. **學生身分＝伺服器發的組別憑證，一組一台裝置**／代價：裝置掛掉需老師釋放／可被「改網址組別參數但無憑證只拿到最少資訊」測試證偽。

## Technical Context

**Language/Version**: Python 3.12（server）、TypeScript 6（web）
**Primary Dependencies**: FastAPI、uvicorn、websockets（server）；React 19、Vite 8（web）
**Storage**: 伺服器記憶體（第一期不做快照，`docs/parity.md` §2）
**Testing**: pytest（含 30 秒逾時）、vitest＋Testing Library
**Target Platform**: 本機瀏覽器，伺服器 `127.0.0.1:8000`
**Project Type**: web application（`server/` + `web/`）
**Performance Goals**: 本機 ≤ 12 組、≤ 20 連線
**Constraints**: 作答隔離、順位以伺服器為準、繁體中文介面
**Scale/Scope**: 單一活動、單一老師

## Constitution Check

| 原則 | 本功能如何符合 | 結果 |
|---|---|---|
| I 需求即法律、兩組一致 | 涵蓋 R-01、R-11；行為與 `docs/parity.md` §4 `app-skeleton` 行一致，契約 `contracts/api.md` 兩組共用 | ✅ |
| II 作答隔離 | 學生 view 只由 `views.student_view` 產生；無效憑證回最少資訊；推播時機不透露他組活動 | ✅ |
| III 順位以伺服器為準 | 本功能尚無作答；活動鎖與讓出點為 002～003 的前提 | ✅ |
| IV Guided Notes 動態定位 | 不涉及 | N/A |
| V 測試先行與人工驗證 | 先寫 `test_phases.py`、`test_api_skeleton.py`；`verification.md` 含人工驗證步驟 | ✅ |
| VI 簡單與本機優先 | 記憶體狀態、單埠 | ✅ |
| VII 圖表優先 | 四張圖已產出並轉 PNG；實作後核對（見 `verification.md`） | ✅ |
| VIII 繁體中文與資料衛生 | 介面文案繁中；金鑰與憑證不入庫、不出現在日誌 | ✅ |

## Project Structure

### Documentation (this feature)

```text
specs/001-app-skeleton/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── contracts/README.md   # 指向 /contracts/api.md（兩組共用凍結件）
├── tasks.md
└── verification.md       # 門禁原樣輸出、變異實錄、圖碼一致核對、人工驗證
```

### Source Code (repository root)

```text
server/
├── pyproject.toml
├── quiz_server/
│   ├── __main__.py     # 組件圖 __main__
│   ├── app.py          # 組件圖 app.py；時序圖 app.py
│   ├── activity.py     # 類別圖 Activity
│   ├── phases.py       # 類別圖 Phase、PhaseError
│   └── views.py        # 類別圖 views
└── tests/
    ├── conftest.py
    ├── test_phases.py
    └── test_api_skeleton.py

web/
├── package.json、vite.config.ts、tsconfig.json、eslint.config.js、index.html
└── src/
    ├── main.tsx、App.tsx、route.ts、types.ts、api.ts、live.ts、styles.css
    └── pages/
        ├── Home.tsx、Teacher.tsx、Student.tsx
        └── pages.test.tsx

contracts/api.md
```

**Structure Decision**: web application（Option 2）；目錄名 `server/`、`web/` 與 OpenSpec 組相同，便於兩組對照。

## Complexity Tracking

無違反憲章之處。
