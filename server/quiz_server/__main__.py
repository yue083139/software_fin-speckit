"""啟動：python -m quiz_server [--host 127.0.0.1] [--port 8000]。"""
import argparse
import sys

import uvicorn

from .app import create_app, resolve_teacher_key


def main() -> None:
    ap = argparse.ArgumentParser(description="課堂搶答系統伺服器（僅供本機）")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    key = resolve_teacher_key()
    sys.stdout.reconfigure(encoding="utf-8")
    base = f"http://{a.host}:{a.port}"
    print(f"老師頁：{base}/#/teacher?key={key}", flush=True)
    print(f"學生頁：{base}/", flush=True)
    # uvicorn 在 INFO 等級會印出含查詢字串的 WebSocket 接受紀錄（含老師金鑰與組別憑證）；
    # 它不屬存取日誌，access_log=False 擋不到（真棧探針 2026-11-11 實證），故只留 warning 以上
    uvicorn.run(create_app(teacher_key=key), host=a.host, port=a.port,
                log_level="warning", access_log=False)


if __name__ == "__main__":
    main()
