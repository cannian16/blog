from __future__ import annotations

import hashlib
import time
from datetime import datetime

import jwt
from sqlalchemy import inspect

from app.core import db as db_module
from app.core.config import DEFAULT_DATABASE_URL
from app.models import Link, Message, Post, Skill, Song, Tool
from app.schemas.resources import LinkSchema, PostSchema, SkillSchema, SongSchema, ToolSchema


EXPECTED_ROUTES = {
    ("/", "GET"),
    ("/auth/login", "POST"), ("/auth/me", "GET"),
    ("/messages/get", "GET"), ("/messages/add", "POST"),
    ("/links/get", "GET"), ("/links/add", "POST"), ("/links/delete", "POST"), ("/links/update", "POST"), ("/links/addlist", "POST"),
    ("/songs/get", "GET"), ("/songs/add", "POST"), ("/songs/delete", "POST"), ("/songs/update", "POST"), ("/songs/addlist", "POST"),
    ("/skills/get", "GET"), ("/skills/add", "POST"), ("/skills/addlist", "POST"), ("/skills/delete", "POST"), ("/skills/update", "POST"),
    ("/tools/get", "GET"), ("/tools/add", "POST"), ("/tools/delete", "POST"), ("/tools/update", "POST"), ("/tools/addlist", "POST"),
    ("/posts/get", "GET"), ("/posts/add", "POST"), ("/posts/delete", "POST"), ("/posts/update", "POST"),
    ("/system/deploy", "POST"),
}


def test_route_collection_and_plain_text_root(client):
    routes = {
        (path, method.upper())
        for path, operations in client.app.openapi()["paths"].items()
        for method in operations
    }
    assert routes == EXPECTED_ROUTES
    response = client.get("/")
    assert response.status_code == 200
    assert response.text == "Hello, World!"
    assert response.headers["content-type"].startswith("text/plain")


