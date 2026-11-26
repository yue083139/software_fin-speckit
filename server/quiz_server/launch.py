"""啟動後自動開老師頁（easy-setup D1）。

成敗只看 `webbrowser.open` 的回傳值：探針（probes/results/2026-11-26-easy-setup.txt ①）在本機
`webbrowser.get().name` 為空字串、`open` 仍回 True 並開啟，故不以瀏覽器名稱判斷；
回 False 或拋例外時只靠終端機網址。
"""
import time
import webbrowser
from collections.abc import Callable, Mapping

NO_BROWSER_HINT = "沒有自動開啟瀏覽器，請手動開上面的老師頁網址。"


def should_open(no_browser: bool, env: Mapping[str, str]) -> bool:
    """`--no-browser`、`QUIZ_NO_BROWSER=1`、`CI` 非空任一即不開（CI 與無頭環境不該彈出瀏覽器）。"""
    return not (no_browser or env.get("QUIZ_NO_BROWSER") == "1" or env.get("CI"))


def open_when_ready(is_started: Callable[[], bool], url: str,
                    opener: Callable[[str], bool] = webbrowser.open, timeout: float = 30,
                    interval: float = 0.1, sleep: Callable[[float], None] = time.sleep,
                    now: Callable[[], float] = time.monotonic) -> bool:
    deadline = now() + timeout
    while not is_started():
        if now() > deadline:
            return False
        sleep(interval)
    try:
        ok = bool(opener(url))
    except Exception:  # 無桌面、找不到瀏覽器等：不影響伺服器，退回終端機網址
        ok = False
    if not ok:
        print(NO_BROWSER_HINT, flush=True)
    return ok
