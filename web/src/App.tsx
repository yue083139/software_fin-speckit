import { useEffect, useMemo, useState } from "react";
import { parseRoute, takeTeacherKey } from "./route";
import Home from "./pages/Home";
import Teacher from "./pages/Teacher";
import Student from "./pages/Student";
import { loadToken } from "./api";

export default function App() {
  const [hash, setHash] = useState(location.hash);
  useEffect(() => {
    const on = () => setHash(location.hash);
    window.addEventListener("hashchange", on);
    return () => window.removeEventListener("hashchange", on);
  }, []);
  const route = parseRoute(hash);
  // 網址帶 key 時取出並自網址移除；之後（含重新整理）從本分頁 sessionStorage 取
  const teacherKey = useMemo(() => (route.page === "teacher" ? takeTeacherKey() : ""), [hash]); // eslint-disable-line react-hooks/exhaustive-deps
  if (route.page === "teacher") return <Teacher teacherKey={teacherKey} />;
  if (route.page === "student") return <Student token={loadToken()} />;
  return <Home />;
}
