# Tests for item endpoints and access control.

import uuid

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


# Helpers for common auth flows.
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
	data = response.json()
	assert data["status"] == "ok"
	assert "database" in data
	assert data["database"] in ["connected", "disconnected"]


def test_item_crud_and_ownership():
	# Verify ownership checks for CRUD operations.
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
	list_one_data = list_one.json()
	assert "items" in list_one_data
	assert "total" in list_one_data
	assert any(item["id"] == item_id for item in list_one_data["items"])

	list_two = client.get("/api/v1/items/", headers=headers_two)
	assert list_two.status_code == 200
	list_two_data = list_two.json()
	assert all(item["id"] != item_id for item in list_two_data["items"])

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


def test_items_require_auth():
	# Ensure item routes reject unauthenticated access.
	list_response = client.get("/api/v1/items/")
	assert list_response.status_code == 401

	create_response = client.post(
		"/api/v1/items/",
		json={"title": "No auth", "description": "Denied"},
	)
	assert create_response.status_code == 401

	invalid_headers = {"Authorization": "Bearer invalid"}
	list_invalid = client.get("/api/v1/items/", headers=invalid_headers)
	assert list_invalid.status_code == 401


def test_item_not_found_for_owner():
	email = f"user-{uuid.uuid4().hex}@example.com"
	register_user(email)
	tokens = login_user(email)
	headers = {"Authorization": f"Bearer {tokens['access_token']}"}

	response = client.get("/api/v1/items/999999", headers=headers)
	assert response.status_code == 404
