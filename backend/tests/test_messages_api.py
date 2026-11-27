from __future__ import annotations

import hashlib
from datetime import datetime

from app.models import Message


def test_message_validation(client):
    assert client.post("/messages", json={"username": "", "email": "a@test.com", "content": "x"}).status_code == 422
    assert client.post("/messages", json={"username": "A", "email": "bad", "content": "x"}).status_code == 422
    assert client.post("/messages", json={"username": "A", "email": "a@test.com", "content": ""}).status_code == 422
    response = client.post(
        "/messages",
        json={"username": "A", "email": "a@test.com", "content": "x", "website_url": "bad"},
    )
    assert response.status_code == 422


def test_message_create_hash_pagination_and_order(client, session_factory):
    first = client.post("/messages", json={"username": " First ", "email": "First@Test.com", "content": " One "})
    second = client.post(
        "/messages",
        json={"username": "Second", "email": "second@test.com", "content": "Two", "website_url": "https://example.com"},
    )
    assert first.status_code == second.status_code == 201
    assert first.json()["username"] == "First"
    assert "email" not in first.json()
    assert first.json()["email_hash"] == hashlib.sha256(b"first@test.com").hexdigest()

    with session_factory() as session:
        session.get(Message, first.json()["id"]).created_at = datetime(2024, 1, 1)
        session.get(Message, second.json()["id"]).created_at = datetime(2024, 1, 2)
        session.commit()

    response = client.get("/messages?page=1&limit=1")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert body["page"] == 1
    assert body["limit"] == 1
    assert body["pages"] == 2
    assert body["items"][0]["username"] == "Second"
    assert "email" not in body["items"][0]

    assert client.get("/messages?page=0").status_code == 422
    assert client.get("/messages?limit=0").status_code == 422
