# Tests for global exception handlers.

import uuid

from fastapi import APIRouter
from fastapi.routing import APIRoute
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

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


def ensure_route(path: str, handler):
	if any(isinstance(route, APIRoute) and route.path == path for route in app.router.routes):
		return
	router = APIRouter()
	router.add_api_route(path, handler, methods=["POST"])
	app.include_router(router)


def test_validation_error_format():
	response = client.post("/api/v1/users/", json={"email": "missing-password"})
	assert response.status_code == 422
	payload = response.json()
	assert payload["code"] == "validation_error"
	assert payload["detail"] == "Validation error"
	assert "errors" in payload


def test_http_exception_format():
	email = f"user-{uuid.uuid4().hex}@example.com"
	register_user(email)
	tokens = login_user(email)
	response = client.get(
		"/api/v1/items/999999",
		headers={"Authorization": f"Bearer {tokens['access_token']}"},
	)
	assert response.status_code == 404
	payload = response.json()
	assert payload["code"] == "http_error"
	assert payload["detail"] == "Item not found"


def test_integrity_error_handler():
	path = "/_test/integrity"

	def raise_integrity():
		raise IntegrityError("stmt", {"email": "dup"}, Exception("boom"))

	ensure_route(path, raise_integrity)
	response = client.post(path, json={})
	assert response.status_code == 409
	payload = response.json()
	assert payload["code"] == "db_integrity_error"
	assert payload["detail"] == "Database integrity error"


def test_sqlalchemy_error_handler():
	path = "/_test/sqlalchemy"

	def raise_sqlalchemy():
		raise SQLAlchemyError("boom")

	ensure_route(path, raise_sqlalchemy)
	response = client.post(path, json={})
	assert response.status_code == 500
	payload = response.json()
	assert payload["code"] == "db_error"
	assert payload["detail"] == "Database error"
