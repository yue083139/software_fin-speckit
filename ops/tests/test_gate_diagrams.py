"""圖表門禁的負例：缺 PNG、孤兒 PNG、改圖未重轉都要紅。"""
import subprocess
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))

import gate_diagrams  # noqa: E402

PUML = "@startuml\nA -> B\n@enduml\n"


def _git(repo: Path, *args: str, when: str | None = None) -> None:
    env = None
    if when:
        import os
        env = {**os.environ, "GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                    *args], check=True, capture_output=True, env=env)


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "diagrams").mkdir()
    return tmp_path


def test_empty_is_green(repo: Path):
    assert gate_diagrams.scan(repo) == []


def test_missing_png_is_red(repo: Path):
    (repo / "diagrams" / "001-x-class.puml").write_text(PUML, encoding="utf-8")
    assert gate_diagrams.scan(repo) == ["diagrams/001-x-class.puml: 缺同名 PNG，請執行 make diagrams"]


def test_paired_is_green(repo: Path):
    (repo / "diagrams" / "a.puml").write_text(PUML, encoding="utf-8")
    (repo / "diagrams" / "a.png").write_bytes(b"\x89PNG")
    assert gate_diagrams.scan(repo) == []


def test_orphan_png_is_red(repo: Path):
    (repo / "diagrams" / "a.png").write_bytes(b"\x89PNG")
    assert gate_diagrams.scan(repo) == ["diagrams/a.png: 孤兒 PNG（原檔已不存在）"]


def test_stale_png_is_red(repo: Path):
    d = repo / "diagrams"
    (d / "a.puml").write_text(PUML, encoding="utf-8")
    (d / "a.png").write_bytes(b"\x89PNG")
    _git(repo, "add", ".")
    _git(repo, "commit", "-qm", "init", when="2026-01-01T00:00:00")
    (d / "a.puml").write_text(PUML + "' 改圖\n", encoding="utf-8")
    _git(repo, "commit", "-qam", "edit", when="2026-01-02T00:00:00")
    assert gate_diagrams.scan(repo) == [
        "diagrams/a.puml: PNG 的最後提交早於原檔，請執行 make diagrams 並一併提交"
    ]
