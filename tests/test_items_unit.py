# Unit tests for item endpoint functions.

import asyncio
import uuid

import pytest
from fastapi import HTTPException, status

from app.api.v1.endpoints import items as items_endpoint
from app.core.security import get_password_hash
from app.db.models import User
from app.db.session import SessionLocal
from app.schemas.item import ItemCreate, ItemUpdate


def _run(coro):
    return asyncio.run(coro)


def _email(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex}@example.com"


def test_items_endpoint_functions_cover_success_and_not_found_paths():
    async def _scenario() -> None:
        async with SessionLocal() as db:
            owner = User(
                email=_email("items-owner"), hashed_password=get_password_hash("StrongPass123!")
            )
            other = User(
                email=_email("items-other"), hashed_password=get_password_hash("StrongPass123!")
            )
            db.add(owner)
            db.add(other)
            await db.commit()
            await db.refresh(owner)
            await db.refresh(other)
            owner_user = User(
                id=owner.id,
                email=_email("items-owner-stub"),
                hashed_password=get_password_hash("StrongPass123!"),
            )
            other_user = User(
                id=other.id,
                email=_email("items-other-stub"),
                hashed_password=get_password_hash("StrongPass123!"),
            )

            created = await items_endpoint.create_item(
                ItemCreate(title="My Item", description="Created by owner"),
                db,
                owner_user,
            )
            assert created.id is not None

            page = await items_endpoint.read_items(0, 10, db, owner_user)
            assert page.total >= 1
            assert any(item.id == created.id for item in page.items)

            fetched = await items_endpoint.read_item(created.id, db, owner_user)
            assert fetched.id == created.id

            updated = await items_endpoint.update_item(
                created.id,
                ItemUpdate(description="Updated description"),
                db,
                owner_user,
            )
            assert updated.description == "Updated description"

            with pytest.raises(HTTPException) as read_forbidden:
                await items_endpoint.read_item(created.id, db, other_user)
            assert read_forbidden.value.status_code == status.HTTP_404_NOT_FOUND

            with pytest.raises(HTTPException) as update_missing:
                await items_endpoint.update_item(
                    999999999,
                    ItemUpdate(title="x"),
                    db,
                    owner_user,
                )
            assert update_missing.value.status_code == status.HTTP_404_NOT_FOUND

            await items_endpoint.delete_item(created.id, db, owner_user)

            with pytest.raises(HTTPException) as delete_missing:
                await items_endpoint.delete_item(created.id, db, owner_user)
            assert delete_missing.value.status_code == status.HTTP_404_NOT_FOUND

    _run(_scenario())
