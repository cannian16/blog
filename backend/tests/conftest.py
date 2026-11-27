from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

BACKEND_DIR = Path(__file__).resolve().parents[1]

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL") or (
    "postgresql://dev:dev_password@127.0.0.1:5433/blog_test"
)
if make_url(TEST_DATABASE_URL).get_backend_name() != "postgresql":
    raise RuntimeError("测试必须使用 PostgreSQL，请通过 TEST_DATABASE_URL 指定连接地址")

os.environ["DATABASE_URL"] = TEST_DATABASE_URL
os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "password")

import app.models  # noqa: E402, F401
from app.core.db import Base, get_db  # noqa: E402
from app.middleware.trace_id import TraceIDMiddleware  # noqa: E402
from app.routers import router as api_router  # noqa: E402


def _ensure_database() -> None:
    url = make_url(TEST_DATABASE_URL)
    admin_engine = create_engine(url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :name"),
                {"name": url.database},
            ).scalar()
            if not exists:
                connection.execute(text(f'CREATE DATABASE "{url.database}"'))
    except OperationalError as exc:
        safe_url = url.render_as_string(hide_password=True)
        raise RuntimeError(
            f"无法连接 PostgreSQL（{safe_url}）。"
            "请先启动 docker compose up -d postgresql，或设置 TEST_DATABASE_URL。"
        ) from exc
    finally:
        admin_engine.dispose()


@pytest.fixture(scope="session")
def test_database_url() -> str:
    return TEST_DATABASE_URL


@pytest.fixture(scope="session", autouse=True)
def prepared_database() -> Iterator[None]:
    _ensure_database()
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        env={**os.environ, "DATABASE_URL": TEST_DATABASE_URL},
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Alembic 迁移失败:\n{result.stdout}\n{result.stderr}")
    yield


@pytest.fixture(scope="session")
def db_engine(prepared_database: None) -> Iterator[Engine]:
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(db_engine: Engine) -> sessionmaker:
    return sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture(autouse=True)
def clean_database(db_engine: Engine) -> Iterator[None]:
    table_names = ", ".join(f'"{table.name}"' for table in Base.metadata.sorted_tables)
    with db_engine.begin() as connection:
        connection.execute(text(f"TRUNCATE TABLE {table_names} RESTART IDENTITY CASCADE"))
    yield


@pytest.fixture
def client(session_factory: sessionmaker) -> Iterator[TestClient]:
    application = FastAPI()
    application.add_middleware(TraceIDMiddleware)
    application.include_router(api_router)

    def override_get_db():
        with session_factory() as session:
            yield session

    application.dependency_overrides[get_db] = override_get_db
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
