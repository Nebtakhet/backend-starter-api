# Authentication service functions for login and token lifecycle.

from datetime import timedelta

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


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
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


async def store_refresh_token(
    db: AsyncSession,
    user_id: int,
    raw_token: str,
    *,
    commit: bool = True,
) -> RefreshToken:
    expires_at = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_hash = hash_refresh_token(raw_token)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    if commit:
        await db.commit()
        await db.refresh(record)
    else:
        await db.flush()
    return record


async def rotate_refresh_token(db: AsyncSession, raw_token: str) -> Token | None:
    token_hash = hash_refresh_token(raw_token)
    async with db.begin():
        claim_result = await db.execute(
            update(RefreshToken)
            .where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.revoked.is_(False),
                RefreshToken.expires_at > utcnow(),
            )
            .values(revoked=True)
            .returning(RefreshToken.user_id)
        )
        user_id = claim_result.scalar_one_or_none()
        if user_id is not None:
            access_token = create_access_token(subject=str(user_id))
            new_refresh = create_refresh_token()
            await store_refresh_token(db, user_id, new_refresh, commit=False)
            return Token(access_token=access_token, refresh_token=new_refresh)

        record_result = await db.execute(
            select(RefreshToken).where(RefreshToken.token_hash == token_hash)
        )
        record: RefreshToken | None = record_result.scalars().first()
        if not record:
            return None

        if record.revoked:
            # Defensive: a reused refresh token invalidates all sessions for the user.
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.user_id == record.user_id)
                .values(revoked=True)
            )
            return None

        return None


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
