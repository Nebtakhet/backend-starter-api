from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.schemas.auth import Token
from app.services.user_service import get_user_by_email


def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_user_token(user) -> Token:
    access_token = create_access_token(subject=str(user.id))
    return Token(access_token=access_token)
