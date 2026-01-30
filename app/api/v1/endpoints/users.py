from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.schemas.user import UserCreate, UserOut
from app.services.user_service import create_user, get_user_by_email, list_users

router = APIRouter()


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(data: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    if get_user_by_email(db, data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return create_user(db, data)


@router.get("/", response_model=list[UserOut])
def read_users(db: Session = Depends(get_db)) -> list[UserOut]:
    return list_users(db)


@router.get("/me", response_model=UserOut)
def read_me(current_user=Depends(get_current_user)) -> UserOut:
    return current_user
