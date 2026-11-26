"""Google 設定精靈端點（easy-setup D2）：白名單、只改 .env 兩鍵、立即生效、密鑰不外洩、世代號。全程不連網。"""
import asyncio
import logging
from urllib.parse import parse_qs

import httpx
import pytest
from conftest import TEACHER_KEY
from fastapi.testclient import TestClient
from google_fake import ACCESS, CODE, EMAIL, id_token

from quiz_server.app import create_app
from quiz_server.google_auth import GoogleCallbackError, GoogleSession, state_digest

H = {"X-Teacher-Key": TEACHER_KEY}
VALID_ID = "123456789012-" + "a" * 32 + ".apps.googleusercontent.com"
VALID_SECRET = "GOCSPX-" + "0" * 28
OTHER_ID = "210987654321-" + "b" * 32 + ".apps.googleusercontent.com"
PUBLIC = {"host": "abc-def.trycloudflare.com", "cf-connecting-ip": "203.0.113.9"}


@pytest.fixture(autouse=True)
def _isolated_env(monkeypatch):
    # 端點會設 os.environ；monkeypatch 先刪，測試結束還原，不污染其他測試
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)


@pytest.fixture
def env_file(tmp_path):
    return tmp_path / ".env"


@pytest.fixture
def session():
    return GoogleSession(None, None)


@pytest.fixture
def cfg(activity, session, env_file):
    app = create_app(activity=activity, teacher_key=TEACHER_KEY, google=session, env_file=env_file)
    with TestClient(app) as c:
        yield c


def save(c, client_id=VALID_ID, client_secret=VALID_SECRET, headers=H):
    return c.post("/api/teacher/google/config", headers=headers,
                  json={"client_id": client_id, "client_secret": client_secret})


def test_status_has_hint_and_redirect_uri(cfg):
    s = cfg.get("/api/teacher/google", headers=H).json()
    assert s == {"configured": False, "signed_in": False, "email": None, "client_id_hint": None,
                 "redirect_uri": "http://127.0.0.1:8000/api/google/callback"}


def test_save_writes_two_keys_keeps_other_lines_and_takes_effect(cfg, env_file):
    import os
    env_file.write_text("﻿# 我的設定\nFOO=1\n\nBAR = 2\n", encoding="utf-8")
    r = save(cfg)
    assert r.status_code == 200
    body = r.json()
    assert body["configured"] is True and body["signed_in"] is False
    assert body["client_id_hint"] == "123456…apps.googleusercontent.com"
    assert VALID_SECRET not in r.text and VALID_ID not in r.text
    lines = env_file.read_text(encoding="utf-8").splitlines()
    assert lines == ["# 我的設定", "FOO=1", "", "BAR = 2",
                     f"GOOGLE_CLIENT_ID={VALID_ID}", f"GOOGLE_CLIENT_SECRET={VALID_SECRET}"]
    assert os.environ["GOOGLE_CLIENT_ID"] == VALID_ID
    # 不重啟即可登入：授權網址帶新的用戶端 ID
    url = cfg.post("/api/teacher/google/login", headers=H).json()["url"]
    assert parse_qs(httpx.URL(url).query.decode())["client_id"] == [VALID_ID]


def test_spaced_and_duplicate_keys_collapse_to_one(cfg, env_file):
    env_file.write_text("GOOGLE_CLIENT_ID = old\nX=1\nGOOGLE_CLIENT_ID=old2\nGOOGLE_CLIENT_SECRET=old\n",
                        encoding="utf-8")
    assert save(cfg).status_code == 200
    lines = env_file.read_text(encoding="utf-8").splitlines()
    assert lines == [f"GOOGLE_CLIENT_ID={VALID_ID}", "X=1", f"GOOGLE_CLIENT_SECRET={VALID_SECRET}"]


def test_no_temp_file_left(cfg, env_file):
    assert save(cfg).status_code == 200
    assert list(env_file.parent.glob(".env.tmp-*")) == []


@pytest.mark.parametrize(("client_id", "client_secret"), [
    (VALID_ID, VALID_SECRET + "\n"),               # 尾端換行：fullmatch 才擋得住
    (VALID_ID + "\nFOO=1", VALID_SECRET),           # 換行注入第二行
    (VALID_ID, "GOCSPX-" + "0" * 10 + "=" + "0" * 17),
    (VALID_ID, "gocspx-" + "0" * 28),               # 錯前綴
    (VALID_ID, "GOCSPX-" + "0" * 122),              # 超過 128 字
    ("not-a-client-id", VALID_SECRET),
    (" " + VALID_ID, VALID_SECRET),                 # 伺服器不 strip：寫入的必須就是驗證過的值
])
def test_invalid_rejected_and_file_unchanged(cfg, env_file, client_id, client_secret):
    env_file.write_text("FOO=1\n", encoding="utf-8")
    before = env_file.read_bytes()
    r = save(cfg, client_id, client_secret)
    assert r.status_code == 422
    assert "0" * 10 not in r.text and "FOO" not in r.text  # 不回顯輸入
    assert env_file.read_bytes() == before
    assert cfg.get("/api/teacher/google", headers=H).json()["configured"] is False


