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
SQLALCHEMY_DATABASE_URL = (os.getenv("BLOODLINK_DB_URL") or os.getenv("DATABASE_URL")
                           or f"sqlite:///{DEFAULT_DB.as_posix()}")
# Hosted Postgres (Neon, Supabase, Render) hands out postgres:// URLs; use the psycopg 3 driver for them.
for prefix in ("postgres://", "postgresql://"):
    if SQLALCHEMY_DATABASE_URL.startswith(prefix):
        SQLALCHEMY_DATABASE_URL = "postgresql+psycopg://" + SQLALCHEMY_DATABASE_URL[len(prefix):]

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=300)
SessionLocal = sessionmaker(bind=engine, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
