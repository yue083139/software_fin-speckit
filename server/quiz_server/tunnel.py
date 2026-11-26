"""Cloudflare 快速通道（student-qr D1）：讓手機以公開 https 網址連到學生頁。

只在 `--tunnel` 或 `QUIZ_TUNNEL=1` 時啟動；找不到 cloudflared 或逾時拿不到網址 ⇒ 回 None，伺服器照常只開本機。
通道網址每次啟動都不同；DNS 生效約需數十秒（探針 2026-11-26：第 31 次、約 60 秒後才連得上）。
"""
import re
import shutil
import subprocess
import threading
import time
from pathlib import Path
from typing import IO

# 只認 INF 等級的表框列，且排除 cloudflared 自己的 API 網域（實作輪對抗評審）
URL = re.compile(r"(?:^|\s)INF \|\s+(https://(?!api\.)[a-z0-9-]+\.trycloudflare\.com)\s+\|")
# winget 安裝後要重開終端機 PATH 才更新；先找 PATH，再找預設安裝位置
KNOWN_PATHS = (Path(r"C:\Program Files (x86)\cloudflared\cloudflared.exe"),
               Path(r"C:\Program Files\cloudflared\cloudflared.exe"))


def find_cloudflared() -> str | None:
    found = shutil.which("cloudflared")
    if found:
        return found
    return next((str(p) for p in KNOWN_PATHS if p.is_file()), None)


def parse_url(line: str) -> str | None:
    """cloudflared 把網址印在一個表框列裡（`INF |  https://….trycloudflare.com  |`）；只認這種列。"""
    m = URL.search(line)
    return m.group(1) + "/" if m else None


def wait_for_url(stream: IO[str], timeout: float) -> str | None:
    deadline = time.monotonic() + timeout
    for line in stream:
        url = parse_url(line)
        if url:
            return url
        if time.monotonic() > deadline:
            return None
    return None


class Tunnel:
    def __init__(self, port: int) -> None:
        self.port = port
        self.proc: subprocess.Popen[str] | None = None

    def start(self, timeout: float = 30) -> str | None:
        exe = find_cloudflared()
        if exe is None:
            return None
        # 執行檔來自 PATH 或固定安裝路徑、參數全為常數與整數埠，不含外部輸入
        self.proc = subprocess.Popen(  # noqa: S603
            [exe, "tunnel", "--no-autoupdate", "--url", f"http://127.0.0.1:{self.port}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
            text=True, encoding="utf-8", errors="replace")
        assert self.proc.stdout is not None
        stream = self.proc.stdout
        result: list[str | None] = [None]

        def read() -> None:
            result[0] = wait_for_url(stream, timeout)

        reader = threading.Thread(target=read, daemon=True)
        reader.start()
        reader.join(timeout)
        if result[0] is None:
            self.stop()
            return None
        # 之後持續讀掉輸出，避免管線塞滿讓 cloudflared 卡住；內容不印（含連線細節）
        threading.Thread(target=lambda: [None for _ in stream], daemon=True).start()
        return result[0]

    def stop(self) -> None:
        if self.proc is None or self.proc.poll() is not None:
            return
        self.proc.terminate()
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
