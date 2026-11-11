"""由 Claude Code 規範產生 Codex 規範，並檢查兩者不漂移（卡 codex-parity）。

來源 → 產生物：
- 每份受版控的 CLAUDE.md → 同目錄 AGENTS.md（根目錄另附 ops/agents/codex-appendix.md）
- .claude/skills/review-dispatch/SKILL.md → .agents/skills/review-dispatch/SKILL.md
CLAUDE.md 是唯一真相來源；產生物手改即漂移，`--check` 判紅。

用法：python ops/sync_agents.py --write | --check [根目錄]
"""
import re
import subprocess
import sys
from pathlib import Path

OPS = Path(__file__).resolve().parent
APPENDIX = OPS / "agents" / "codex-appendix.md"
HEADER = "<!-- 由 ops/sync_agents.py 從 {src} 產生，勿手改；改來源後執行 make sync-agents -->\n"
SKILLS = [(".claude/skills/review-dispatch/SKILL.md", ".agents/skills/review-dispatch/SKILL.md")]


def _git_files(root: Path, pattern: str) -> list[str]:
    out = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "-z", "--", pattern],
        check=True, capture_output=True,
    ).stdout.decode("utf-8")
    return sorted(filter(None, out.split("\0")))


def _read(path: Path) -> str:
    # 一律正規化為 LF：Windows 工作樹可能是 CRLF、CI（Linux）是 LF，不正規化則同一來源兩地產物不同而假紅
    with path.open(encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---(\r?\n)", re.S)


def _with_header_after_frontmatter(text: str, src: str) -> str:
    # Codex 只認以 --- 開頭的 frontmatter；註記插在 frontmatter 之後，換行沿用來源（Windows 可能是 CRLF）
    m = _FRONTMATTER.match(text)
    if m:
        header = HEADER.format(src=src).replace("\n", m.group(1))
        return text[: m.end()] + header + text[m.end():]
    return HEADER.format(src=src) + text


def plan(root: Path) -> dict[str, str]:
    """產生物相對路徑 → 應有內容。"""
    out = {}
    for src in _git_files(root, "*CLAUDE.md"):
        if Path(src).name != "CLAUDE.md":
            continue
        dst = str(Path(src).with_name("AGENTS.md").as_posix())
        body = HEADER.format(src=src) + _read(root / src)
        if dst == "AGENTS.md":
            body += _read(APPENDIX)
        out[dst] = body
    for src, dst in SKILLS:
        if (root / src).is_file():
            out[dst] = _with_header_after_frontmatter(_read(root / src), src)
    return out


def check(root: Path) -> list[str]:
    expected = plan(root)
    problems = []
    for dst, body in expected.items():
        p = root / dst
        if not p.is_file():
            problems.append(f"{dst}: 缺檔")
        elif _read(p) != body:
            problems.append(f"{dst}: 與來源不一致，請改 CLAUDE.md 後執行 make sync-agents")
    # 產生物還在、來源已刪：以檔頭註記辨識，避免誤判使用者自寫的 AGENTS.md
    for dst in _git_files(root, "*AGENTS.md") + [d for _, d in SKILLS]:
        p = root / dst
        if dst not in expected and p.is_file() and "由 ops/sync_agents.py" in _read(p):
            problems.append(f"{dst}: 來源 CLAUDE.md 已不存在，請刪除產生物")
    return problems


def write(root: Path) -> None:
    for dst, body in plan(root).items():
        p = root / dst
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as f:
            f.write(body)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "--check"
    root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path.cwd()
    if mode == "--write":
        write(root)
    problems = check(root)
    for p in problems:
        print(p)
    print(f"gate-agents: {len(problems)} 處漂移")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
