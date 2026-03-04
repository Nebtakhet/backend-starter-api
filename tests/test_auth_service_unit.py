# Unit tests for auth service branch behavior.

import asyncio
from datetime import timedelta
import uuid

from sqlalchemy import select

from app.core.security import get_password_hash, hash_refresh_token
from app.db.models import RefreshToken, User
from app.db.session import SessionLocal
from app.services.auth_service import (
    authenticate_user,
    create_user_token,
    revoke_all_refresh_tokens,
    revoke_refresh_token,
    rotate_refresh_token,
)
from app.utils.time import utcnow


def _run(coro):
    return asyncio.run(coro)


async def _create_user(email: str, password: str = "StrongPass123!") -> User:
    async with SessionLocal() as db:
        user = User(email=email, hashed_password=get_password_hash(password))
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user


async def _insert_refresh_token(
    user_id: int,
    raw_token: str,
    *,
    revoked: bool = False,
    expires_delta: timedelta = timedelta(days=1),
) -> None:
    async with SessionLocal() as db:
        record = RefreshToken(
            user_id=user_id,
            token_hash=hash_refresh_token(raw_token),
            revoked=revoked,
            expires_at=utcnow() + expires_delta,
        )
        db.add(record)
        await db.commit()


async def _list_user_tokens(user_id: int) -> list[RefreshToken]:
    async with SessionLocal() as db:
        result = await db.execute(select(RefreshToken).where(RefreshToken.user_id == user_id))
        return list(result.scalars().all())


async def _get_user_by_email(email: str) -> User | None:
    async with SessionLocal() as db:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()


def test_authenticate_user_returns_none_for_missing_user():
    async def _scenario():
        async with SessionLocal() as db:
            user = await authenticate_user(db, "missing@example.com", "StrongPass123!")
            assert user is None

    _run(_scenario())


def test_authenticate_user_returns_none_for_invalid_password():
    email = f"auth-invalid-{uuid.uuid4().hex}@example.com"
    _run(_create_user(email, "StrongPass123!"))

    async def _scenario():
        async with SessionLocal() as db:
            user = await authenticate_user(db, email, "WrongPass123!")
            assert user is None

    _run(_scenario())


def test_authenticate_user_returns_user_for_valid_credentials():
    email = f"auth-valid-{uuid.uuid4().hex}@example.com"
    created = _run(_create_user(email, "StrongPass123!"))

    async def _scenario():
        async with SessionLocal() as db:
            user = await authenticate_user(db, email, "StrongPass123!")
            assert user is not None
            assert user.id == created.id

    _run(_scenario())


def test_create_user_token_persists_refresh_token():
    email = f"token-create-{uuid.uuid4().hex}@example.com"
    created = _run(_create_user(email, "StrongPass123!"))

    async def _scenario():
        async with SessionLocal() as db:
            user = await _get_user_by_email(email)
            assert user is not None
            token = await create_user_token(db, user)
            assert token.access_token
            assert token.refresh_token

        records = await _list_user_tokens(created.id)
        assert records
        token_hashes = {record.token_hash for record in records}
        assert hash_refresh_token(token.refresh_token) in token_hashes

    _run(_scenario())


def test_rotate_refresh_token_returns_none_when_missing():
    async def _scenario():
        async with SessionLocal() as db:
            token = await rotate_refresh_token(db, f"missing-{uuid.uuid4().hex}")
            assert token is None

    _run(_scenario())


def test_revoke_refresh_token_returns_false_for_missing_token():
    async def _scenario():
        async with SessionLocal() as db:
            revoked = await revoke_refresh_token(db, f"missing-{uuid.uuid4().hex}")
            assert revoked is False

    _run(_scenario())


def test_revoke_all_refresh_tokens_marks_all_revoked():
    email = f"revoke-all-{uuid.uuid4().hex}@example.com"
    created = _run(_create_user(email, "StrongPass123!"))
    _run(_insert_refresh_token(created.id, f"tok-a-{uuid.uuid4().hex}"))
    _run(_insert_refresh_token(created.id, f"tok-b-{uuid.uuid4().hex}"))

    async def _scenario():
        async with SessionLocal() as db:
            await revoke_all_refresh_tokens(db, created.id)

        records = await _list_user_tokens(created.id)
        assert len(records) >= 2
        assert all(record.revoked for record in records)

    _run(_scenario())


def test_rotate_refresh_token_revoked_record_revokes_all_and_returns_none():
    email = f"rotate-revoked-{uuid.uuid4().hex}@example.com"
    created = _run(_create_user(email, "StrongPass123!"))
    revoked_token = f"revoked-{uuid.uuid4().hex}"
    active_token = f"active-{uuid.uuid4().hex}"
    _run(_insert_refresh_token(created.id, revoked_token, revoked=True))
    _run(_insert_refresh_token(created.id, active_token, revoked=False))

    async def _scenario():
        async with SessionLocal() as db:
            token = await rotate_refresh_token(db, revoked_token)
            assert token is None

        records = await _list_user_tokens(created.id)
        assert records
        assert all(record.revoked for record in records)

    _run(_scenario())


def test_rotate_refresh_token_expired_record_returns_none():
    email = f"rotate-expired-{uuid.uuid4().hex}@example.com"
    created = _run(_create_user(email, "StrongPass123!"))
    expired_token = f"expired-{uuid.uuid4().hex}"
    _run(_insert_refresh_token(created.id, expired_token, expires_delta=timedelta(minutes=-1)))

    async def _scenario():
        async with SessionLocal() as db:
            token = await rotate_refresh_token(db, expired_token)
            assert token is None

    _run(_scenario())
