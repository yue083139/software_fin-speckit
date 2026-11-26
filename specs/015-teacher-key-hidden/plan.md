# Implementation Plan: 015-teacher-key-hidden

**Branch**: `015-teacher-key-hidden` | **Date**: 2026-11-26 | **Spec**: [spec.md](spec.md)

## Summary

老師金鑰載入後自網址移除、存本分頁 sessionStorage；只改 web，伺服器與契約不變。以 `diagrams/015-teacher-key-hidden-*.puml` 為藍圖（憲章原則 VII）。

## Technical Context

React 19＋Vite＋TypeScript＋antd 5；vitest＋jsdom；兩組 web 逐字相同。

## Constitution Check

- 作答隔離：不新增送往學生的資料；學生頁不讀 `qz_teacher_key`。✅
- 簡單與本機優先：不改伺服器、不新增依賴。✅
- 圖表優先：三張圖先於實作。✅
- 繁體中文：文案沿用既有句。✅

## 變更點

| 檔 | 內容 |
|---|---|
| `web/src/route.ts` | `TEACHER_KEY_STORE`、`takeTeacherKey()`、`clearTeacherKey()` |
| `web/src/App.tsx` | 老師頁改用 `takeTeacherKey()` |
| `web/src/pages/Teacher.tsx` | REST 401／4401 清除並顯示錯誤頁 |
| `web/CLAUDE.md`（＋`make sync-agents`） | 金鑰規範句 |
| README、`docs/manual-verification.md` 場次 G、`docs/parity.md`、`eval/acceptance/matrix.yaml` M-024 | 文件 |

## 圖碼一致核對

實作後逐條核：component（App→route→sessionStorage／history；Teacher→api）、class（route 三個匯出）、sequence（載入→replaceState→存→重新整理→401 清除）與程式一致。
