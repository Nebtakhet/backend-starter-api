from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    description: str | None = None


class ItemCreate(ItemBase):
    owner_id: int


class ItemOut(ItemBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True
