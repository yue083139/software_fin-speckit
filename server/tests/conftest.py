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
def ready_activity(activity):
    """可直接開始搶答的活動；後續卡要求開始前須有題目時，在此補上匯入。"""
    return activity


@pytest.fixture
def client(activity):
    from fastapi.testclient import TestClient

    from quiz_server.app import create_app
    with TestClient(create_app(activity=activity, teacher_key=TEACHER_KEY)) as c:
        yield c


@pytest.fixture
def teacher_headers():
    return {"X-Teacher-Key": TEACHER_KEY}
