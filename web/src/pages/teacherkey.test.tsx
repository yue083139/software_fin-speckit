import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import Teacher from "./Teacher";
import { TEACHER_KEY_STORE } from "../route";

// teacher-key-hidden：金鑰錯誤（REST 401）時清掉 sessionStorage 並顯示既有的金鑰錯誤提示
describe("老師金鑰錯誤", () => {
  const realFetch = globalThis.fetch;
  const RealWS = globalThis.WebSocket;
  beforeEach(() => {
    sessionStorage.setItem(TEACHER_KEY_STORE, "wrong");
    globalThis.fetch = (async () =>
      new Response(JSON.stringify({ detail: "需要老師金鑰" }), { status: 401 })) as typeof fetch;
    class FakeWS {
      onclose: ((ev: { code: number }) => void) | null = null;
      onmessage: unknown = null;
      onopen: unknown = null;
      onerror: unknown = null;
      close() {}
      send() {}
    }
    (globalThis as unknown as { WebSocket: unknown }).WebSocket = FakeWS;
  });
  afterEach(() => {
    globalThis.fetch = realFetch;
    globalThis.WebSocket = RealWS;
    sessionStorage.clear();
  });

  it("401 ⇒ 清除 sessionStorage 並顯示整頁金鑰錯誤", async () => {
    render(<Teacher teacherKey="wrong" />);
    await waitFor(() => expect(screen.getByText("老師金鑰錯誤")).toBeInTheDocument());
    expect(screen.getByText(/終端機印出的完整老師頁網址重新開啟/)).toBeInTheDocument();
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBeNull();
  });
});

// 對抗通道藥方：只有「需要老師金鑰」的 401 才清金鑰；Google 401 照舊顯示訊息；兩個清除點各有測試
describe("金鑰清除點與 Google 401", () => {
  const realFetch = globalThis.fetch;
  const RealWS = globalThis.WebSocket;
  const endedView = {
    role: "teacher",
    phase: "ended",
    teams: ["第1組", "第2組"],
    joined: [],
    source: "測試學習單",
    questions: [],
    board: [],
    team_scores: {},
  };
  let closeWith: number | null = null;
  let exportReply: { status: number; detail: string } = { status: 401, detail: "請先以 Google 帳號登入" };

  beforeEach(() => {
    sessionStorage.setItem(TEACHER_KEY_STORE, "good");
    closeWith = null;
    globalThis.fetch = (async (url: RequestInfo | URL) => {
      if (String(url).includes("/api/teacher/google"))
        return new Response(JSON.stringify({ configured: true, signed_in: false, email: null }), { status: 200 });
      return new Response(JSON.stringify({ detail: exportReply.detail }), { status: exportReply.status });
    }) as typeof fetch;
    class FakeWS {
      onclose: ((ev: { code: number }) => void) | null = null;
      onmessage: ((ev: { data: string }) => void) | null = null;
      onopen: (() => void) | null = null;
      onerror: unknown = null;
      constructor() {
        setTimeout(() => {
          if (closeWith !== null) this.onclose?.({ code: closeWith });
          else this.onmessage?.({ data: JSON.stringify({ type: "state", seq: 1, view: endedView }) });
        }, 0);
      }
      close() {}
      send() {}
    }
    (globalThis as unknown as { WebSocket: unknown }).WebSocket = FakeWS;
  });
  afterEach(() => {
    globalThis.fetch = realFetch;
    globalThis.WebSocket = RealWS;
    sessionStorage.clear();
  });

  it("Google 401 不清金鑰、不跳金鑰錯誤頁，顯示 Google 訊息", async () => {
    exportReply = { status: 401, detail: "請先以 Google 帳號登入" };
    render(<Teacher teacherKey="good" />);
    const button = await screen.findByText("匯出到 Google 試算表");
    fireEvent.click(button.closest("button")!);
    await waitFor(() => expect(screen.getByText("請先以 Google 帳號登入")).toBeInTheDocument());
    expect(screen.queryByText("老師金鑰錯誤")).toBeNull();
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBe("good");
  });

  it("操作回「需要老師金鑰」401（Google 狀態 200）⇒ 清金鑰並顯示金鑰錯誤頁", async () => {
    exportReply = { status: 401, detail: "需要老師金鑰" };
    render(<Teacher teacherKey="good" />);
    const button = await screen.findByText("匯出到 Google 試算表");
    fireEvent.click(button.closest("button")!);
    await waitFor(() => expect(screen.getByText("老師金鑰錯誤")).toBeInTheDocument());
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBeNull();
  });

  it("WebSocket 4401 ⇒ 清金鑰並顯示金鑰錯誤頁", async () => {
    closeWith = 4401;
    render(<Teacher teacherKey="good" />);
    await waitFor(() => expect(screen.getByText("老師金鑰錯誤")).toBeInTheDocument());
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBeNull();
  });
});
