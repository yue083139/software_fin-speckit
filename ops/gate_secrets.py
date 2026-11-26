"""門禁：倉內不得出現真憑證形狀的字串（CLAUDE.md 基本紀律「真實資料不入庫」）。

夾具用「前綴字面量＋0×n」放行（如 AKIA 後接 16 個 0）；只要主體不是全 0 就當真憑證。
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _files import UNDECODABLE, read_utf8, tracked_text_files  # noqa: E402

PATTERNS = {
    "OpenAI/Anthropic 金鑰": re.compile(r"sk-(?:proj-|ant-[a-z0-9]+-)?([A-Za-z0-9_\-]{20,})"),
    "AWS 存取金鑰": re.compile(r"AKIA([0-9A-Z]{16})"),
    "Google API 金鑰": re.compile(r"AIza([0-9A-Za-z_\-]{35})"),
    "GitHub 權杖": re.compile(r"gh[pousr]_([A-Za-z0-9]{36})"),
    # guided-notes-sheets-sync D6：Google OAuth 用戶端密鑰、access token、refresh token
    "Google OAuth 用戶端密鑰": re.compile(r"GOCSPX-([A-Za-z0-9_\-]{20,})"),
    "Google access token": re.compile(r"ya29\.([A-Za-z0-9_\-]{20,})"),
    # 前一字元不可是英數、「/」「:」「.」：避開 http://127.0.0.1// 這類網址
    "Google refresh token": re.compile(r"(?<![\w/:.])1//([A-Za-z0-9_\-]{20,})"),
    "私鑰": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |)PRIVATE KEY-----()"),
}


def _is_fixture(body: str) -> bool:
    core = body.replace("-", "").replace("_", "")
    return bool(core) and set(core) == {"0"}


def scan(root: Path) -> list[str]:
    hits = []
    for path in tracked_text_files(root):
        text = read_utf8(path)
        if text is None:
            hits.append(f"{path.relative_to(root).as_posix()}: {UNDECODABLE}")
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for name, pat in PATTERNS.items():
                for m in pat.finditer(line):
                    if not _is_fixture(m.group(1)):
                        # 不印出命中字串本身，避免門禁輸出把真金鑰再散播到 CI 日誌
                        hits.append(f"{path.relative_to(root).as_posix()}:{n}: {name}形狀")
    return hits


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    hits = scan(root)
    for h in hits:
        print(h)
    print(f"gate-secrets: {len(hits)} findings")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
