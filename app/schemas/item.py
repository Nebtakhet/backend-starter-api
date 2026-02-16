"""Pydantic schemas for item data exchange."""

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class ItemOut(ItemBase):
    id: int
    owner_id: int

    model_config = ConfigDict(from_attributes=True)


class ItemListResponse(BaseModel):
    """Paginated response for list of items."""

    items: list[ItemOut]
    total: int
    skip: int
    limit: int
