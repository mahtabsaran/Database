from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class FactoryBase(BaseModel):
    factory_name: str


class FactoryCreate(FactoryBase):
    pass


class FactoryOut(FactoryBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class FactoryUpdate(BaseModel):
    factory_name: Optional[str] = None


class PaginatedFactoryResponse(BaseModel):
    items: List[FactoryOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool