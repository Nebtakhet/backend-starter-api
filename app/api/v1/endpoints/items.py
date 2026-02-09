"""Item CRUD endpoints scoped to the current user."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.db.models import Item, User
from app.schemas.item import ItemCreate, ItemOut, ItemUpdate

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = Item(
        title=data.title,
        description=data.description,
        owner_id=current_user.id,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[ItemOut])
def read_items(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ItemOut]:
    return db.query(Item).filter(Item.owner_id == current_user.id).all()


@router.get("/{item_id}", response_model=ItemOut)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    return item


@router.put("/{item_id}", response_model=ItemOut)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ItemOut:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    if data.title is not None:
        item.title = data.title
    if data.description is not None:
        item.description = data.description
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item or item.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    db.delete(item)
    db.commit()
    return None
