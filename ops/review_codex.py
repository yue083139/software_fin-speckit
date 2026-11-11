"""以 Codex 起獨立評審會話（移植自 hybrid_agent）：Claude 的 finder-tail 子代理在 Codex 的對應做法。

提示詞＝.claude/agents/finder-tail-<通道>.md 本文（去 frontmatter）＋派單檔全文＋執行環境說明，
與 Claude 派單同一份骨架。評審在受評 HEAD 的一次性 git worktree 副本裡進行（`--sandbox workspace-write`），
評審員可在副本寫暫存檔、做變異實驗，真實工作樹不在可寫範圍——「禁改工作樹」由機制而非自律守；結束即刪副本。
回報寫到派單檔同目錄的 <派單檔名>.review-<通道>.md。

用法：python ops/review_codex.py <red|arch> <派單檔> [工作樹] [--codex <codex 執行檔>] [--dry-run]
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHANNELS = {"red": "finder-tail-red", "arch": "finder-tail-arch"}
_FRONTMATTER = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
PREFLIGHT_OK = "preflight-ok"


def venv_python(workdir: Path) -> Path | None:
    for rel in (".venv/Scripts/python.exe", ".venv/bin/python"):
        if (workdir / rel).is_file():
            return workdir / rel
    return None


def preflight(codex: str, py: Path) -> bool:
    # 實測直譯器在 Codex 沙箱內能否載入 pytest：Windows 上 Store 版 Python（WindowsApps 執行別名）與
    # uv 硬連結自快取的套件在沙箱內皆不可讀（codex-parity 實跑發現），不先測就會指派一條跑不起來的路
    probe = [codex, "sandbox", "--", str(py), "-B", "-c", f"import pytest; print('{PREFLIGHT_OK}')"]
    try:
        out = subprocess.run(probe, capture_output=True, text=True, encoding="utf-8", timeout=120)
    except (OSError, subprocess.TimeoutExpired):
        return False
    return PREFLIGHT_OK in out.stdout


def environment_notes(py: Path | None, usable: bool) -> str:
    if py is None or not usable:
        return (
            "## 執行環境\n\n"
            "本機 venv 在 Codex 沙箱內不可用：本次無法實跑測試與門禁，"
            "回報中每條須寫明「未實跑」，不得當作通過。"
            "（修法：在受評工作樹執行 `make codex-venv` 後重派。）\n"
        )
    return (
        "## 執行環境（由 ops/review_codex.py 附加）\n\n"
        "- 你的工作目錄是受評 HEAD 的一次性副本，可寫入、可做變異實驗；結束後即刪除。\n"
        f"- 不要用 uv、不要用裸 python；一律用 `{py}` 並加 `-B`。\n"
        f"- 跑 pytest 加 `-p no:cacheprovider`，例如 `{py} -B -m pytest -q -p no:cacheprovider ops/tests`。\n"
        f"- 門禁腳本直接執行，例如 `{py} -B ops/sync_agents.py --check .`。\n"
        "- 指令跑不起來時，回報中寫明哪一條「未實跑」與原樣錯誤，不得當作通過。\n"
    )


def build_prompt(channel: str, dispatch: Path, notes: str) -> str:
    agent = (ROOT / ".claude" / "agents" / f"{CHANNELS[channel]}.md").read_text(encoding="utf-8")
    body = _FRONTMATTER.sub("", agent, count=1)
    return f"{body.strip()}\n\n# 派單全文\n\n{dispatch.read_text(encoding='utf-8').strip()}\n\n{notes}"


def build_command(codex: str, workdir: Path, out: Path) -> list[str]:
    return [codex, "exec", "--sandbox", "workspace-write", "--ephemeral",
            "-C", str(workdir), "-o", str(out), "-"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("channel", choices=sorted(CHANNELS))
    ap.add_argument("dispatch", type=Path)
    ap.add_argument("workdir", type=Path, nargs="?", default=ROOT)
    ap.add_argument("--codex", default="codex")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    workdir = a.workdir.resolve()
    out = a.dispatch.resolve().with_name(f"{a.dispatch.stem}.review-{a.channel}.md")
    py = venv_python(workdir)
    usable = py is not None and (a.dry_run or preflight(a.codex, py))
    prompt = build_prompt(a.channel, a.dispatch, environment_notes(py, usable))
    base = Path(tempfile.gettempdir()) / "review-codex-dry-run" if a.dry_run else Path(
        tempfile.mkdtemp(prefix="review-codex-"))
    copy = base / "wt"
    cmd = build_command(a.codex, copy, out)
    if a.dry_run:
        print(" ".join(cmd))
        print(prompt)
        return 0
    subprocess.run(["git", "-C", str(workdir), "worktree", "add", "-q", "--detach", str(copy), "HEAD"],
                   check=True)
    try:
        tmp = copy / ".tmp"
        tmp.mkdir()
        env = {**os.environ, "TMP": str(tmp), "TEMP": str(tmp), "TMPDIR": str(tmp)}
        rc = subprocess.run(cmd, input=prompt, text=True, encoding="utf-8", env=env).returncode
    finally:
        subprocess.run(["git", "-C", str(workdir), "worktree", "remove", "--force", str(copy)], check=False)
    print(f"review-codex: 退出碼 {rc}，預檢 {'通過' if usable else '未過（評審未實跑）'}，回報 {out}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
