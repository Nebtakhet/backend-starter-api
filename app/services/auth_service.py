# Authentication service functions for login and token lifecycle.

from datetime import timedelta, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.db.models import RefreshToken, User
from app.schemas.auth import Token
from app.services.user_service import get_user_by_email
from app.utils.time import utcnow


async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


async def create_user_token(db: AsyncSession, user: User) -> Token:
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token()
    await store_refresh_token(db, user.id, refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


async def store_refresh_token(db: AsyncSession, user_id: int, raw_token: str) -> RefreshToken:
    expires_at = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_hash = hash_refresh_token(raw_token)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> Token | None:
    token_hash = hash_refresh_token(raw_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    record = result.scalars().first()
    if not record:
        return None
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if record.revoked:
        # Defensive: a reused refresh token invalidates all sessions for the user.
        await revoke_all_refresh_tokens(db, record.user_id)
        return None
    if expires_at <= utcnow():
        return None
    record.revoked = True
    access_token = create_access_token(subject=str(record.user_id))
    new_refresh = create_refresh_token()
    await store_refresh_token(db, record.user_id, new_refresh)
    await db.commit()
    return Token(access_token=access_token, refresh_token=new_refresh)


async def revoke_refresh_token(db: AsyncSession, raw_token: str) -> bool:
    token_hash = hash_refresh_token(raw_token)
    result = await db.execute(select(RefreshToken).where(RefreshToken.token_hash == token_hash))
    record = result.scalars().first()
    if not record or record.revoked:
        return False
    record.revoked = True
    await db.commit()
    return True


async def revoke_all_refresh_tokens(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(RefreshToken).where(RefreshToken.user_id == user_id).values(revoked=True)
    )
    await db.commit()
