# Implementation Plan: 016-teacher-key-error

**Branch**: `016-teacher-key-error` | **Date**: 2026-11-26 | **Spec**: `specs/016-teacher-key-error/spec.md`
**藍圖**：`diagrams/016-teacher-key-error-{component,class,sequence}.puml`（憲章原則 VII）

## Summary
老師 WebSocket 金鑰錯誤改為「先交握、不送訊息、再以 4401 關閉」，老師頁收到 4401 整頁顯示提示。

## Technical Context
Python 3.12／FastAPI WebSocket；React 19＋antd 5。只改 `server/quiz_server/app.py` 一個分支與 `web/src/pages/Teacher.tsx` 一個元件。

## Constitution Check
- 作答隔離：錯金鑰連線關閉前不送任何訊息 ✅
- 圖表優先：三張圖先於實作 ✅；實作後核對一致 ✅
- 兩組一致：server、web、contracts 與 OpenSpec 組逐字相同 ✅

## 程式與圖對照
| 圖元素 | 程式 |
|---|---|
| app.ws（金鑰錯誤分支） | `server/quiz_server/app.py` `ws()` |
| useLiveView／NO_RECONNECT | `web/src/live.ts` |
| BadKeyNotice（015 實作，本功能沿用） | `web/src/pages/Teacher.tsx` |
