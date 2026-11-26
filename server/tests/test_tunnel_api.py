"""老師頁一鍵開關手機連線（easy-setup D3）。以假 Tunnel 替身，不真起 cloudflared、不連網。"""
import asyncio
import threading
import time

import httpx
import pytest
from conftest import TEACHER_KEY
from fastapi.testclient import TestClient

from quiz_server.app import create_app
from quiz_server.views import student_view

H = {"X-Teacher-Key": TEACHER_KEY}
URL = "https://abc-def-ghi.trycloudflare.com/"
PUBLIC = {"host": "abc-def.trycloudflare.com", "cf-connecting-ip": "203.0.113.9"}


class FakeTunnel:
    def __init__(self, url: str | None = URL, available: bool = True) -> None:
        self.url = url
        self._available = available
        self.starts = 0
        self.stops = 0
        self.gate = threading.Event()
        self.gate.set()
        self.started = threading.Event()
        self._alive = False

    def available(self) -> bool:
        return self._available

    def start(self, timeout: float = 30) -> str | None:
        self.starts += 1
        self.started.set()
        self.gate.wait(5)
        self._alive = self.url is not None
        return self.url

    def stop(self) -> None:
        self.stops += 1
        self._alive = False

    def alive(self) -> bool:
        return self._alive


def client_for(activity, tunnel, **kw):
    return TestClient(create_app(activity=activity, teacher_key=TEACHER_KEY, tunnel=tunnel, **kw))


def teacher_state(c):
    return c.get("/api/teacher/state", headers=H).json()


def test_open_then_close(activity):
    t = FakeTunnel()
    with client_for(activity, t) as c:
        assert teacher_state(c)["tunnel"] == "off"
        r = c.post("/api/teacher/tunnel", headers=H)
        assert r.status_code == 200 and r.json() == {"tunnel": "on", "student_url": URL}
        s = teacher_state(c)
        assert s["tunnel"] == "on" and s["student_url"] == URL
        assert c.post("/api/teacher/tunnel", headers=H).json()["tunnel"] == "on"  # 冪等
        assert t.starts == 1
        r = c.delete("/api/teacher/tunnel", headers=H)
        assert r.status_code == 200 and r.json() == {"tunnel": "off", "student_url": None}
        s = teacher_state(c)
        assert s["tunnel"] == "off" and s["student_url"] is None
        assert t.stops >= 1
        assert c.delete("/api/teacher/tunnel", headers=H).status_code == 200  # 已關冪等


def test_open_pushes_to_teacher_websocket(activity):
    with client_for(activity, FakeTunnel()) as c, \
            c.websocket_connect(f"/ws?role=teacher&key={TEACHER_KEY}") as ws:
        assert ws.receive_json()["view"]["tunnel"] == "off"
        c.post("/api/teacher/tunnel", headers=H)
        seen = []
        while not seen or seen[-1] != "on":
            seen.append(ws.receive_json()["view"]["tunnel"])
        assert seen[0] == "starting" and seen[-1] == "on"


def test_cloudflared_missing_503(activity):
    with client_for(activity, FakeTunnel(available=False)) as c:
        r = c.post("/api/teacher/tunnel", headers=H)
        assert r.status_code == 503
        assert "winget install --id Cloudflare.cloudflared -e" in r.json()["detail"]
        assert teacher_state(c)["tunnel"] == "off"


def test_no_tunnel_injected_503(activity):
    with client_for(activity, None) as c:
        assert c.post("/api/teacher/tunnel", headers=H).status_code == 503


def test_timeout_504(activity):
    with client_for(activity, FakeTunnel(url=None)) as c:
        r = c.post("/api/teacher/tunnel", headers=H)
        assert r.status_code == 504 and r.json()["detail"] == "建立手機連線逾時，請再試一次"
        s = teacher_state(c)
        assert s["tunnel"] == "off" and s["student_url"] is None


