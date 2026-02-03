from datetime import timedelta, timezone

from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, hash_refresh_token, verify_password
from app.db.models import RefreshToken, User
from app.schemas.auth import Token
from app.services.user_service import get_user_by_email
from app.utils.time import utcnow


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_token(db: Session, user: User) -> Token:
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token()
    store_refresh_token(db, user.id, refresh_token)
    return Token(access_token=access_token, refresh_token=refresh_token)


def store_refresh_token(db: Session, user_id: int, raw_token: str) -> RefreshToken:
    expires_at = utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    token_hash = hash_refresh_token(raw_token)
    record = RefreshToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def rotate_refresh_token(db: Session, raw_token: str) -> Token | None:
    token_hash = hash_refresh_token(raw_token)
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )
    if not record:
        return None
    expires_at = record.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if record.revoked:
        revoke_all_refresh_tokens(db, record.user_id)
        return None
    if expires_at <= utcnow():
        return None
    record.revoked = True
    access_token = create_access_token(subject=str(record.user_id))
    new_refresh = create_refresh_token()
    store_refresh_token(db, record.user_id, new_refresh)
    db.commit()
    return Token(access_token=access_token, refresh_token=new_refresh)


def revoke_refresh_token(db: Session, raw_token: str) -> bool:
    token_hash = hash_refresh_token(raw_token)
    record = (
        db.query(RefreshToken)
        .filter(RefreshToken.token_hash == token_hash)
        .first()
    )
    if not record or record.revoked:
        return False
    record.revoked = True
    db.commit()
    return True


def revoke_all_refresh_tokens(db: Session, user_id: int) -> None:
    db.query(RefreshToken).filter(RefreshToken.user_id == user_id).update(
        {RefreshToken.revoked: True}
    )
    db.commit()
