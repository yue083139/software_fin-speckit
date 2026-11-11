// 以 hash 路由：#/、#/teacher?key=…、#/student
export interface Route {
  page: "home" | "teacher" | "student";
  params: URLSearchParams;
}

export function parseRoute(hash: string): Route {
  const raw = hash.replace(/^#/, "");
  const [path, query = ""] = raw.split("?");
  const params = new URLSearchParams(query);
  if (path === "/teacher") return { page: "teacher", params };
  if (path === "/student") return { page: "student", params };
  return { page: "home", params };
}
