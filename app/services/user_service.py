# User service functions for basic user operations.

from sqlalchemy.orm import Session

from app.core.security import get_password_hash, verify_password
from app.db.models import User
from app.schemas.user import UserCreate


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, data: UserCreate) -> User:
    user = User(email=data.email, hashed_password=get_password_hash(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).all()


def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> bool:
    if not verify_password(current_password, user.hashed_password):
        return False
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    db.refresh(user)
    return True
