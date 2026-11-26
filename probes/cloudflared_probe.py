"""student-qr 探針：Cloudflare 快速通道的網址輸出行、轉送到本機的標頭、WebSocket 可否經通道。

用法：uv run --project server python -X utf8 probes/cloudflared_probe.py [cloudflared 路徑]
需本機已安裝 cloudflared；會向 Cloudflare 申請一條臨時 trycloudflare.com 通道，結束即關閉。
只回顯標頭名稱與 Host、client.host，不回顯其他標頭值（可能含來源 IP）。
"""
import asyncio
import re
import shutil
import subprocess
import sys
import threading
import time

import httpx
import uvicorn
import websockets
from fastapi import FastAPI, Request, WebSocket

PORT = 8020
URL = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")
app = FastAPI()


def _summary(host: str | None, client: str | None, headers) -> dict:
    names = sorted(k.lower() for k in headers.keys())
    if client and client not in ("127.0.0.1", "1.2.3.4"):  # 1.2.3.4＝對照組偽造值；其餘是真實公網 IP，不印
        client = "<公網 IP，已遮蔽>"
    return {"host": host, "client.host": client,
            "x-forwarded-for 存在": "x-forwarded-for" in names,
            "cf-connecting-ip 存在": "cf-connecting-ip" in names,
            "x-forwarded-host 存在": "x-forwarded-host" in names,
            "標頭名稱": names}


@app.get("/echo")
def echo(request: Request) -> dict:
    client = request.client.host if request.client else None
    return _summary(request.headers.get("host"), client, request.headers)


@app.websocket("/ws")
async def ws(socket: WebSocket) -> None:
    await socket.accept()
    await socket.send_json(_summary(socket.headers.get("host"),
                                    socket.client.host if socket.client else None, socket.headers))
    await socket.close()


def main() -> None:
    exe = sys.argv[1] if len(sys.argv) > 1 else shutil.which("cloudflared")
    print(f"cloudflared：{exe}")
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=PORT, log_level="warning"))
    threading.Thread(target=server.run, daemon=True).start()
    # 探針：執行檔由命令列指定，參數皆為常數
    proc = subprocess.Popen(  # noqa: S603
        [exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{PORT}"],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    public = None
    start = time.monotonic()
    assert proc.stdout is not None
    for line in proc.stdout:
        if URL.search(line):
            public = URL.search(line).group(0)
            print(f"① 含網址的輸出行（{time.monotonic() - start:.1f} 秒）：{line.rstrip()}")
            break
        if time.monotonic() - start > 60:
            break
    if not public:
        print("① 60 秒內沒拿到網址")
        proc.terminate()
        return
    threading.Thread(target=lambda: [None for _ in proc.stdout], daemon=True).start()  # 持續讀，避免管線塞滿
    for i in range(60):  # 新通道 DNS 生效需要幾十秒
        try:
            r = httpx.get(f"{public}/echo", timeout=10)
            if r.status_code == 200:
                print(f"② 經通道 GET /echo（第 {i + 1} 次嘗試）：{r.json()}")
                break
        except httpx.HTTPError as exc:
            last = exc
        time.sleep(2)
    else:
        print(f"② GET 失敗：{last!r}")
    forged = {"Host": "evil.example", "X-Forwarded-For": "1.2.3.4"}
    r = httpx.get(f"http://127.0.0.1:{PORT}/echo", headers=forged)
    print(f"② 對照：本機直連、偽造 Host 與 X-Forwarded-For：{r.json()}")

    async def ws_try() -> None:
        async with websockets.connect(public.replace("https://", "wss://") + "/ws", open_timeout=20) as s:
            print(f"③ 經通道 WebSocket：{await s.recv()}")

    try:
        asyncio.run(ws_try())
    except Exception as exc:  # 探針：任何失敗都照實印出
        print(f"③ WebSocket 失敗：{exc!r}")
    try:
        r = httpx.get(f"{public}/echo", headers={"Host": f"127.0.0.1:{PORT}"}, timeout=15)
        body = r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text[:120]
        print(f"④ 經通道偽造 Host: 127.0.0.1:{PORT}：HTTP {r.status_code}；{body}")
    except Exception as exc:  # 探針：任何失敗都照實印出
        print(f"④ 偽造 Host 失敗：{exc!r}")
    proc.terminate()
    proc.wait(timeout=10)
    print(f"通道已關閉（cloudflared 結束碼 {proc.returncode}）")
    server.should_exit = True


if __name__ == "__main__":
    main()
