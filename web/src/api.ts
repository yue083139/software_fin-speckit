// REST 呼叫：老師端帶 X-Teacher-Key、學生端帶 X-Team-Token；錯誤一律轉成帶中文訊息的 Error。
export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

// 伺服器老師金鑰錯誤的 401 文案（server/quiz_server/app.py require_teacher）。
// 只有這個 401 才是金鑰錯；Google 未登入／過期同樣回 401，但不是金鑰問題（teacher-key-hidden 對抗通道藥方）
export const BAD_TEACHER_KEY_DETAIL = "需要老師金鑰";

export function isBadTeacherKey(e: unknown): boolean {
  return e instanceof ApiError && e.status === 401 && e.message === BAD_TEACHER_KEY_DETAIL;
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

export async function teacherDelete(path: string, key: string): Promise<unknown> {
  return parse(await fetch(`/api/teacher/${path}`, { method: "DELETE", headers: { "X-Teacher-Key": key } }));
}

export async function teacherUpload(key: string, file: File): Promise<unknown> {
  const form = new FormData();
  form.append("file", file);
  return parse(await fetch("/api/teacher/import", { method: "POST", headers: { "X-Teacher-Key": key }, body: form }));
}

export async function studentSubmit(token: string, question: number, answers: string[]): Promise<unknown> {
  return parse(await fetch("/api/student/submit", jsonInit({ "X-Team-Token": token }, { question, answers })));
}

// 老師金鑰在標頭，不能用一般連結下載；改以 fetch 取回檔案再觸發瀏覽器儲存
export async function teacherDownload(key: string): Promise<void> {
  const res = await fetch("/api/teacher/export", { headers: { "X-Teacher-Key": key } });
  if (!res.ok) {
    await parse(res);
    return;
  }
  const disposition = res.headers.get("content-disposition") ?? "";
  const match = /filename\*=UTF-8''([^;]+)/.exec(disposition);
  const name = match ? decodeURIComponent(match[1]) : "guided-notes-result.xlsx";
  const url = URL.createObjectURL(await res.blob());
  const a = document.createElement("a");
  a.href = url;
  a.download = name;
  a.click();
  URL.revokeObjectURL(url);
}

export interface PublicInfo {
  phase: string;
  teams: string[];
  joined: string[];
  team_play?: boolean;
}

export async function publicInfo(): Promise<PublicInfo> {
  return (await parse(await fetch("/api/public/info"))) as PublicInfo;
}

// 組隊時加入已有組員的組別要帶邀請碼（team-mode D2）
export async function joinTeam(team: string, code?: string): Promise<{ team: string; token: string }> {
  const body = code ? { team, code } : { team };
  return (await parse(await fetch("/api/student/join", jsonInit({}, body)))) as { team: string; token: string };
}

export async function studentDraft(token: string, question: number, answers: string[]): Promise<unknown> {
  return parse(await fetch("/api/student/draft", jsonInit({ "X-Team-Token": token }, { question, answers })));
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

// Google 帳號登入狀態（guided-notes-sheets-sync D1、D6）：權杖只在伺服器，前端只看得到是否登入與帳號
export interface GoogleStatus {
  configured: boolean;
  signed_in: boolean;
  email: string | null;
  client_id_hint?: string | null; // easy-setup：遮罩後的用戶端 ID；密鑰永不回傳
  redirect_uri?: string; // easy-setup：給設定精靈複製
}

// 手機連線（easy-setup D3）：伺服器即時起停 cloudflared，狀態也會經 WebSocket 推來
export interface TunnelResult {
  tunnel: TunnelState;
  student_url: string | null;
}

export type TunnelState = "off" | "starting" | "on";

export async function googleStatus(key: string): Promise<GoogleStatus> {
  return (await parse(await fetch("/api/teacher/google", { headers: { "X-Teacher-Key": key } }))) as GoogleStatus;
}
