from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import LoginRequest, Token
from app.services.auth_service import authenticate_user, create_user_token

router = APIRouter()


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    return create_user_token(user)
