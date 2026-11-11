"""門禁：Spec Kit 憲章已填妥（無範本佔位符、有版本列、含圖表優先原則）。

評分檢驗 constitution；範本佔位符（如 [PRINCIPLE_1_NAME]）殘留或原則 VII 被刪，即視同憲章未完成。

用法：python ops/gate_speckit.py [根目錄]
"""
import re
import sys
from pathlib import Path

CONSTITUTION = ".specify/memory/constitution.md"
PLACEHOLDER = re.compile(r"\[[A-Z][A-Z_0-9]+\]")
VERSION = re.compile(r"^\*\*Version\*\*: (\d+\.\d+\.\d+)", re.M)
REQUIRED = ["PlantUML 設計優先", "./diagrams/", "speckit.implement"]


def scan(root: Path) -> tuple[list[str], str | None]:
    path = root / CONSTITUTION
    if not path.is_file():
        return [f"{CONSTITUTION}: 缺檔"], None
    text = path.read_text(encoding="utf-8")
    problems = []
    for n, line in enumerate(text.splitlines(), 1):
        for m in PLACEHOLDER.finditer(line):
            problems.append(f"{CONSTITUTION}:{n}: 範本佔位符 {m.group(0)}")
    v = VERSION.search(text)
    if not v:
        problems.append(f"{CONSTITUTION}: 缺 **Version**: X.Y.Z 版本列")
    for needle in REQUIRED:
        if needle not in text:
            problems.append(f"{CONSTITUTION}: 缺圖表優先原則要素「{needle}」")
    return problems, v.group(1) if v else None


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    problems, version = scan(root)
    for p in problems:
        print(p)
    print(f"gate-speckit: 憲章 v{version or '?'}，{len(problems)} 處問題")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
