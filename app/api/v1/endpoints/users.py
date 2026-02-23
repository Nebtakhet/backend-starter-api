# User registration and profile endpoints.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.models import User
from app.schemas.user import UserCreate, UserOut, UserPasswordChange
from app.services.user_service import (
    change_user_password,
    create_user,
    get_user_by_email,
    list_users,
)

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(data: UserCreate, db: AsyncSession = Depends(get_db)) -> User:
    if await get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return await create_user(db, data)


@router.get("/", response_model=list[UserOut])
async def read_users(db: AsyncSession = Depends(get_db)) -> list[User]:
    return await list_users(db)


@router.get("/me", response_model=UserOut)
def read_me(current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    data: UserPasswordChange,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    changed = await change_user_password(
        db, current_user, data.current_password, data.new_password
    )
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    return None
