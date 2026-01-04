from pydantic import BaseModel
from typing import List
from datetime import datetime


class MeasureUnitBase(BaseModel):
    unit_name: str


class MeasureUnitCreate(MeasureUnitBase):
    pass


class MeasureUnitOut(BaseModel):
    unit_name: str
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedMeasureUnitResponse(BaseModel):
    items: List[MeasureUnitOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool