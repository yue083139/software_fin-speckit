"""啟動：python -m quiz_server [--host 127.0.0.1] [--port 8000] [--tunnel]。"""
import argparse
import os
import re
import sys
from pathlib import Path

import uvicorn

from .app import create_app, resolve_teacher_key
from .tunnel import Tunnel

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
ENV_LINE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$")


def load_env(path: Path = ENV_FILE) -> None:
    """讀 repo 根目錄 `.env`（GOOGLE_CLIENT_ID 等）；不覆蓋既有環境變數（guided-notes-sheets-sync D1）。"""
    if not path.is_file():
        return
    # utf-8-sig：Windows 編輯器存的 .env 可能帶 BOM，否則第一個變數會被略過（實作輪評審）
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        m = ENV_LINE.match(line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2).strip('"').strip("'")


def main() -> None:
    ap = argparse.ArgumentParser(description="課堂搶答系統伺服器（僅供本機）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--tunnel", action="store_true",
                    help="以 Cloudflare 快速通道取得公開網址，讓手機掃 QR code 進學生頁"
                         "（亦可設 QUIZ_TUNNEL=1）")
    a = ap.parse_args()
    load_env()
    key = resolve_teacher_key()
    sys.stdout.reconfigure(encoding="utf-8")
    base = f"http://{a.host}:{a.port}"
    tunnel = Tunnel(a.port)
    student_url = None
    if a.tunnel or os.environ.get("QUIZ_TUNNEL") == "1":
        print("正在建立 Cloudflare 快速通道（約 5 秒）…", flush=True)
        student_url = tunnel.start()
        if student_url is None:
            print("無法建立通道（找不到 cloudflared 或逾時）：改為只在本機開啟。"
                  "安裝：winget install --id Cloudflare.cloudflared -e", flush=True)
    print(f"老師頁（只能在本機開啟）：{base}/#/teacher?key={key}", flush=True)
    print(f"學生頁：{base}/", flush=True)
    if student_url:
        print(f"學生頁（手機掃老師頁的 QR code，或直接開）：{student_url}", flush=True)
        print("新通道網址約需 1 分鐘才連得上；每次啟動網址都會不同。", flush=True)
    try:
        # uvicorn 在 INFO 等級會印出含查詢字串的 WebSocket 接受紀錄（含老師金鑰與組別憑證）；
        # 它不屬存取日誌，access_log=False 擋不到（真棧探針 2026-11-11 實證），故只留 warning 以上
        uvicorn.run(create_app(teacher_key=key, student_url=student_url), host=a.host, port=a.port,
                    log_level="warning", access_log=False)
    finally:
        tunnel.stop()


if __name__ == "__main__":
    main()
