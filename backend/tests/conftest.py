import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-at-least-32-bytes")
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "password")

from app.main import create_app  # noqa: E402


@pytest.fixture
def client(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'test.db').as_posix()}"
    application = create_app(database_url, create_tables=True, debug=False)
    with TestClient(application) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}
