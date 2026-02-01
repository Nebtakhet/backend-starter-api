import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def register_user(email: str, password: str = "password123") -> None:
    response = client.post(
        "/api/v1/users/",
        json={"email": email, "password": password},
    )
    assert response.status_code == 201


def login_user(email: str, password: str = "password123") -> dict:
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_item_crud_and_ownership():
    email_one = f"user-{uuid.uuid4().hex}@example.com"
    email_two = f"user-{uuid.uuid4().hex}@example.com"
    register_user(email_one)
    register_user(email_two)

    tokens_one = login_user(email_one)
    tokens_two = login_user(email_two)

    headers_one = {"Authorization": f"Bearer {tokens_one['access_token']}"}
    headers_two = {"Authorization": f"Bearer {tokens_two['access_token']}"}

    create_response = client.post(
        "/api/v1/items/",
        json={"title": "Test", "description": "Owned by user one"},
        headers=headers_one,
    )
    assert create_response.status_code == 201
    item_id = create_response.json()["id"]

    list_one = client.get("/api/v1/items/", headers=headers_one)
    assert list_one.status_code == 200
    assert any(item["id"] == item_id for item in list_one.json())

    list_two = client.get("/api/v1/items/", headers=headers_two)
    assert list_two.status_code == 200
    assert all(item["id"] != item_id for item in list_two.json())

    get_other = client.get(f"/api/v1/items/{item_id}", headers=headers_two)
    assert get_other.status_code == 404

    update_other = client.put(
        f"/api/v1/items/{item_id}",
        json={"title": "Hacked"},
        headers=headers_two,
    )
    assert update_other.status_code == 404

    delete_other = client.delete(f"/api/v1/items/{item_id}", headers=headers_two)
    assert delete_other.status_code == 404

    update_own = client.put(
        f"/api/v1/items/{item_id}",
        json={"title": "Updated"},
        headers=headers_one,
    )
    assert update_own.status_code == 200
    assert update_own.json()["title"] == "Updated"

    delete_own = client.delete(f"/api/v1/items/{item_id}", headers=headers_one)
    assert delete_own.status_code == 204
