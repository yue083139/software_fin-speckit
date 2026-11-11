import { useEffect, useState } from "react";
import { parseRoute } from "./route";
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
  if (route.page === "teacher") return <Teacher teacherKey={route.params.get("key") ?? ""} />;
  if (route.page === "student") return <Student token={loadToken()} />;
  return <Home />;
}
