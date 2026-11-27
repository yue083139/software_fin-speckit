# Implementation Plan: 019-live-feed

**Branch**: `019-live-feed` | **Date**: 2026-11-27 | **Spec**: `specs/019-live-feed/spec.md`
**藍圖**：`diagrams/019-live-feed-{component,class,sequence}.puml`（憲章原則 VII）

## Summary

1. **前端比對前後兩次老師 view 的 `board` 找新送出，不改伺服器**（R1）／代價：快訊時刻＝推播到達時刻／可被 `livefeed.test.tsx`「經典搶答第 1 順位是『搶下』」證偽。
2. **第一個 view（開頁、重整）只當基準不出通知**（R2）／可被「第一次收到 view 只當基準」證偽。
3. **只在搶答中、只經典第 1 順位說「搶下」**（R3）／可被「非經典模式一律『送出』」證偽。
4. **文案只含組別與題號、不含答案**（R4）：老師頁常投影／可被「文案不含答案」證偽。

**矩陣落點**：M-029（R-04、X-04）守門 `web/src/pages/livefeed.test.tsx`。
**merge 三問第三問**：R-04「檢視搶答時的作答狀況」的即時呈現強化，課堂投影時提升參與感（X-04）；只改前端，範圍成本小。

## Technical Context
React 19＋antd 5＋TypeScript。新增 `web/src/pages/LiveFeed.tsx`（`feedEvents`＋`useLiveFeed`，antd `App.useApp().notification`）；`Teacher.tsx` 在 `useLiveView` 後呼叫；`main.tsx` 的 `<AntApp notification={{ maxCount: 4 }}>`。不改 server、contracts。

## Constitution Check
- 作答隔離：只在老師頁；學生端不變，不新增送往學生端的資料 ✅
- 順位以伺服器為準：「搶下」直接讀伺服器給的 `rank`，前端不判定順位 ✅
- 圖表優先：三張圖先於實作 ✅；實作後核對見 `verification.md`
- 兩組一致：web 與 OpenSpec 組逐字相同 ✅

## 程式與圖對照
| 圖元素 | 程式 |
|---|---|
| feedEvents／FeedEvent | `web/src/pages/LiveFeed.tsx` |
| useLiveFeed（useRef 基準、notification.open） | `web/src/pages/LiveFeed.tsx` |
| Teacher（useLiveView 後呼叫 useLiveFeed） | `web/src/pages/Teacher.tsx` 預設匯出元件 |
| AntApp（notification maxCount 4） | `web/src/main.tsx` |
