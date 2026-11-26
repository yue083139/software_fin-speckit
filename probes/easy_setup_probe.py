"""easy-setup 探針（准入③）：①uv 子行程內 webbrowser.open 能否開預設瀏覽器 ②執行期起停 cloudflared 多次不殘留。

用法（負責人本機執行；會開一個瀏覽器分頁、並連 Cloudflare 建立快速通道約 5 秒／次）：
  uv run --project server python -X utf8 probes/easy_setup_probe.py --browser-url http://127.0.0.1:8000/ --cycles 3
原樣輸出存 probes/results/<日期>-easy-setup.txt（通道網址已遮蔽）。
"""
import argparse
import http.server
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "server"))
from quiz_server.tunnel import Tunnel, find_cloudflared  # noqa: E402


def count_cloudflared() -> int:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq cloudflared.exe", "/FO", "CSV", "/NH"],  # noqa: S603,S607
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
    return sum(1 for line in out.splitlines() if line.lower().startswith('"cloudflared.exe"'))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--browser-url", default="")
    ap.add_argument("--cycles", type=int, default=3)
    a = ap.parse_args()
    print("指令：uv run --project server python -X utf8 probes/easy_setup_probe.py "
          f"--browser-url {a.browser_url or '(略過)'} --cycles {a.cycles}")
    if a.browser_url:
        try:
            name = webbrowser.get().name
        except webbrowser.Error as e:
            name = f"(get 失敗：{e})"
        print(f"① webbrowser.get().name：{name}")
        print(f"① webbrowser.open 回傳：{webbrowser.open(a.browser_url)}")
    print(f"② find_cloudflared：{find_cloudflared()}")
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), http.server.SimpleHTTPRequestHandler)
    port = srv.server_address[1]
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = count_cloudflared()
    print(f"② 起始 cloudflared 行程數（含既有）：{base}")
    for i in range(1, a.cycles + 1):
        t = Tunnel(port)
        t0 = time.monotonic()
        url = t.start(timeout=30)
        took = time.monotonic() - t0
        running = count_cloudflared()
        t.stop()
        time.sleep(1)
        after = count_cloudflared()
        shown = "取得 https://<遮蔽>.trycloudflare.com/" if url else "None"
        print(f"② 第 {i} 次：start {took:.1f} 秒 → {shown}；執行中 {running}；stop 後 {after}（基準 {base}）")
    srv.shutdown()
    print(f"② 結束 cloudflared 行程數：{count_cloudflared()}（基準 {base}）")


if __name__ == "__main__":
    main()
