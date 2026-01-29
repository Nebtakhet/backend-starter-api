from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.db.models import Item, User
from app.schemas.item import ItemCreate, ItemOut

router = APIRouter()


@router.post("/", response_model=ItemOut, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db)) -> ItemOut:
    owner = db.query(User).filter(User.id == data.owner_id).first()
    if not owner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found",
        )
    item = Item(title=data.title, description=data.description, owner_id=data.owner_id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/", response_model=list[ItemOut])
def read_items(db: Session = Depends(get_db)) -> list[ItemOut]:
    return db.query(Item).all()
