"""repo 根目錄 `.env` 的讀寫（easy-setup D2；guided-notes-sheets-sync D1 的 `load_env` 同一規則）。

只改指定鍵：同鍵第一行換成新值、其後同鍵行刪除（`load_env` 取第一行，留著後面的行會讓兩邊語意分岔），
其他行（註解、其他鍵、空行）原樣保留。路徑由呼叫端注入，正式碼固定 `ENV_FILE`，不接受請求指定。
值由呼叫端先以白名單驗證；本模組不做跳脫，寫入的就是傳入的原值。
"""
import os
import re
import secrets
from collections.abc import Iterable, Mapping
from pathlib import Path

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"
ENV_LINE = re.compile(r"^\s*([A-Z][A-Z0-9_]*)\s*=\s*(.*?)\s*$")


def read_lines(path: Path) -> list[str]:
    # utf-8-sig：Windows 編輯器存的 .env 可能帶 BOM，否則第一個變數會被略過
    #（guided-notes-sheets-sync 實作輪評審）
    return path.read_text(encoding="utf-8-sig").splitlines() if path.is_file() else []


def _key(line: str) -> str | None:
    m = ENV_LINE.match(line)
    return m.group(1) if m else None


def _write(path: Path, lines: list[str]) -> None:
    # 同目錄暫存檔＋os.replace：寫到一半中斷也不會留下半截 .env；`.env.tmp-*` 由 .gitignore 的 `.env.*` 涵蓋
    tmp = path.with_name(f"{path.name}.tmp-{secrets.token_hex(6)}")
    try:
        tmp.write_text("".join(line + "\n" for line in lines), encoding="utf-8")
        os.replace(tmp, path)
    finally:
        if tmp.exists():
            tmp.unlink()


def write_keys(values: Mapping[str, str], path: Path = ENV_FILE) -> None:
    out: list[str] = []
    done: set[str] = set()
    for line in read_lines(path):
        key = _key(line)
        if key in values:
            if key not in done:
                out.append(f"{key}={values[key]}")
                done.add(key)
            continue
        out.append(line)
    out.extend(f"{k}={v}" for k, v in values.items() if k not in done)
    _write(path, out)


def remove_keys(keys: Iterable[str], path: Path = ENV_FILE) -> None:
    if not path.is_file():
        return
    drop = set(keys)
    _write(path, [line for line in read_lines(path) if _key(line) not in drop])


def load_env(path: Path = ENV_FILE) -> None:
    """讀 `.env` 設進環境變數；不覆蓋既有環境變數（guided-notes-sheets-sync D1）。"""
    for line in read_lines(path):
        m = ENV_LINE.match(line)
        if m and m.group(1) not in os.environ:
            os.environ[m.group(1)] = m.group(2).strip('"').strip("'")
