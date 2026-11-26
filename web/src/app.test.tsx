import { act, render, screen, waitFor } from "@testing-library/react";
import App from "./App";
import { TEACHER_KEY_STORE } from "./route";

// teacher-key-hidden 架構通道藥方：takeTeacherKey 在載入與 hashchange 時直接執行；金鑰一換老師頁重新掛載
describe("App 老師頁金鑰", () => {
  const realFetch = globalThis.fetch;
  const RealWS = globalThis.WebSocket;
  let good = "good";
  beforeEach(() => {
    sessionStorage.clear();
    globalThis.fetch = (async (_url: RequestInfo | URL, init?: RequestInit) => {
      const key = new Headers(init?.headers).get("X-Teacher-Key");
      return key === good
        ? new Response(JSON.stringify({ configured: false, signed_in: false, email: null }), { status: 200 })
        : new Response(JSON.stringify({ detail: "需要老師金鑰" }), { status: 401 });
    }) as typeof fetch;
    class FakeWS {
      onclose: unknown = null;
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
    history.replaceState(null, "", "/");
  });

  async function paste(url: string) {
    await act(async () => {
      location.hash = url;
    });
  }

  it("同分頁重貼同一網址，金鑰仍自網址移除", async () => {
    history.replaceState(null, "", "/#/teacher?key=good");
    render(<App />);
    expect(location.hash).toBe("#/teacher");
    await paste("#/teacher?key=good");
    await waitFor(() => expect(location.hash).toBe("#/teacher"));
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBe("good");
  });

  it("先貼錯金鑰、再貼正確網址，錯誤頁消失", async () => {
    history.replaceState(null, "", "/#/teacher?key=bad");
    render(<App />);
    await waitFor(() => expect(screen.getByText("老師金鑰錯誤")).toBeInTheDocument());
    good = "good";
    await paste("#/teacher?key=good");
    await waitFor(() => expect(screen.queryByText("老師金鑰錯誤")).toBeNull());
    expect(location.hash).toBe("#/teacher");
  });
});
