"""啟動：python -m quiz_server [--host 127.0.0.1] [--port 8000] [--tunnel] [--no-browser]。"""
import argparse
import os
import sys
import threading

import uvicorn

from .app import create_app, resolve_teacher_key
from .envfile import load_env
from .launch import open_when_ready, should_open
from .tunnel import Tunnel


def start_browser(server: uvicorn.Server, url: str) -> None:
    """就緒後開老師頁一次（easy-setup D1）；背景執行緒，不擋伺服器啟動。"""
    threading.Thread(target=open_when_ready, args=(lambda: server.started, url), daemon=True).start()


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(description="課堂搶答系統伺服器（僅供本機）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--tunnel", action="store_true",
                    help="啟動時就以 Cloudflare 快速通道取得公開網址（亦可設 QUIZ_TUNNEL=1；"
                         "平常在老師頁按「開啟手機連線」即可）")
    ap.add_argument("--no-browser", action="store_true",
                    help="不要自動開老師頁（亦可設 QUIZ_NO_BROWSER=1）")
    a = ap.parse_args(argv)
    load_env()
    key = resolve_teacher_key()
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    # 老師頁一律用 127.0.0.1：`--host 0.0.0.0` 時 base 不是可開的網址，且老師端點只接受本機 Host
    base = f"http://127.0.0.1:{a.port}"
    teacher_url = f"{base}/#/teacher?key={key}"
    # 同一個實例注入 app：老師頁的開關與 `--tunnel` 啟動時開的通道是同一條（easy-setup v1.1 藥方 1）
    tunnel = Tunnel(a.port)
    student_url = None
    if a.tunnel or os.environ.get("QUIZ_TUNNEL") == "1":
        print("正在建立 Cloudflare 快速通道（約 5 秒）…", flush=True)
        student_url = tunnel.start()
        if student_url is None:
            print("無法建立通道（找不到 cloudflared 或逾時）：改為只在本機開啟。"
                  "安裝：winget install --id Cloudflare.cloudflared -e", flush=True)
    print(f"老師頁（只能在本機開啟）：{teacher_url}", flush=True)
    print(f"學生頁：{base}/", flush=True)
    if student_url:
        print(f"學生頁（手機掃老師頁的 QR code，或直接開）：{student_url}", flush=True)
        print("新通道網址約需 1 分鐘才連得上；每次啟動網址都會不同。", flush=True)
    try:
        # uvicorn 在 INFO 等級會印出含查詢字串的 WebSocket 接受紀錄（含老師金鑰與組別憑證）；
        # 它不屬存取日誌，access_log=False 擋不到（真棧探針 2026-11-11 實證），故只留 warning 以上
        app = create_app(teacher_key=key, student_url=student_url, tunnel=tunnel)
        server = uvicorn.Server(uvicorn.Config(app, host=a.host, port=a.port,
                                               log_level="warning", access_log=False))
        if should_open(a.no_browser, os.environ):
            start_browser(server, teacher_url)
        server.run()
    finally:
        tunnel.stop()


if __name__ == "__main__":
    main()
