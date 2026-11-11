import { useEffect, useState } from "react";
import type { View } from "./types";

// 連上 /ws 並持續接收自己的 view；斷線每 1 秒重連（app-skeleton D4）。
export function useLiveView(query: string): { view: View | null; connected: boolean; closedCode: number | null } {
  const [view, setView] = useState<View | null>(null);
  const [connected, setConnected] = useState(false);
  const [closedCode, setClosedCode] = useState<number | null>(null);

  useEffect(() => {
    let socket: WebSocket | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let stopped = false;
    const connect = () => {
      const proto = location.protocol === "https:" ? "wss" : "ws";
      socket = new WebSocket(`${proto}://${location.host}/ws?${query}`);
      socket.onopen = () => setConnected(true);
      socket.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        if (msg.type === "state") setView(msg.view as View);
      };
      socket.onclose = (ev) => {
        setConnected(false);
        setClosedCode(ev.code);
        // 金鑰錯誤（4401）不重連，避免無限重試
        if (!stopped && ev.code !== 4401) timer = setTimeout(connect, 1000);
      };
    };
    connect();
    return () => {
      stopped = true;
      clearTimeout(timer);
      socket?.close();
    };
  }, [query]);

  return { view, connected, closedCode };
}
