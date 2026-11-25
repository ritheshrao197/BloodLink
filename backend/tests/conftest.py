"""Each test gets a fresh SQLite file DB. Telegram is off (messages are only logged) and nothing is seeded."""

import os
import sys
import tempfile
from pathlib import Path

_DB = Path(tempfile.mkdtemp()) / "test.db"
os.environ["BLOODLINK_DB_URL"] = f"sqlite:///{_DB.as_posix()}"
os.environ["TELEGRAM_BOT_TOKEN"] = ""
os.environ["AUTO_SEED"] = "0"
os.environ["REMINDERS"] = "0"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def fresh_db(monkeypatch):
    import models  # noqa: F401  (registers the tables)
    import weather
    from database import Base, engine

    monkeypatch.setattr(weather, "current", lambda district: None)  # no network calls from tests
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield


@pytest.fixture
def db():
    from database import SessionLocal

    s = SessionLocal()
    yield s
    s.close()


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    import main

    return TestClient(main.app)  # not used as a context manager, so the lifespan (seed, threads) never runs
