"""PlantUML 轉檔與語法檢查（憲章原則 VII）。

有 Java ⇒ `java -jar .tools/plantuml-<版本>.jar`（憲章指定做法，jar 不在則自動下載指定版本）；
無 Java ⇒ 退用同版本 Docker 映像 `plantuml/plantuml:<版本>`。兩者皆無 ⇒ 退出碼 2 並說明，不得當作通過。

用法：python ops/diagrams.py render|check [根目錄]
"""
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

VERSION = "1.2026.9"
JAR_URL = f"https://github.com/plantuml/plantuml/releases/download/v{VERSION}/plantuml-{VERSION}.jar"


def _jar(root: Path) -> Path:
    jar = root / ".tools" / f"plantuml-{VERSION}.jar"
    if not jar.is_file():
        jar.parent.mkdir(parents=True, exist_ok=True)
        print(f"下載 {JAR_URL}")
        urllib.request.urlretrieve(JAR_URL, jar)  # noqa: S310  固定 https 網址
    return jar


def command(root: Path, mode_flag: str, files: list[Path]) -> list[str] | None:
    if shutil.which("java"):
        return ["java", "-jar", str(_jar(root)), "-charset", "UTF-8", mode_flag, *map(str, files)]
    if shutil.which("docker"):
        rels = [f"/data/{f.relative_to(root / 'diagrams').as_posix()}" for f in files]
        return ["docker", "run", "--rm", "-v", f"{(root / 'diagrams').resolve()}:/data",
                f"plantuml/plantuml:{VERSION}", "-charset", "UTF-8", mode_flag, *rels]
    return None


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "check"
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    files = sorted((root / "diagrams").glob("**/*.puml"))
    name = "diagrams" if mode == "render" else "gate-diagrams-syntax"
    if not files:
        print(f"{name}: 0 個圖檔")
        return 0
    cmd = command(root, "-tpng" if mode == "render" else "-checkonly", files)
    if cmd is None:
        print(f"{name}: 未跑——找不到 java 或 docker（安裝 JRE 21 或 Docker 後重跑）")
        return 2
    rc = subprocess.run(cmd, check=False).returncode
    verb = "已轉 PNG" if mode == "render" else "語法通過"
    print(f"{name}: {len(files)} 個圖檔{verb if rc == 0 else f'失敗（退出碼 {rc}）'}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
