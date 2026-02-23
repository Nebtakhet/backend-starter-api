# Authentication endpoints (login, refresh, logout).

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import settings
from app.schemas.auth import LoginRequest, RefreshRequest, Token
from app.services.auth_service import (
    authenticate_user,
    create_user_token,
    revoke_refresh_token,
    rotate_refresh_token,
)

from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/login", response_model=Token)
@limiter.limit(settings.AUTH_LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    data: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return await create_user_token(db, user)


@router.post("/refresh", response_model=Token)
@limiter.limit(settings.AUTH_REFRESH_RATE_LIMIT)
async def refresh_token(
    request: Request,
    data: RefreshRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    token = await rotate_refresh_token(db, data.refresh_token)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    return token


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(data: RefreshRequest, db: AsyncSession = Depends(get_db)) -> None:
    await revoke_refresh_token(db, data.refresh_token)
    return None