def test_close_rejected_after_start(ready_activity):
    t = FakeTunnel()
    with client_for(ready_activity, t) as c:
        c.post("/api/teacher/tunnel", headers=H)
        assert c.post("/api/teacher/start", headers=H).status_code == 200
        r = c.delete("/api/teacher/tunnel", headers=H)
        assert r.status_code == 409 and r.json()["detail"] == "搶答進行中不能關閉手機連線"
        assert teacher_state(c)["tunnel"] == "on" and t.stops == 0
        assert c.post("/api/teacher/tunnel", headers=H).status_code == 200  # 開啟不限階段


def test_starting_second_open_409_and_close_cancels(activity):
    t = FakeTunnel()
    t.gate.clear()
    app = create_app(activity=activity, teacher_key=TEACHER_KEY, tunnel=t)

    async def go():
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as c:
            first = asyncio.create_task(c.post("/api/teacher/tunnel", headers=H))
            assert await asyncio.to_thread(t.started.wait, 5)
            assert activity.tunnel_state == "starting"
            second = await c.post("/api/teacher/tunnel", headers=H)
            assert second.status_code == 409 and second.json()["detail"] == "手機連線建立中"
            closing = asyncio.create_task(c.delete("/api/teacher/tunnel", headers=H))
            await asyncio.sleep(0.05)
            t.gate.set()
            r1, rd = await first, await closing
            return r1, rd

    r1, rd = asyncio.run(go())
    assert r1.status_code == 200 and r1.json() == {"tunnel": "off", "student_url": None}
    assert rd.status_code == 200 and rd.json() == {"tunnel": "off", "student_url": None}
    assert t.starts == 1 and t.stops >= 1
    assert activity.tunnel_state == "off" and activity.public_url is None


def test_unexpected_exit_turns_off(activity):
    t = FakeTunnel()
    t._alive = True
    with client_for(activity, t, student_url=URL, tunnel_watch_interval=0.02) as c:
        assert teacher_state(c)["tunnel"] == "on"
        t._alive = False
        deadline = time.monotonic() + 3
        while teacher_state(c)["tunnel"] != "off":
            assert time.monotonic() < deadline
            time.sleep(0.02)
        assert teacher_state(c)["student_url"] is None


def test_boot_tunnel_is_same_instance_and_can_be_closed(activity):
    """`--tunnel` 啟動時開的通道就是注入的實例，DELETE 停得掉（v1.1 藥方 1）。"""
    t = FakeTunnel()
    t._alive = True
    with client_for(activity, t, student_url=URL) as c:
        assert teacher_state(c)["tunnel"] == "on"
        assert c.delete("/api/teacher/tunnel", headers=H).status_code == 200
        assert t.stops == 1


def test_shutdown_stops_tunnel(activity):
    t = FakeTunnel()
    with client_for(activity, t) as c:
        c.post("/api/teacher/tunnel", headers=H)
    assert t.stops >= 1


def test_public_host_rejected(activity):
    t = FakeTunnel()
    with client_for(activity, t) as c:
        assert c.post("/api/teacher/tunnel", headers={**H, **PUBLIC}).status_code == 403
        assert c.delete("/api/teacher/tunnel", headers={**H, **PUBLIC}).status_code == 403
        assert c.post("/api/teacher/tunnel").status_code == 401
    assert t.starts == 0


def test_student_view_never_has_tunnel_fields(activity):
    with client_for(activity, FakeTunnel()) as c:
        token = c.post("/api/student/join", json={"team": "第1組"}).json()["token"]
        c.post("/api/teacher/tunnel", headers=H)
        team = activity.team_of(token)
        v = student_view(activity, team)
        assert "tunnel" not in v and "student_url" not in v
        assert URL not in str(v)


@pytest.mark.parametrize("state", ["off", "starting", "on"])
def test_set_tunnel_bumps_version(activity, state):
    before = activity.version
    asyncio.run(activity.set_tunnel(state, URL if state == "on" else None))
    assert activity.version == before + 1 and activity.tunnel_state == state
