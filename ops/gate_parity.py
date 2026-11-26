"""門禁：兩組共用文件逐位元組一致（需求 P-03「兩組產出的系統功能要一致」）。

OpenSpec 組與 SpecKit 組各一個 repo，`SHARED` 內的檔案必須兩邊相同；一邊改了另一邊沒跟上即紅。
另一個 repo 不在本機（如 CI）時無從比對：印「未跑」並以退出碼 0 結束——**未跑不是綠**，
報都綠否時須寫「gate-parity 未跑」，合併前由負責人在本機帶 SIBLING 補跑。

用法：python ops/gate_parity.py [本 repo 根目錄] [另一 repo 根目錄]
"""
import sys
from pathlib import Path

SHARED = [
    "docs/requirements.md",
    "docs/parity.md",
    "docs/discipline-precedents.md",
    "docs/trd-game-modes.md",
    "docs/research/competitors.md",
    ".claude/agents/finder-tail-red.md",
    ".claude/agents/finder-tail-arch.md",
    ".claude/skills/review-dispatch/SKILL.md",
    "ops/gate_parity.py",
    "tests/fixtures/guided-notes/single.xlsx",
    "tests/fixtures/guided-notes/group.xlsx",
    "tests/fixtures/guided-notes/variant.xlsx",
    "tests/fixtures/guided-notes/reference.xlsx",
    "tests/fixtures/guided-notes/build_reference.py",
    "contracts/api.md",
]
SKIPPED = "gate-parity: 未跑（未提供另一 repo 路徑或路徑不存在）"


def _norm(data: bytes) -> bytes:
    # Windows 工作樹可能是 CRLF；比的是內容不是換行慣例
    return data.replace(b"\r\n", b"\n")


def compare(root: Path, sibling: Path) -> list[str]:
    problems = []
    for rel in SHARED:
        a, b = root / rel, sibling / rel
        if not a.is_file() or not b.is_file():
            missing = [str(p) for p in (a, b) if not p.is_file()]
            problems.append(f"{rel}: 缺檔（{'、'.join(missing)}）")
        elif _norm(a.read_bytes()) != _norm(b.read_bytes()):
            problems.append(f"{rel}: 兩組內容不一致")
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    sibling = Path(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2] else None
    if sibling is None or not sibling.is_dir():
        print(SKIPPED)
        return 0
    problems = compare(root, sibling)
    for p in problems:
        print(p)
    print(f"gate-parity: {len(problems)} 處不一致")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
