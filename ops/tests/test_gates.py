"""門禁的負例：證明「錯時會紅」（CLAUDE.md 基本紀律「先對標、多方向驗證」）。"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

OPS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(OPS))

import gate_secrets  # noqa: E402
import gate_zh_hant  # noqa: E402


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    return tmp_path


def test_zh_hant_flags_simplified(repo: Path):
    (repo / "a.md").write_text("這是繁體\n" + chr(0x8FD9) + "是簡體\n", encoding="utf-8")
    assert gate_zh_hant.scan(repo) == [f"a.md:2: 簡體字 {chr(0x8FD9)}"]


def test_zh_hant_passes_traditional_and_ambiguous(repo: Path):
    # 于、后、里、并、准 在繁體也有正當用法，刻意不收
    (repo / "a.md").write_text("這是繁體，皇后在公里外並准于此\n", encoding="utf-8")
    assert gate_zh_hant.scan(repo) == []


def test_zh_hant_allow_mark(repo: Path):
    (repo / "a.md").write_text(chr(0x8FD9) + " zh-hant: allow\n", encoding="utf-8")
    assert gate_zh_hant.scan(repo) == []


def test_zh_hant_covers_untracked_new_file(repo: Path):
    (repo / "new.py").write_text("# " + chr(0x4E2A) + "\n", encoding="utf-8")
    assert len(gate_zh_hant.scan(repo)) == 1


@pytest.mark.parametrize("secret", [
    "sk-" + "A1b2C3d4E5f6G7h8I9j0K1l2",
    "sk-proj-" + "A1b2C3d4E5f6G7h8I9j0K1l2",
    "AKIA" + "ABCDEFGH12345678",
    "AIza" + "B" * 35,
    "ghp_" + "c" * 36,
    "GOCSPX-" + "Ab1Cd2Ef3Gh4Ij5Kl6Mn7Op8Qr",
    "ya29." + "a0AfB_" + "x" * 30,
    "1//" + "0eXyZ" + "q" * 30,
    "-----BEGIN " + "PRIVATE KEY-----",
])
def test_secrets_flags_real_shapes(repo: Path, secret: str):
    (repo / "conf.txt").write_text(f"key={secret}\n", encoding="utf-8")
    hits = gate_secrets.scan(repo)
    assert len(hits) == 1
    assert secret not in hits[0]  # 門禁輸出不得回顯金鑰


@pytest.mark.parametrize(
    "fixture", ["sk-" + "0" * 24, "AKIA" + "0" * 16, "AIza" + "0" * 35, "ghp_" + "0" * 36,
                "GOCSPX-" + "0" * 28, "ya29." + "0" * 40, "1//" + "0" * 40, "http://127.0.0.1//" + "a" * 30]
)
def test_secrets_passes_zero_fixtures(repo: Path, fixture: str):
    (repo / "conf.txt").write_text(f"key={fixture}\n", encoding="utf-8")
    assert gate_secrets.scan(repo) == []


def test_gate_exit_codes(repo: Path):
    (repo / "a.md").write_text("AKIA" + "ABCDEFGH12345678\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(OPS / "gate_secrets.py"), str(repo)], capture_output=True)
    assert r.returncode == 1
    (repo / "a.md").write_text("ok\n", encoding="utf-8")
    r = subprocess.run([sys.executable, str(OPS / "gate_secrets.py"), str(repo)], capture_output=True)
    assert r.returncode == 0



@pytest.mark.parametrize("gate", [gate_secrets, gate_zh_hant])
@pytest.mark.parametrize("encoding", ["utf-16", "utf-16-le", "gbk"])
def test_non_utf8_file_is_red(repo: Path, gate, encoding: str):
    # 評審實證：UTF-16 檔裡的金鑰與 GBK 檔裡的簡體字，舊版門禁 0 findings、退出碼 0
    payload = "AKIA" + "ABCDEFGH12345678 " + chr(0x8FD9) + "\n"
    (repo / "out.txt").write_bytes(payload.encode(encoding))
    hits = gate.scan(repo)
    assert len(hits) == 1 and "無法以 UTF-8 解碼" in hits[0]


HOOK = OPS.parent / ".githooks" / "pre-push"
SHA_A, SHA_0 = "1" * 40, "0" * 40


def _run_hook(stdin: str, env_extra: dict[str, str] | None = None) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
    env.update(env_extra or {})
    # 以 PATH 解析 bash：Windows 的 CreateProcess 會先搜 System32，裸 "bash" 可能拿到 WSL 的 bash.exe（不認
    # Windows 路徑，鉤子讀不到而 127）；Store 版 Python 碰巧避開，
    # 改用 uv 管理的 Python（make codex-venv）即踩到
    bash = shutil.which("bash") or "bash"
    return subprocess.run(
        [bash, str(HOOK), "origin", "url"], input=stdin, capture_output=True, text=True, env=env
    )


def _line(remote_ref: str) -> str:
    return f"refs/heads/feat {SHA_A} {remote_ref} {SHA_0}\n"


@pytest.mark.parametrize("remote_ref", ["refs/heads/main", "refs/heads/dev"])
def test_prepush_blocks_protected(remote_ref: str):
    r = _run_hook(_line(remote_ref))
    assert r.returncode == 1
    assert "拒絕" in r.stderr


@pytest.mark.parametrize(
    "remote_ref", ["refs/heads/feat/x", "refs/heads/maintenance", "refs/heads/dev-notes"]
)
def test_prepush_allows_feature(remote_ref: str):
    assert _run_hook(_line(remote_ref)).returncode == 0


def test_prepush_blocks_when_any_ref_protected():
    lines = _line("refs/heads/feat/a") + _line("refs/heads/main")
    assert _run_hook(lines).returncode == 1


def test_prepush_does_not_depend_on_claude_env():
    # ! 與 Claude 的 Bash 工具環境相同，鉤子只依目標分支判斷；擋 Claude 交給權限層
    assert _run_hook(_line("refs/heads/feat/x"), {"CLAUDECODE": "1"}).returncode == 0
    assert _run_hook(_line("refs/heads/main"), {"CLAUDECODE": "1"}).returncode == 1
