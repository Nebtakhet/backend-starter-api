"""Shared FastAPI dependencies for database sessions and auth."""

from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.schemas.auth import TokenPayload
from app.services.user_service import get_user_by_id


def get_db() -> Generator[Session, None, None]:
    """Provide a database session per request.

    The session is automatically closed after the request.
    Commits should be done explicitly in services/endpoints.
    Rollback happens automatically on exceptions.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    # Decode the JWT and load the current user or fail with 401.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
            options={
                "require_exp": True,
                "require_iat": True,
                "require_sub": True,
                "leeway": settings.CLOCK_SKEW_SECONDS,
            },
        )
        subject = payload.get("sub")
        if not isinstance(subject, str):
            raise credentials_exception
        token_data = TokenPayload(sub=subject)
    except JWTError:
        raise credentials_exception
    user = get_user_by_id(db, int(token_data.sub))
    if user is None:
        raise credentials_exception
    return user
