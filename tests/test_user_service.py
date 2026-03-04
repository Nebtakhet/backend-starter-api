# Tests for user service functions.

import asyncio
import uuid

from app.core.security import get_password_hash
from app.db.models import User
from app.db.session import SessionLocal
from app.services.user_service import change_user_password


def _run(coro):
    return asyncio.run(coro)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def test_change_user_password_returns_false_for_wrong_current_password():
    async def _scenario() -> None:
        async with SessionLocal() as db:
            user = User(
                email=_email("users-wrong-password"),
                hashed_password=get_password_hash("StrongPass123!"),
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

            changed = await change_user_password(db, user, "WrongPass123!", "NewStrongPass123!")
            assert changed is False

    _run(_scenario())
