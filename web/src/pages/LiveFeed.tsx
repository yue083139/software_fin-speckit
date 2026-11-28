import { App } from "antd";
import { useEffect, useRef } from "react";
import type { TeacherView } from "../types";

export interface FeedEvent {
  key: string;
  text: string;
}

/**
 * 比對前後兩次老師 view，列出新出現的送出（live-feed）。
 * 開頁、重新整理或斷線重連後收到的第一個 view 只當基準不出通知，避免把已有的送出一次全跳出來；
 * 只在搶答中出通知。文案只含組別與題號、不含答案：老師頁常投影給全班看。
 */
export function feedEvents(prev: TeacherView | null, next: TeacherView): FeedEvent[] {
  if (prev === null || next.phase !== "answering") return [];
  const classic = (next.mode?.key ?? "classic") === "classic";
  const events: FeedEvent[] = [];
  for (const q of next.board) {
    const before = prev.board.find((p) => p.number === q.number);
    for (const r of q.ranking) {
      if (before?.ranking.some((b) => b.team === r.team)) continue;
      events.push({
        key: `${q.number}-${r.team}`,
        text: classic && r.rank === 1 ? `${r.team} 搶下第 ${q.number} 題！` : `${r.team} 送出第 ${q.number} 題`,
      });
    }
  }
  return events;
}

// 老師頁右上角跳出即時搶答快訊；不改畫面其他部分
export function useLiveFeed(view: TeacherView | null, connected = true) {
  const { notification } = App.useApp();
  const prev = useRef<TeacherView | null>(null);
  // 斷線當下手上的 view：重連時 connected 先轉回 true、view 仍是這份舊的，不能拿它當新基準
  const stale = useRef<TeacherView | null>(null);
  useEffect(() => {
    // 斷線即清基準：重連後收到的第一個新 view 重新當基準。斷線期間的送出不補跳（作答狀況表仍完整）；
    // 伺服器重啟後新一輪的同組同題也不會被舊基準吞掉。
    if (!connected) {
      prev.current = null;
      stale.current = view;
      return;
    }
    if (view === null || view === stale.current) return;
    stale.current = null;
    for (const e of feedEvents(prev.current, view)) {
      notification.open({ key: e.key, message: e.text, placement: "topRight", duration: 3 });
    }
    prev.current = view;
  }, [view, connected, notification]);
}
