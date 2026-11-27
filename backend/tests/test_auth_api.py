from __future__ import annotations

import time

import jwt

from app.core.config import settings


def test_login_returns_oauth2_token(client):
    response = client.post("/auth/login", data={"username": "admin", "password": "password"})
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]

    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["username"] == "admin"
    assert me.json()["role"] == "admin"


def test_login_rejects_wrong_credentials(client):
    assert client.post("/auth/login", data={"username": "wrong", "password": "password"}).status_code == 403
    assert client.post("/auth/login", data={"username": "admin", "password": "wrong"}).status_code == 403


def test_login_requires_form_fields(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "password"})
    assert response.status_code == 422


def test_auth_rejects_missing_and_invalid_tokens(client):
    missing = client.get("/auth/me")
    assert missing.status_code == 401
    assert missing.json() == {"detail": "未提供有效凭证"}
    assert missing.headers["www-authenticate"] == "Bearer"

    invalid = client.get("/auth/me", headers={"Authorization": "Bearer invalid"})
    assert invalid.status_code == 401
    assert invalid.json() == {"detail": "无效的 Token"}

    wrong_scheme = client.get("/auth/me", headers={"Authorization": "Token abc"})
    assert wrong_scheme.status_code == 401


def test_auth_rejects_expired_and_non_admin_tokens(client):
    expired = jwt.encode(
        {"sub": "admin", "role": "admin", "exp": int(time.time()) - 1},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert response.json() == {"detail": "Token 已过期"}

    non_admin = jwt.encode(
        {"sub": "user", "role": "user", "exp": int(time.time()) + 60},
        settings.SECRET_KEY,
        algorithm="HS256",
    )
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {non_admin}"})
    assert response.status_code == 403
    assert response.json() == {"detail": "权限不足"}


def test_openapi_declares_oauth2_password_flow(client):
    schema = client.app.openapi()
    oauth2 = next(
        scheme for scheme in schema["components"]["securitySchemes"].values() if scheme["type"] == "oauth2"
    )
    assert oauth2["flows"]["password"]["tokenUrl"] == "/auth/login"
    assert schema["paths"]["/admin/links"]["post"]["security"] == [{"OAuth2PasswordBearer": []}]
