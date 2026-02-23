# Item CRUD endpoints scoped to the current user.

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.db.models import Item, User
from app.schemas.item import ItemCreate, ItemListResponse, ItemOut, ItemUpdate

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
async def create_item(
    data: ItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Item:
    item = Item(
        title=data.title,
        description=data.description,
        owner_id=current_user.id,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


@router.get("/", response_model=ItemListResponse)
async def read_items(
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Max items to return")] = 50,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemListResponse:
    # List items for the current user with pagination.
    total_result = await db.execute(
        select(func.count()).select_from(Item).where(Item.owner_id == current_user.id)
    )
    total = int(total_result.scalar_one())
    items_result = await db.execute(
        select(Item).where(Item.owner_id == current_user.id).offset(skip).limit(limit)
    )
    items = list(items_result.scalars().all())
    # Convert ORM models to Pydantic schemas for type safety
    item_schemas = [ItemOut.model_validate(item) for item in items]
    return ItemListResponse(items=item_schemas, total=total, skip=skip, limit=limit)


@router.get("/{item_id}", response_model=ItemOut)
async def read_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
async def update_item(
    item_id: int,
    data: ItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Item:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if data.title is not None:
        item.title = data.title
    if data.description is not None:
        item.description = data.description
    await db.commit()
    await db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    result = await db.execute(select(Item).where(Item.id == item_id))
    item = result.scalars().first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    await db.delete(item)
    await db.commit()
    return None
