# Tests for API dependency helpers.

import asyncio
import uuid

import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.security import get_password_hash
from app.db.models import User


def _run(coro):
    return asyncio.run(coro)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def _fake_db() -> AsyncSession:
    return AsyncSession()


def test_get_current_user_raises_for_non_string_subject(monkeypatch):
    monkeypatch.setattr(deps.jwt, "decode", lambda *args, **kwargs: {"sub": 123})

    async def _scenario() -> None:
        with pytest.raises(HTTPException) as exc:
            await deps.get_current_user(db=_fake_db(), token="irrelevant")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    _run(_scenario())


def test_get_current_user_raises_when_user_missing(monkeypatch):
    monkeypatch.setattr(deps.jwt, "decode", lambda *args, **kwargs: {"sub": "123"})

    async def _fake_get_user_by_id(db, user_id):
        return None

    monkeypatch.setattr(deps, "get_user_by_id", _fake_get_user_by_id)

    async def _scenario() -> None:
        with pytest.raises(HTTPException) as exc:
            await deps.get_current_user(db=_fake_db(), token="irrelevant")
        assert exc.value.status_code == status.HTTP_401_UNAUTHORIZED

    _run(_scenario())


def test_get_current_user_returns_user(monkeypatch):
    user = User(
        id=321, email=_email("deps-user"), hashed_password=get_password_hash("StrongPass123!")
    )
    monkeypatch.setattr(deps.jwt, "decode", lambda *args, **kwargs: {"sub": "321"})

    async def _fake_get_user_by_id(db, user_id):
        assert user_id == 321
        return user

    monkeypatch.setattr(deps, "get_user_by_id", _fake_get_user_by_id)

    returned = _run(deps.get_current_user(db=_fake_db(), token="irrelevant"))
    assert returned.id == user.id
