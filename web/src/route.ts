// 以 hash 路由：#/、#/teacher（首次帶 ?key=…，載入後即自網址移除）、#/student
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

// teacher-key-hidden：老師金鑰只經網址參數帶入，載入後自網址移除（網址列、瀏覽紀錄、螢幕分享不再露出），
// 存於本分頁 sessionStorage；不寫 localStorage 或 cookie。網址帶新 key 時以網址為準。
export const TEACHER_KEY_STORE = "qz_teacher_key";

export function takeTeacherKey(): string {
  const route = parseRoute(location.hash);
  const fromUrl = route.page === "teacher" ? route.params.get("key") : null;
  if (fromUrl !== null) {
    sessionStorage.setItem(TEACHER_KEY_STORE, fromUrl);
    route.params.delete("key");
    const rest = route.params.toString();
    history.replaceState(history.state, "", `${location.pathname}${location.search}#/teacher${rest ? `?${rest}` : ""}`);
    return fromUrl;
  }
  return sessionStorage.getItem(TEACHER_KEY_STORE) ?? "";
}

export function clearTeacherKey(): void {
  sessionStorage.removeItem(TEACHER_KEY_STORE);
}
