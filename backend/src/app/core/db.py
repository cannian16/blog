from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def _engine_options(url: str) -> dict:
    if url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {"pool_pre_ping": True}


def _make_engine(url: str) -> Engine:
    return create_engine(url, **_engine_options(url))


engine = _make_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def configure_database(database_url: str) -> Engine:
    """Replace the process-local engine, primarily for isolated tests."""
    global engine, SessionLocal
    engine.dispose()
    engine = _make_engine(database_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    return engine


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session