def test_public_host_rejected_before_key(cfg, env_file):
    assert save(cfg, headers={**H, **PUBLIC}).status_code == 403
    assert save(cfg, headers=PUBLIC).status_code == 403
    assert cfg.delete("/api/teacher/google/config", headers={**H, **PUBLIC}).status_code == 403
    assert not env_file.exists()


def test_requires_teacher_key(cfg):
    assert save(cfg, headers={}).status_code == 401
    assert cfg.delete("/api/teacher/google/config").status_code == 401


def test_signed_in_cannot_change_or_clear(cfg, session, env_file):
    assert save(cfg).status_code == 200
    session._access_token = ACCESS  # 測試內直接設為已登入
    before = env_file.read_bytes()
    r = save(cfg, OTHER_ID)
    assert r.status_code == 409 and r.json()["detail"] == "請先登出 Google 再變更設定"
    assert cfg.delete("/api/teacher/google/config", headers=H).status_code == 409
    assert env_file.read_bytes() == before


def test_clear_removes_keys_keeps_others(cfg, env_file):
    import os
    env_file.write_text("FOO=1\n", encoding="utf-8")
    assert save(cfg).status_code == 200
    r = cfg.delete("/api/teacher/google/config", headers=H)
    assert r.status_code == 200 and r.json()["configured"] is False
    assert env_file.read_text(encoding="utf-8").splitlines() == ["FOO=1"]
    assert "GOOGLE_CLIENT_ID" not in os.environ
    assert cfg.post("/api/teacher/google/login", headers=H).status_code == 400


def test_secret_never_logged(cfg, caplog):
    caplog.set_level(logging.DEBUG)
    assert save(cfg).status_code == 200
    assert VALID_SECRET not in caplog.text


def test_reconfigure_discards_inflight_login():
    """世代號（v1.1 藥方 5）：換權杖的 await 期間設定被換掉 ⇒ 舊授權不落地。"""
    holder: dict[str, GoogleSession] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        holder["s"].reconfigure(OTHER_ID, VALID_SECRET)  # 模擬回呼等待 Google 時老師存了新設定
        return httpx.Response(200, json={"access_token": ACCESS, "expires_in": 3600,
                                         "id_token": id_token(EMAIL)})

    s = GoogleSession(VALID_ID, VALID_SECRET, transport=httpx.MockTransport(handler))
    holder["s"] = s
    url, state = s.begin()
    with pytest.raises(GoogleCallbackError):
        asyncio.run(s.complete(state, CODE, state_digest(state)))
    assert s.signed_in is False and s.email is None
    assert url  # 用掉變數，避免 lint


def test_reconfigure_clears_pending_state():
    s = GoogleSession(VALID_ID, VALID_SECRET)
    _, state = s.begin()
    s.reconfigure(OTHER_ID, VALID_SECRET)
    with pytest.raises(GoogleCallbackError):
        asyncio.run(s.complete(state, CODE, state_digest(state)))


def _refresh_session(on_request):
    """已登入且 access token 已過期、帶 refresh token 的 session；續期請求時呼叫 on_request(session)。"""
    holder: dict[str, GoogleSession] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        on_request(holder["s"])
        return httpx.Response(200, json={"access_token": "ya29." + "1" * 40, "expires_in": 3600})

    clock = [1000.0]
    s = GoogleSession(VALID_ID, VALID_SECRET, transport=httpx.MockTransport(handler), clock=lambda: clock[0])
    holder["s"] = s
    s._access_token = ACCESS
    s._refresh_token = "1//" + "0" * 40
    s._expires_at = 900.0  # 已過期 ⇒ token() 會續期
    return s


@pytest.mark.parametrize("interrupt", ["logout", "reconfigure"])
def test_refresh_discarded_when_session_changes_midway(interrupt):
    """續期的 await 期間登出或換設定 ⇒ 新權杖不落地（easy-setup 實作輪紅隊次要）。"""
    from quiz_server.google_auth import GoogleAuthError

    def on_request(s: GoogleSession) -> None:
        if interrupt == "logout":
            s._generation += 1  # 與 logout() 同效果，不在同步 handler 內跑 async
            s._clear()
        else:
            s.reconfigure(OTHER_ID, VALID_SECRET)

    s = _refresh_session(on_request)
    with pytest.raises(GoogleAuthError):
        asyncio.run(s.token())
    assert s.signed_in is False


def test_logout_bumps_generation():
    s = GoogleSession(VALID_ID, VALID_SECRET, transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    before = s._generation
    asyncio.run(s.logout())
    assert s._generation == before + 1
