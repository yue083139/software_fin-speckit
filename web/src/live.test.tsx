import { act, renderHook } from "@testing-library/react";
import { shouldReconnect, useLiveView } from "./live";

class FakeSocket {
  static all: FakeSocket[] = [];
  onopen: (() => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onclose: ((ev: { code: number }) => void) | null = null;
  constructor(public url: string) {
    FakeSocket.all.push(this);
  }
  close() {}
}

describe("useLiveView 重連（student-qr D2）", () => {
  const original = globalThis.WebSocket;
  beforeEach(() => {
    FakeSocket.all = [];
    vi.useFakeTimers();
    (globalThis as unknown as { WebSocket: unknown }).WebSocket = FakeSocket;
  });
  afterEach(() => {
    vi.useRealTimers();
    globalThis.WebSocket = original;
  });

  it("4401、4403 不重連；其他關閉碼重連", () => {
    expect(shouldReconnect(4401)).toBe(false);
    expect(shouldReconnect(4403)).toBe(false);
    expect(shouldReconnect(1006)).toBe(true);
  });

  it("收到 4403 後 5 秒內不再開新連線，且回報關閉碼", () => {
    const { result } = renderHook(() => useLiveView("role=teacher&key=k"));
    expect(FakeSocket.all).toHaveLength(1);
    act(() => FakeSocket.all[0].onclose?.({ code: 4403 }));
    act(() => vi.advanceTimersByTime(5000));
    expect(FakeSocket.all).toHaveLength(1);
    expect(result.current.closedCode).toBe(4403);
  });

  it("一般斷線（1006）1 秒後重連", () => {
    renderHook(() => useLiveView("role=student&token=t"));
    act(() => FakeSocket.all[0].onclose?.({ code: 1006 }));
    act(() => vi.advanceTimersByTime(1100));
    expect(FakeSocket.all).toHaveLength(2);
  });
});
