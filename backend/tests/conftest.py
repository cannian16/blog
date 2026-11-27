import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "password")

import app.models  # noqa: E402, F401
from app.core.db import Base, get_db  # noqa: E402
from app.middleware.trace_id import TraceIDMiddleware  # noqa: E402
from app.routers import router as api_router  # noqa: E402


@pytest.fixture
def db_engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{(tmp_path / 'test.db').as_posix()}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session_factory(db_engine):
    return sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)


@pytest.fixture
def client(session_factory):
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
def auth_headers(client):
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
