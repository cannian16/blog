from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.db import get_db
from app.main import create_app


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


def test_startup_fails_when_database_unavailable(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'missing' / 'app.db').as_posix()}"
    application = create_app(database_url, debug=False)

    with pytest.raises(ConnectionError, match="数据库连接失败"):
        with TestClient(application):
            pass
