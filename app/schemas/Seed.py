from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class SeedBase(BaseModel):
    seed_name: str
    measure_unit_id: int


class SeedCreate(SeedBase):
    pass


class SeedOut(BaseModel):
    id: int
    seed_name: str
    measure_unit_id: int
    created_at: datetime
    unit_name: str  # از رابطه با MeasureUnit

    model_config = ConfigDict(from_attributes=True)


class SeedUpdate(BaseModel):
    seed_name: Optional[str] = None
    measure_unit_id: Optional[int] = None


class PaginatedSeedResponse(BaseModel):
    items: List[SeedOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool