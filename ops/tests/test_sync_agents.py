"""Codex 規範同步門禁的負例：AGENTS.md 與 CLAUDE.md 一漂移就紅（卡 codex-parity）。"""
import subprocess
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))

import sync_agents  # noqa: E402

SKILL = "---\nname: review-dispatch\ndescription: 派評審骨架\n---\n\n# 派單定式\n"


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "CLAUDE.md").write_text("# 總綱\n紀律一\n", encoding="utf-8")
    (tmp_path / "svc").mkdir()
    (tmp_path / "svc" / "CLAUDE.md").write_text("# 元件\n規範\n", encoding="utf-8")
    skill = tmp_path / ".claude" / "skills" / "review-dispatch"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(SKILL, encoding="utf-8")
    return tmp_path


def test_missing_generated_files_are_red(repo: Path):
    problems = sync_agents.check(repo)
    assert sorted(problems) == sorted([
        "AGENTS.md: 缺檔",
        "svc/AGENTS.md: 缺檔",
        ".agents/skills/review-dispatch/SKILL.md: 缺檔",
    ])


def test_write_then_check_is_green(repo: Path):
    sync_agents.write(repo)
    assert sync_agents.check(repo) == []


def test_hand_edit_of_generated_file_is_red(repo: Path):
    sync_agents.write(repo)
    p = repo / "svc" / "AGENTS.md"
    p.write_text(p.read_text(encoding="utf-8") + "手改一行\n", encoding="utf-8")
    assert sync_agents.check(repo) == ["svc/AGENTS.md: 與來源不一致，請改 CLAUDE.md 後執行 make sync-agents"]


def test_source_edit_without_regen_is_red(repo: Path):
    sync_agents.write(repo)
    (repo / "CLAUDE.md").write_text("# 總綱\n紀律一\n紀律二\n", encoding="utf-8")
    assert sync_agents.check(repo) == ["AGENTS.md: 與來源不一致，請改 CLAUDE.md 後執行 make sync-agents"]


def test_orphan_generated_file_is_red(repo: Path):
    sync_agents.write(repo)
    (repo / "svc" / "CLAUDE.md").unlink()
    assert sync_agents.check(repo) == ["svc/AGENTS.md: 來源 CLAUDE.md 已不存在，請刪除產生物"]


def test_only_root_agents_md_carries_codex_appendix(repo: Path):
    sync_agents.write(repo)
    root = (repo / "AGENTS.md").read_text(encoding="utf-8")
    sub = (repo / "svc" / "AGENTS.md").read_text(encoding="utf-8")
    marker = "## Codex 對應表"
    assert marker in root and marker not in sub
    assert "紀律一" in root and "規範" in sub


def test_generated_skill_keeps_frontmatter_first(repo: Path):
    # Codex 只認以 --- 開頭的 SKILL.md frontmatter；產生物的註記不得插在 frontmatter 之前
    sync_agents.write(repo)
    text = (repo / ".agents" / "skills" / "review-dispatch" / "SKILL.md").read_text(encoding="utf-8")
    assert text.startswith("---\nname: review-dispatch\n")
