// REST 呼叫：老師端帶 X-Teacher-Key、學生端帶 X-Team-Token；錯誤一律轉成帶中文訊息的 Error。
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function parse(res: Response): Promise<unknown> {
  const text = await res.text();
  let body: { detail?: unknown };
  try {
    body = text ? JSON.parse(text) : {};
  } catch {
    body = {};
  }
  if (!res.ok) {
    const detail = typeof body.detail === "string" ? body.detail : `請求失敗（${res.status}）`;
    throw new ApiError(res.status, detail);
  }
  return body;
}

function jsonInit(headers: Record<string, string>, body?: unknown): RequestInit {
  return {
    method: "POST",
    headers: body === undefined ? headers : { ...headers, "Content-Type": "application/json" },
    body: body === undefined ? undefined : JSON.stringify(body),
  };
}

export async function teacherPost(path: string, key: string, body?: unknown): Promise<unknown> {
  return parse(await fetch(`/api/teacher/${path}`, jsonInit({ "X-Teacher-Key": key }, body)));
}

export async function teacherUpload(key: string, file: File): Promise<unknown> {
  const form = new FormData();
  form.append("file", file);
  return parse(await fetch("/api/teacher/import", { method: "POST", headers: { "X-Teacher-Key": key }, body: form }));
}

export async function studentSubmit(token: string, question: number, answers: string[]): Promise<unknown> {
  return parse(await fetch("/api/student/submit", jsonInit({ "X-Team-Token": token }, { question, answers })));
}

export async function publicInfo(): Promise<{ phase: string; teams: string[]; joined: string[] }> {
  return (await parse(await fetch("/api/public/info"))) as { phase: string; teams: string[]; joined: string[] };
}

export async function joinTeam(team: string): Promise<{ team: string; token: string }> {
  return (await parse(await fetch("/api/student/join", jsonInit({}, { team })))) as { team: string; token: string };
}

// 組別憑證只放 sessionStorage：同分頁重新整理不必重新加入，關閉分頁即失效（app-skeleton D6）
const TOKEN_KEY = "quiz-team-token";

export function saveToken(token: string): void {
  try {
    sessionStorage.setItem(TOKEN_KEY, token);
  } catch {
    /* 無痕或封鎖儲存時仍可用到分頁關閉為止 */
  }
}

export function loadToken(): string {
  try {
    return sessionStorage.getItem(TOKEN_KEY) ?? "";
  } catch {
    return "";
  }
}
