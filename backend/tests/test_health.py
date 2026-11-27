from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from app.core import db as db_module
from app.core.db import get_db
from app.main import app as main_app


def test_healthz_reports_ok(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


def test_healthz_returns_503_when_database_unavailable(client):
    class BrokenSession:
        def execute(self, *args, **kwargs):
            raise OperationalError("SELECT 1", {}, RuntimeError("database down"))

    client.app.dependency_overrides[get_db] = BrokenSession
    try:
        response = client.get("/healthz")
    finally:
        client.app.dependency_overrides.clear()

    assert response.status_code == 503
    assert response.json() == {"status": "error", "database": "unavailable"}


def test_startup_fails_when_database_unavailable(tmp_path, monkeypatch):
    broken_engine = create_engine(f"sqlite:///{(tmp_path / 'missing' / 'app.db').as_posix()}")
    monkeypatch.setattr(db_module, "engine", broken_engine)
    try:
        with pytest.raises(ConnectionError, match="数据库连接失败"):
            with TestClient(main_app):
                pass
    finally:
        broken_engine.dispose()


def test_trace_id_is_echoed_and_generated(client):
    response = client.get("/healthz", headers={"X-Trace-ID": "trace-123"})
    assert response.headers["x-trace-id"] == "trace-123"

    generated = client.get("/healthz")
    assert generated.headers["x-trace-id"]
