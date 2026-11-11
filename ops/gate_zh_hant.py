"""門禁：倉內文字不得含簡體專用字（CLAUDE.md「全專案一律使用繁體中文」）。

只收「簡體專用、繁體不用」的字；簡繁同形或繁體另有用法的字（如 于、后、里、并、准）刻意不收，
寧可漏抓也不誤報——誤報會讓人習慣性加豁免，閘就廢了。
需要刻意引用簡體的行（如本閘的負例）在該行加 `zh-hant: allow`。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _files import UNDECODABLE, read_utf8, tracked_text_files  # noqa: E402

SIMPLIFIED_ONLY = set("这们说时为国门发实现设计验证对话务开关问题个来还经过让应该统规则级录权险数输处档审评环测试线层断从与将")  # noqa: E501  zh-hant: allow
ALLOW_MARK = "zh-hant: allow"


def scan(root: Path) -> list[str]:
    hits = []
    for path in tracked_text_files(root):
        text = read_utf8(path)
        if text is None:
            hits.append(f"{path.relative_to(root).as_posix()}: {UNDECODABLE}")
            continue
        for n, line in enumerate(text.splitlines(), 1):
            if ALLOW_MARK in line:
                continue
            bad = sorted({c for c in line if c in SIMPLIFIED_ONLY})
            if bad:
                hits.append(f"{path.relative_to(root).as_posix()}:{n}: 簡體字 {''.join(bad)}")
    return hits


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    hits = scan(root)
    for h in hits:
        print(h)
    print(f"gate-zh-hant: {len(hits)} 處簡體字")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
