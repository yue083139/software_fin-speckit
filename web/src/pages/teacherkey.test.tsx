import { render, screen, waitFor } from "@testing-library/react";
import Teacher from "./Teacher";
import { TEACHER_KEY_STORE } from "../route";

// teacher-key-hidden：金鑰錯誤（REST 401）時清掉 sessionStorage 並顯示既有的金鑰錯誤提示
describe("老師金鑰錯誤", () => {
  const realFetch = globalThis.fetch;
  const RealWS = globalThis.WebSocket;
  beforeEach(() => {
    sessionStorage.setItem(TEACHER_KEY_STORE, "wrong");
    globalThis.fetch = (async () =>
      new Response(JSON.stringify({ detail: "老師金鑰錯誤" }), { status: 401 })) as typeof fetch;
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

  it("401 ⇒ 清除 sessionStorage 並顯示請回首頁重新輸入", async () => {
    render(<Teacher teacherKey="wrong" />);
    await waitFor(() => expect(screen.getByText("老師金鑰錯誤，請回首頁重新輸入。")).toBeInTheDocument());
    expect(sessionStorage.getItem(TEACHER_KEY_STORE)).toBeNull();
  });
});
