"""門禁共用：列出受檢檔案。含未追蹤但未被忽略的新檔，避免「還沒 git add 就漏檢」。"""
import subprocess
from pathlib import Path

BINARY_SUFFIXES = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".woff", ".woff2", ".lock", ".xlsx", ".jar",
}


def tracked_text_files(root: Path) -> list[Path]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z"],
        check=True, capture_output=True,
    ).stdout.decode("utf-8")
    files = []
    for rel in filter(None, out.split("\0")):
        p = root / rel
        if p.suffix.lower() in BINARY_SUFFIXES or not p.is_file():
            continue
        files.append(p)
    return files


UNDECODABLE = (
    "無法以 UTF-8 解碼或含 NUL 位元組，門禁無法檢查其內容"
    "（本倉文字檔一律 UTF-8，二進位檔請加副檔名至 BINARY_SUFFIXES）"
)


def read_utf8(path: Path) -> str | None:
    """回傳內容；非 UTF-8 回 None，由呼叫方計為紅。

    不可靜默跳過：Windows PowerShell 5 以 `>` 寫檔預設 UTF-16，跳過即讓檔內金鑰與簡體字假綠。
    含 NUL 也回 None：無 BOM 的 UTF-16LE 恰是合法 UTF-8（ASCII 與 NUL 交錯），解碼不會失敗，
    但金鑰被 NUL 隔開、正則比對不到。
    """
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return None
    return None if "\x00" in text else text
