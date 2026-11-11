"""憲章門禁的負例：佔位符殘留、缺版本列、刪掉圖表優先原則都要紅。"""
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))

import gate_speckit  # noqa: E402

GOOD = (
    "# 憲章\n### VII. 圖表生成\n名稱：PlantUML 設計優先\n存放 ./diagrams/ 目錄。\n"
    "在 speckit.implement 階段驗證。\n**Version**: 1.0.0 | **Ratified**: 2026-11-11\n"
)


@pytest.fixture
def root(tmp_path: Path) -> Path:
    (tmp_path / ".specify" / "memory").mkdir(parents=True)
    return tmp_path


def _write(root: Path, text: str) -> None:
    (root / gate_speckit.CONSTITUTION).write_text(text, encoding="utf-8")


def test_filled_constitution_is_green(root: Path):
    _write(root, GOOD)
    assert gate_speckit.scan(root) == ([], "1.0.0")


def test_placeholder_is_red(root: Path):
    _write(root, GOOD + "### [PRINCIPLE_1_NAME]\n")
    problems, _ = gate_speckit.scan(root)
    assert problems == [f"{gate_speckit.CONSTITUTION}:7: 範本佔位符 [PRINCIPLE_1_NAME]"]


def test_missing_version_is_red(root: Path):
    _write(root, GOOD.replace("**Version**: 1.0.0", "版本未定"))
    problems, version = gate_speckit.scan(root)
    assert version is None and any("版本列" in p for p in problems)


def test_removed_diagram_principle_is_red(root: Path):
    _write(root, GOOD.replace("PlantUML 設計優先", "（刪除）"))
    problems, _ = gate_speckit.scan(root)
    assert problems == [f"{gate_speckit.CONSTITUTION}: 缺圖表優先原則要素「PlantUML 設計優先」"]


def test_missing_file_is_red(tmp_path: Path):
    assert gate_speckit.scan(tmp_path)[0] == [f"{gate_speckit.CONSTITUTION}: 缺檔"]
