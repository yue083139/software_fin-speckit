"""兩組共用文件門禁的負例：一邊改了另一邊沒跟上就紅。"""
import subprocess
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))

import gate_parity  # noqa: E402


def _populate(root: Path) -> Path:
    for rel in gate_parity.SHARED:
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(f"內容 {rel}\n".encode())
    return root


@pytest.fixture
def pair(tmp_path: Path) -> tuple[Path, Path]:
    return _populate(tmp_path / "a"), _populate(tmp_path / "b")


def test_identical_is_green(pair):
    assert gate_parity.compare(*pair) == []


def test_crlf_only_difference_is_green(pair):
    a, b = pair
    rel = "docs/parity.md"
    (b / rel).write_bytes((a / rel).read_bytes().replace(b"\n", b"\r\n"))
    assert gate_parity.compare(a, b) == []


def test_content_drift_is_red(pair):
    a, b = pair
    (b / "docs/parity.md").write_text("另一組改了\n", encoding="utf-8")
    assert gate_parity.compare(a, b) == ["docs/parity.md: 兩組內容不一致"]


def test_missing_file_is_red(pair):
    a, b = pair
    (b / "docs/requirements.md").unlink()
    problems = gate_parity.compare(a, b)
    assert len(problems) == 1 and problems[0].startswith("docs/requirements.md: 缺檔")


def test_cli_without_sibling_reports_not_run(tmp_path: Path):
    r = subprocess.run([sys.executable, str(OPS / "gate_parity.py"), str(tmp_path), ""],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 0 and "未跑" in r.stdout


def test_cli_drift_exit_code(pair):
    a, b = pair
    (b / "docs/parity.md").write_text("x\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(OPS / "gate_parity.py"), str(a), str(b)],
                       capture_output=True, text=True, encoding="utf-8")
    assert r.returncode == 1
