# Unit tests for user endpoint functions.

import asyncio
import uuid

import pytest
from fastapi import HTTPException, status

from app.api.v1.endpoints import users as users_endpoint
from app.core.security import verify_password
from app.db.session import SessionLocal
from app.schemas.user import UserCreate, UserPasswordChange
from app.services.user_service import get_user_by_id


def _run(coro):
    return asyncio.run(coro)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def test_users_endpoint_functions_cover_register_list_and_password_change():
    async def _scenario() -> None:
        async with SessionLocal() as db:
            created = await users_endpoint.register_user(
                UserCreate(email=_email("users-register"), password="StrongPass123!"),
                db,
            )
            assert created.id is not None

            users = await users_endpoint.read_users(db)
            assert any(user.id == created.id for user in users)

            me = users_endpoint.read_me(created)
            assert me.id == created.id

            await users_endpoint.change_password(
                UserPasswordChange(
                    current_password="StrongPass123!",
                    new_password="NewStrongPass123!",
                ),
                db,
                created,
            )

            refreshed = await get_user_by_id(db, created.id)
            assert refreshed is not None
            assert verify_password("NewStrongPass123!", refreshed.hashed_password)

    _run(_scenario())


def test_register_user_rejects_duplicate_email():
    async def _scenario() -> None:
        email = _email("users-duplicate")
        async with SessionLocal() as db:
            await users_endpoint.register_user(
                UserCreate(email=email, password="StrongPass123!"), db
            )
            with pytest.raises(HTTPException) as exc:
                await users_endpoint.register_user(
                    UserCreate(email=email, password="StrongPass123!"), db
                )
            assert exc.value.status_code == status.HTTP_400_BAD_REQUEST

    _run(_scenario())
