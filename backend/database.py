import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

try:  # optional: load ../.env so backend and bot share one config file
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:  # pragma: no cover
    pass

DEFAULT_DB = Path(__file__).resolve().parent / "bloodlink.db"
SQLALCHEMY_DATABASE_URL = os.getenv("BLOODLINK_DB_URL", f"sqlite:///{DEFAULT_DB.as_posix()}")

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
