from __future__ import annotations


def test_post_crud_and_flat_serialization(client, auth_headers):
    payload = {
        "id": 101,
        "title": "Post",
        "description": "Desc",
        "image": "image.png",
        "tags": ["python"],
        "category": "Code",
        "content": "Body",
    }
    created = client.post("/admin/posts", json=payload, headers=auth_headers)
    assert created.status_code == 201, created.text
    body = created.json()
    assert body["id"] == 101
    assert body["title"] == "Post"
    assert body["tags"] == ["python"]
    assert "metadata" not in body

    listed = client.get("/posts")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["id"] == 101

    detail = client.get("/posts/101")
    assert detail.status_code == 200
    assert detail.json()["title"] == "Post"

    updated = client.patch("/admin/posts/101", json={"title": "Updated", "tags": ["api"]}, headers=auth_headers)
    assert updated.status_code == 200
    assert updated.json()["title"] == "Updated"
    assert updated.json()["tags"] == ["api"]
    assert updated.json()["description"] == "Desc"

    deleted = client.delete("/admin/posts/101", headers=auth_headers)
    assert deleted.status_code == 204
    assert client.get("/posts/101").status_code == 404


def test_post_validation_and_missing_items(client, auth_headers):
    assert client.post("/admin/posts", json={"id": "not-an-int", "title": "P", "content": "C"}, headers=auth_headers).status_code == 422
    assert client.post("/admin/posts", json={"id": 1, "title": "", "content": "C"}, headers=auth_headers).status_code == 422
    assert client.get("/posts/999999").status_code == 404
    assert client.patch("/admin/posts/999999", json={"title": "X"}, headers=auth_headers).status_code == 404
    assert client.delete("/admin/posts/999999", headers=auth_headers).status_code == 404
