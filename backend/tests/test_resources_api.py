from __future__ import annotations

import pytest

RESOURCES = [
    (
        "links",
        {"name": "Link A", "url": "https://a.test", "description": "desc", "icon": "icon.png"},
        {"name": "Link B"},
        "name",
    ),
    (
        "songs",
        {"title": "Song A", "artist": "Artist", "url": "song.mp3", "cover": "cover.jpg"},
        {"title": "Song B"},
        "title",
    ),
    (
        "skills",
        {"name": "Python", "logo": "python.svg", "url": "https://python.org"},
        {"name": "FastAPI"},
        "name",
    ),
    (
        "tools",
        {"title": "Tool A", "subtitle": "Sub", "url": "https://tool.test", "imgUrl": "tool.png", "content": "Body"},
        {"imgUrl": "new.png"},
        "title",
    ),
]


@pytest.mark.parametrize(("resource", "payload", "update", "changed_field"), RESOURCES)
def test_resource_crud(client, auth_headers, resource, payload, update, changed_field):
    empty = client.get(f"/{resource}")
    assert empty.status_code == 200
    assert empty.json() == {"items": []}

    unauthorized = client.post(f"/admin/{resource}", json=payload)
    assert unauthorized.status_code == 401

    created = client.post(f"/admin/{resource}", json=payload, headers=auth_headers)
    assert created.status_code == 201, created.text
    item = created.json()
    item_id = item["id"]
    assert item[changed_field] == payload[changed_field]
    if resource == "tools":
        assert item["imgUrl"] == payload["imgUrl"]

    listed = client.get(f"/{resource}")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == item_id

    updated = client.patch(f"/admin/{resource}/{item_id}", json=update, headers=auth_headers)
    assert updated.status_code == 200
    for key, value in update.items():
        assert updated.json()[key] == value
    for key, value in payload.items():
        if key not in update:
            assert updated.json()[key] == value

    missing = client.patch(f"/admin/{resource}/999999", json=update, headers=auth_headers)
    assert missing.status_code == 404

    deleted = client.delete(f"/admin/{resource}/{item_id}", headers=auth_headers)
    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get(f"/{resource}").json() == {"items": []}

    assert client.delete(f"/admin/{resource}/{item_id}", headers=auth_headers).status_code == 404


@pytest.mark.parametrize(("resource", "payload", "update", "changed_field"), RESOURCES)
def test_resource_validation(client, auth_headers, resource, payload, update, changed_field):
    invalid = dict(payload)
    invalid.pop(changed_field)
    assert client.post(f"/admin/{resource}", json=invalid, headers=auth_headers).status_code == 422


def test_bulk_create_and_sorting(client, auth_headers):
    songs = [
        {"title": "S1", "artist": "A", "url": "s1.mp3", "cover": "c1.jpg"},
        {"title": "S2", "artist": "B", "url": "s2.mp3", "cover": "c2.jpg"},
    ]
    created = client.post("/admin/songs/bulk", json=songs, headers=auth_headers)
    assert created.status_code == 201
    assert created.json() == {"created": 2}
    assert [item["title"] for item in client.get("/songs").json()["items"]] == ["S2", "S1"]

    skills = [
        {"name": "K1", "logo": "k1.svg", "url": "https://k1.test"},
        {"name": "K2", "logo": "k2.svg", "url": "https://k2.test"},
    ]
    assert client.post("/admin/skills/bulk", json=skills, headers=auth_headers).json() == {"created": 2}
    assert [item["name"] for item in client.get("/skills").json()["items"]] == ["K1", "K2"]

    tools = [
        {"title": "T1", "subtitle": "S1", "url": "https://t1.test", "imgUrl": "t1.png", "content": "C1"},
        {"title": "T2", "subtitle": "S2", "url": "https://t2.test", "imgUrl": "t2.png", "content": "C2"},
    ]
    assert client.post("/admin/tools/bulk", json=tools, headers=auth_headers).json() == {"created": 2}
    assert [item["title"] for item in client.get("/tools").json()["items"]] == ["T2", "T1"]
