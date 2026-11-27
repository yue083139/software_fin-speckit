import { App } from "antd";
import { useEffect, useRef } from "react";
import type { TeacherView } from "../types";

export interface FeedEvent {
  key: string;
  text: string;
}

/**
 * 比對前後兩次老師 view，列出新出現的送出（live-feed）。
 * 第一次收到 view（開頁、重連）只當基準不出通知，避免把已有的送出一次全跳出來；
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
export function useLiveFeed(view: TeacherView | null) {
  const { notification } = App.useApp();
  const prev = useRef<TeacherView | null>(null);
  useEffect(() => {
    if (view === null) return;
    for (const e of feedEvents(prev.current, view)) {
      notification.open({ key: e.key, message: e.text, placement: "topRight", duration: 3 });
    }
    prev.current = view;
  }, [view, notification]);
}
