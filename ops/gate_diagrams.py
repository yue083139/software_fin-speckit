"""門禁：每個 PlantUML 原檔都有同名 PNG（憲章原則 VII「圖表生成」、需求 P-04）。

只核「有沒有轉檔」，不核 PNG 是否為最新——不同平台字型不同，PNG 位元組無法跨平台比對；
語法正確性由 `make gate-diagrams-syntax`（PlantUML -checkonly，CI 必跑）負責，
圖碼一致由實作輪評審對照各功能 verification.md 的核對表負責。
另檢查 PNG 不早於 .puml 的最後修改提交，擋「改了圖忘了重轉」。

用法：python ops/gate_diagrams.py [根目錄]
"""
import subprocess
import sys
from pathlib import Path


def _commit_time(root: Path, rel: str) -> int | None:
    out = subprocess.run(
        ["git", "-C", str(root), "log", "-1", "--format=%ct", "--", rel],
        capture_output=True, text=True, check=False,
    ).stdout.strip()
    return int(out) if out else None


def scan(root: Path) -> list[str]:
    problems = []
    for puml in sorted((root / "diagrams").glob("**/*.puml")):
        rel = puml.relative_to(root).as_posix()
        png = puml.with_suffix(".png")
        if not png.is_file():
            problems.append(f"{rel}: 缺同名 PNG，請執行 make diagrams")
            continue
        t_puml = _commit_time(root, rel)
        t_png = _commit_time(root, png.relative_to(root).as_posix())
        if t_puml is not None and t_png is not None and t_png < t_puml:
            problems.append(f"{rel}: PNG 的最後提交早於原檔，請執行 make diagrams 並一併提交")
    for png in sorted((root / "diagrams").glob("**/*.png")):
        if not png.with_suffix(".puml").is_file():
            problems.append(f"{png.relative_to(root).as_posix()}: 孤兒 PNG（原檔已不存在）")
    return problems


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    problems = scan(root)
    for p in problems:
        print(p)
    n = len(list((root / "diagrams").glob("**/*.puml")))
    print(f"gate-diagrams: {n} 個圖檔，{len(problems)} 處問題")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
