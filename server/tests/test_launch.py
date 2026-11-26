"""啟動後自動開老師頁（easy-setup D1）與 `__main__` 的通道注入（v1.1 藥方 1）。

不開真瀏覽器、不起 cloudflared。
"""
import pytest

from quiz_server import __main__ as main_module
from quiz_server.launch import open_when_ready, should_open


@pytest.mark.parametrize(("no_browser", "env", "expected"), [
    (False, {}, True),
    (True, {}, False),
    (False, {"QUIZ_NO_BROWSER": "1"}, False),
    (False, {"CI": "true"}, False),
    (False, {"CI": ""}, True),
    (False, {"QUIZ_NO_BROWSER": "0"}, True),
])
def test_should_open(no_browser, env, expected):
    assert should_open(no_browser, env) is expected


def test_opens_once_after_ready():
    ticks = iter([False, False, True, True, True])
    opened: list[str] = []
    ok = open_when_ready(lambda: next(ticks), "http://127.0.0.1:8000/#/teacher?key=k",
                         opener=lambda u: opened.append(u) or True, sleep=lambda _: None)
    assert ok is True and opened == ["http://127.0.0.1:8000/#/teacher?key=k"]


def test_opener_false_prints_hint(capsys):
    ok = open_when_ready(lambda: True, "u", opener=lambda _: False, sleep=lambda _: None)
    assert ok is False
    assert "沒有自動開啟瀏覽器，請手動開上面的老師頁網址" in capsys.readouterr().out


def test_opener_raising_prints_hint(capsys):
    def boom(_: str) -> bool:
        raise RuntimeError("no display")

    assert open_when_ready(lambda: True, "u", opener=boom, sleep=lambda _: None) is False
    assert "沒有自動開啟瀏覽器" in capsys.readouterr().out


def test_never_ready_does_not_open():
    clock = iter(range(1000))
    opened: list[str] = []
    ok = open_when_ready(lambda: False, "u", opener=lambda u: opened.append(u) or True, timeout=5,
                         sleep=lambda _: None, now=lambda: float(next(clock)))
    assert ok is False and opened == []


class FakeTunnel:
    instances: list["FakeTunnel"] = []

    def __init__(self, port: int) -> None:
        self.port = port
        self.started = 0
        self.stopped = 0
        FakeTunnel.instances.append(self)

    def start(self, timeout: float = 30) -> str | None:
        self.started += 1
        return "https://abc-def.trycloudflare.com/"

    def stop(self) -> None:
        self.stopped += 1


class FakeServer:
    def __init__(self, config) -> None:
        self.config = config
        self.started = True

    def run(self) -> None:
        pass


@pytest.fixture
def wiring(monkeypatch):
    FakeTunnel.instances = []
    calls: dict = {"browser": []}

    def fake_create_app(**kw):
        calls["create_app"] = kw
        return object()

    monkeypatch.setattr(main_module, "Tunnel", FakeTunnel)
    monkeypatch.setattr(main_module, "create_app", fake_create_app)
    monkeypatch.setattr(main_module, "load_env", lambda *a, **k: None)
    monkeypatch.setattr(main_module.uvicorn, "Server", FakeServer)
    monkeypatch.setattr(main_module, "start_browser", lambda server, url: calls["browser"].append(url))
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("QUIZ_NO_BROWSER", raising=False)
    monkeypatch.delenv("QUIZ_TUNNEL", raising=False)
    monkeypatch.setenv("QUIZ_TEACHER_KEY", "k" * 22)
    return calls


def test_main_injects_tunnel_with_server_port(wiring):
    main_module.main(["--port", "8123", "--no-browser"])
    (t,) = FakeTunnel.instances
    assert t.port == 8123 and t.started == 0
    assert wiring["create_app"]["tunnel"] is t
    assert wiring["create_app"]["student_url"] is None
    assert wiring["browser"] == []
    assert t.stopped == 1  # 伺服器結束一定收子行程


def test_main_boot_tunnel_uses_same_instance(wiring):
    main_module.main(["--port", "8123", "--tunnel", "--no-browser"])
    (t,) = FakeTunnel.instances
    assert t.started == 1 and wiring["create_app"]["tunnel"] is t
    assert wiring["create_app"]["student_url"] == "https://abc-def.trycloudflare.com/"


def test_main_opens_teacher_page_once(wiring):
    main_module.main(["--port", "8123"])
    assert wiring["browser"] == ["http://127.0.0.1:8123/#/teacher?key=" + "k" * 22]


def test_main_respects_env_flag(wiring, monkeypatch):
    monkeypatch.setenv("QUIZ_NO_BROWSER", "1")
    main_module.main(["--port", "8123"])
    assert wiring["browser"] == []
