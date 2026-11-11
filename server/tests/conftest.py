import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parents[2] / "tests" / "fixtures" / "guided-notes"
TEACHER_KEY = "test-teacher-key-0000"
os.environ.setdefault("QUIZ_TEACHER_KEY", TEACHER_KEY)


@pytest.fixture
def fixture_bytes():
    def _read(name: str) -> bytes:
        return (FIXTURES / name).read_bytes()
    return _read


@pytest.fixture
def activity():
    from quiz_server.activity import Activity
    return Activity()


@pytest.fixture
def ready_activity(activity, fixture_bytes):
    """可直接開始搶答的活動：開始前須已匯入題目（buzz-answering MODIFIED requirement）。"""
    import asyncio
    asyncio.run(activity.load_questions(fixture_bytes("group.xlsx"), "group.xlsx"))
    return activity


@pytest.fixture
def loaded_client(client, fixture_bytes, teacher_headers):
    """已匯入 group.xlsx（4 題：第 1、2 題為 2 子題題組）的測試用戶端。"""
    r = client.post("/api/teacher/import", headers=teacher_headers,
                    files={"file": ("group.xlsx", fixture_bytes("group.xlsx"), "application/octet-stream")})
    assert r.status_code == 200
    return client


@pytest.fixture
def client(activity):
    from fastapi.testclient import TestClient

    from quiz_server.app import create_app
    with TestClient(create_app(activity=activity, teacher_key=TEACHER_KEY)) as c:
        yield c


@pytest.fixture
def teacher_headers():
    return {"X-Teacher-Key": TEACHER_KEY}