def test_authentication_contract(client):
    assert client.post("/auth/login", json={"username": "wrong", "password": "password"}).json() == {"message": "管理员用户名错误"}
    assert client.post("/auth/login", json={"username": "admin", "password": "wrong"}).status_code == 403
    assert client.get("/auth/me").json() == {"message": "未提供有效凭证"}
    assert client.get("/auth/me", headers={"Authorization": "Token abc"}).status_code == 401
    assert client.get("/auth/me", headers={"Authorization": "Bearer invalid"}).json() == {"message": "无效的 Token"}

    no_admin = jwt.encode({"admin": False, "exp": int(time.time()) + 60}, "test-secret-key-with-at-least-32-bytes", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {no_admin}"}).json() == {"message": "权限不足"}
    expired = jwt.encode({"admin": True, "exp": int(time.time()) - 1}, "test-secret-key-with-at-least-32-bytes", algorithm="HS256")
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"}).json() == {"message": "Token 已过期"}


def _exercise_resource(client, headers, prefix, payload, update, expected_delete):
    created = client.post(f"/{prefix}/add", json=payload, headers=headers)
    assert created.status_code == 201, created.text
    item_id = created.json()["id"]
    listed = client.get(f"/{prefix}/get")
    assert listed.status_code == 200 and listed.json()[0]["id"] == item_id
    changed = client.post(f"/{prefix}/update", json={"id": item_id, **update}, headers=headers)
    assert changed.status_code == 200
    for key, value in update.items():
        assert changed.json()[key] == value
    deleted = client.post(f"/{prefix}/delete", json={"id": item_id}, headers=headers)
    assert deleted.status_code == 200 and deleted.json() == expected_delete


def test_crud_for_link_song_skill_and_tool(client, auth_headers):
    _exercise_resource(client, auth_headers, "links", {"name": " A ", "url": "https://a.test", "description": "desc", "icon": "icon"}, {"name": "B"}, {"message": "友链已删除"})
    _exercise_resource(client, auth_headers, "songs", {"title": "Song", "artist": "Artist", "url": "song.mp3", "cover": "cover.jpg"}, {"title": "New Song"}, {"message": "歌曲已删除"})
    _exercise_resource(client, auth_headers, "skills", {"name": "Python", "logo": "python.svg", "url": "https://python.org"}, {"name": "FastAPI"}, {"message": "技能已删除"})
    _exercise_resource(client, auth_headers, "tools", {"title": "Tool", "subtitle": "Sub", "url": "https://tool.test", "imgUrl": "tool.png", "content": "Body"}, {"imgUrl": "new.png"}, {"message": "工具已删除"})


def test_post_crud_and_nested_serialization(client, auth_headers):
    payload = {"id": "post-one", "title": " Post ", "description": "Desc", "image": "image.png", "tags": ["python"], "category": "Code", "content": "Body"}
    created = client.post("/posts/add", json=payload, headers=auth_headers)
    assert created.status_code == 201
    assert created.json()["metadata"]["title"] == "Post"
    assert set(created.json()) == {"id", "metadata", "content"}
    updated = client.post("/posts/update", json={"id": "post-one", "title": "Updated", "tags": ["api"]}, headers=auth_headers)
    assert updated.json()["metadata"]["tags"] == ["api"]
    assert client.get("/posts/get").json()[0]["id"] == "post-one"
    assert client.post("/posts/delete", json={"id": "post-one"}, headers=auth_headers).json() == {"message": "文章已删除"}


def test_message_validation_hash_pagination_and_order(client):
    assert client.post("/messages/add", json={"username": "", "email": "a@test.com", "content": "x"}).json() == {"error": "用户名长度需在1-20位之间"}
    assert client.post("/messages/add", json={"username": "A", "email": "bad", "content": "x"}).json() == {"error": "邮箱格式不正确"}
    assert client.post("/messages/add", json={"username": "A", "email": "a@test.com", "content": ""}).json() == {"error": "内容不能为空且不能超过200字"}
    assert client.post("/messages/add", json={"username": "A", "email": "a@test.com", "content": "x", "website_url": "bad"}).json() == {"error": "网址格式不正确"}

    first = client.post("/messages/add", json={"username": " First ", "email": "First@Test.com", "content": " One "})
    second = client.post("/messages/add", json={"username": "Second", "email": "second@test.com", "content": "Two", "website_url": "https://example.com"})
    assert first.status_code == second.status_code == 201
    with db_module.SessionLocal() as session:
        session.get(Message, first.json()["id"]).created_at = datetime(2024, 1, 1)
        session.get(Message, second.json()["id"]).created_at = datetime(2024, 1, 2)
        session.commit()

    fallback = client.get("/messages/get?page=invalid&limit=invalid").json()
    assert fallback["pagination"]["page"] == 1
    assert fallback["pagination"]["limit"] == 20

    response = client.get("/messages/get?page=1&limit=1")
    body = response.json()
    assert body["pagination"] == {"total": 2, "page": 1, "limit": 1, "pages": 2}
    assert body["messages"][0]["username"] == "Second"
    assert "email" not in body["messages"][0]
    assert body["messages"][0]["email_hash"] == hashlib.sha256(b"second@test.com").hexdigest()


def test_model_database_and_schema_field_compatibility(client):
    expected = {
        "links": ["id", "name", "url", "description", "icon", "created_at"],
        "messages": ["id", "username", "website_url", "content", "email", "ip_address", "user_agent", "created_at"],
        "posts": ["id", "title", "published", "description", "image", "tags", "category", "content"],
        "skills": ["id", "name", "logo", "url"],
        "songs": ["id", "title", "artist", "url", "cover"],
        "tools": ["id", "title", "subtitle", "url", "imgUrl", "content"],
    }
    inspector = inspect(db_module.engine)
    assert set(inspector.get_table_names()) == set(expected)
    for table, columns in expected.items():
        assert [column["name"] for column in inspector.get_columns(table)] == columns

    expected_types = {
        "links": ["INTEGER", "VARCHAR(50)", "VARCHAR(500)", "VARCHAR(200)", "VARCHAR(500)", "DATETIME"],
        "messages": ["INTEGER", "VARCHAR(50)", "VARCHAR(200)", "TEXT", "VARCHAR(100)", "VARCHAR(45)", "VARCHAR(500)", "DATETIME"],
        "posts": ["VARCHAR(100)", "VARCHAR(200)", "DATETIME", "VARCHAR(200)", "VARCHAR(500)", "JSON", "VARCHAR(100)", "TEXT"],
        "skills": ["INTEGER", "VARCHAR(50)", "VARCHAR(200)", "VARCHAR(200)"],
        "songs": ["INTEGER", "VARCHAR(50)", "VARCHAR(50)", "VARCHAR(200)", "VARCHAR(200)"],
        "tools": ["INTEGER", "VARCHAR(50)", "VARCHAR(50)", "VARCHAR(200)", "VARCHAR(200)", "TEXT"],
    }
    for table, types in expected_types.items():
        assert [str(column["type"]) for column in inspector.get_columns(table)] == types

    assert Tool.__table__.c.imgUrl.nullable is False
    assert Post.__table__.c.tags.nullable is False and Post.__table__.c.tags.default is not None
    assert Post.__table__.c.published.server_default is not None
    assert Post.__table__.c.description.server_default.arg == "''"
    assert Link.__table__.c.created_at.nullable is True
    assert Message.__table__.c.website_url.nullable is True
    assert set(LinkSchema.model_fields) == {"id", "name", "url", "description", "icon", "created_at"}
    assert set(SongSchema.model_fields) == {"id", "title", "artist", "url", "cover"}
    assert set(SkillSchema.model_fields) == {"id", "name", "logo", "url"}
    assert set(ToolSchema.model_fields) == {"id", "title", "subtitle", "url", "imgUrl", "content"}
    assert set(PostSchema.model_fields) == {"id", "title", "published", "description", "image", "tags", "category", "content"}
    assert DEFAULT_DATABASE_URL.endswith("/backend/instance/app.db")


def test_bulk_resource_endpoints_and_sorting(client, auth_headers):
    cases = [
        ("links", [{"name": "L1", "url": "https://1.test", "description": "D1", "icon": "I1"}], "成功添加 1 个友链"),
        ("songs", [
            {"title": "S1", "artist": "A", "url": "1.mp3", "cover": "1.jpg"},
            {"title": "S2", "artist": "A", "url": "2.mp3", "cover": "2.jpg"},
        ], "成功添加 2 首歌曲"),
        ("skills", [
            {"name": "K1", "logo": "1.svg", "url": "https://1.test"},
            {"name": "K2", "logo": "2.svg", "url": "https://2.test"},
        ], "成功添加 2 个技能"),
        ("tools", [
            {"title": "T1", "subtitle": "S", "url": "https://1.test", "imgUrl": "1.png", "content": "C"},
            {"title": "T2", "subtitle": "S", "url": "https://2.test", "imgUrl": "2.png", "content": "C"},
        ], "成功添加 2 个工具"),
    ]
    for prefix, payload, message in cases:
        response = client.post(f"/{prefix}/addlist", json=payload, headers=auth_headers)
        assert response.status_code == 201 and response.json() == {"message": message}

    assert [item["title"] for item in client.get("/songs/get").json()] == ["S2", "S1"]
    assert [item["name"] for item in client.get("/skills/get").json()] == ["K1", "K2"]
    assert [item["title"] for item in client.get("/tools/get").json()] == ["T2", "T1"]


def test_system_deploy_service_contract(monkeypatch):
    from types import SimpleNamespace
    from app.services import system

    monkeypatch.setattr(system, "settings", SimpleNamespace(GITHUB_TOKEN=None, GITHUB_REPO=None))
    body, status_code = system.trigger_deploy()
    assert status_code == 500
    assert body == {"status": "error", "message": "服务器配置缺失：未找到 GitHub Token 或 Repo 路径"}

    class Response:
        status_code = 204
        content = b""
        text = ""

    calls = {}
    def fake_post(url, *, headers, json, timeout):
        calls.update(url=url, headers=headers, json=json, timeout=timeout)
        return Response()

    monkeypatch.setattr(system, "settings", SimpleNamespace(GITHUB_TOKEN="token", GITHUB_REPO="owner/repo"))
    monkeypatch.setattr(system.requests, "post", fake_post)
    body, status_code = system.trigger_deploy()
    assert status_code == 200 and body == {"status": "success", "message": "CI/CD 流程已在 GitHub 启动"}
    assert calls["url"] == "https://api.github.com/repos/owner/repo/dispatches"
    assert calls["json"]["event_type"] == "deploy-command"
    assert calls["timeout"] == 10


def test_docs_head_and_exact_options_compatibility(client, auth_headers):
    for path in ("/docs", "/redoc", "/openapi.json"):
        response = client.get(path)
        assert response.status_code == 404
        assert response.headers["content-type"].startswith("text/html")

    get_paths = {path for path, method in EXPECTED_ROUTES if method == "GET"}
    for path in get_paths:
        headers = auth_headers if path == "/auth/me" else None
        get_response = client.get(path, headers=headers)
        head_response = client.head(path, headers=headers)
        assert head_response.status_code == get_response.status_code, path
        assert head_response.content == b"", path

    business_paths = {path for path, _ in EXPECTED_ROUTES}
    assert len(business_paths) == 30
    for path in business_paths:
        response = client.options(path)
        assert response.status_code == 200, path
        assert "OPTIONS" in response.headers["allow"]

    preflight = client.options(
        "/",
        headers={
            "Origin": "http://localhost:4321",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code == 200
    assert "access-control-allow-origin" not in preflight.headers

    assert client.options("/unknown").status_code == 404
    preflight = client.options(
        "/unknown",
        headers={"Origin": "http://localhost:4321", "Access-Control-Request-Method": "POST"},
    )
    assert preflight.status_code == 404


def test_flask_json_loading_and_authentication_order(client, auth_headers):
    no_content_type = client.post("/auth/login", content='{"username":"admin","password":"password"}')
    assert no_content_type.status_code == 415
    assert no_content_type.headers["content-type"].startswith("text/html")
    assert "Unsupported Media Type" in no_content_type.text

    for content in ("", "{"):
        response = client.post("/auth/login", content=content, headers={"Content-Type": "application/json"})
        assert response.status_code == 400
        assert response.headers["content-type"].startswith("text/html")
        assert "Bad Request" in response.text
        assert response.status_code != 422

    unauthenticated = client.post("/songs/add", content="{")
    assert unauthenticated.status_code == 401
    assert unauthenticated.json() == {"message": "未提供有效凭证"}

    invalid_token = client.post("/songs/add", content="{", headers={"Authorization": "Bearer invalid"})
    assert invalid_token.status_code == 401
    assert invalid_token.json() == {"message": "无效的 Token"}

    authenticated_without_json_type = client.post("/songs/add", content="{}", headers=auth_headers)
    assert authenticated_without_json_type.status_code == 415
    authenticated_empty_json = client.post(
        "/songs/add",
        content="",
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert authenticated_empty_json.status_code == 400
    assert authenticated_empty_json.headers["content-type"].startswith("text/html")


def test_flask_html_not_found_pagination_and_empty_bearer(client, auth_headers):
    missing = client.post("/songs/delete", json={"id": 999999}, headers=auth_headers)
    assert missing.status_code == 404
    assert missing.headers["content-type"].startswith("text/html")
    assert "404 Not Found" in missing.text
    assert "歌曲不存在" not in missing.text

    pagination = client.get("/messages/get?page=0&limit=-3").json()["pagination"]
    assert pagination["page"] == 1
    assert pagination["limit"] == 20

    empty_bearer = client.get("/auth/me", headers={"Authorization": "Bearer "})
    assert empty_bearer.status_code == 401
    assert empty_bearer.json() == {"message": "无效的 Token"}
    for authorization in ("Bearer", "Token abc"):
        response = client.get("/auth/me", headers={"Authorization": authorization})
        assert response.status_code == 401
        assert response.json() == {"message": "未提供有效凭证"}
