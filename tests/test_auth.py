"""Tests for authentication flows and error handling."""

import uuid

from fastapi.testclient import TestClient
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.routing import APIRoute

from app.main import app
from app.api.deps import get_db
from app.core.security import get_password_hash
from app.db.models import User
from app.db.session import SessionLocal

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


def test_login_invalid_credentials():
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrong"},
    )
    assert response.status_code == 401


def test_register_duplicate_email_fails():
    email = f"user-{uuid.uuid4().hex}@example.com"
    register_user(email)
    response = client.post(
        "/api/v1/users/",
        json={"email": email, "password": "password123"},
    )
    assert response.status_code == 400


def test_me_requires_auth():
    response = client.get("/api/v1/users/me")
    assert response.status_code == 401


def test_register_login_and_access_me():
    email = f"user-{uuid.uuid4().hex}@example.com"
    register_user(email)
    tokens = login_user(email)
    access_token = tokens["access_token"]

    me_response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == email


def test_refresh_flow_and_logout_revokes():
    email = f"user-{uuid.uuid4().hex}@example.com"
    register_user(email)
    tokens = login_user(email)
    refresh_token = tokens["refresh_token"]

    refresh_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_response.status_code == 200
    new_refresh = refresh_response.json()["refresh_token"]

    logout_response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": new_refresh},
    )
    assert logout_response.status_code == 204

    refresh_after_logout = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh},
    )
    assert refresh_after_logout.status_code == 401


def test_refresh_token_reuse_revokes_all():
    email = f"user-{uuid.uuid4().hex}@example.com"
    register_user(email)
    tokens = login_user(email)
    original_refresh = tokens["refresh_token"]

    rotate_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert rotate_response.status_code == 200
    new_refresh = rotate_response.json()["refresh_token"]

    reuse_response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": original_refresh},
    )
    assert reuse_response.status_code == 401

    refresh_after_reuse = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": new_refresh},
    )
    assert refresh_after_reuse.status_code == 401


def test_refresh_with_invalid_token():
    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 401


def test_logout_with_invalid_token_is_idempotent():
    response = client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": "invalid-token"},
    )
    assert response.status_code == 204


def test_me_rejects_invalid_token():
    response = client.get(
        "/api/v1/users/me",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401


def test_db_rollback_on_exception():
    # Ensure the request error rolls back the DB transaction.
    route_path = "/_test/rollback"
    if not any(
        isinstance(route, APIRoute) and route.path == route_path for route in app.router.routes
    ):
        router = APIRouter()

        @router.post(route_path)
        def force_rollback(payload: dict, db=Depends(get_db)):
            user = User(
                email=payload["email"],
                hashed_password=get_password_hash("password123"),
            )
            db.add(user)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="force rollback",
            )

        app.include_router(router)

    email = f"rollback-{uuid.uuid4().hex}@example.com"
    response = client.post(route_path, json={"email": email})
    assert response.status_code == 400

    db = SessionLocal()
    try:
        found = db.query(User).filter(User.email == email).first()
        assert found is None
    finally:
        db.close()
