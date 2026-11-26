import { useEffect, useState } from "react";
import { parseRoute, takeTeacherKey } from "./route";
import Home from "./pages/Home";
import Teacher from "./pages/Teacher";
import Student from "./pages/Student";
import { loadToken } from "./api";

// teacher-key-hidden：在載入與每次 hashchange 時直接取金鑰（會以 replaceState 自網址移除 key），
// 再讀 replaceState 之後的 location.hash；不放在 render 裡算，否則同分頁重貼同一網址時 React 不重繪、key 留在網址列
function snapshot(): { hash: string; teacherKey: string } {
  const teacherKey = parseRoute(location.hash).page === "teacher" ? takeTeacherKey() : "";
  return { hash: location.hash, teacherKey };
}

export default function App() {
  const [snap, setSnap] = useState(snapshot);
  useEffect(() => {
    const on = () => setSnap(snapshot());
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  const route = parseRoute(snap.hash);
  // 金鑰一換就重新掛載老師頁：錯誤提示與 WebSocket 關閉碼不會沿用到新金鑰
  if (route.page === "teacher") return <Teacher key={snap.teacherKey} teacherKey={snap.teacherKey} />;
  if (route.page === "student") return <Student token={loadToken()} />;
  return <Home />;
}
