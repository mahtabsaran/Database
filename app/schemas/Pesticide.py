from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class PesticideBase(BaseModel):
    pesticide_name: str
    measure_unit_id: int


class PesticideCreate(PesticideBase):
    pass


class PesticideOut(BaseModel):
    id: int
    pesticide_name: str
    measure_unit_id: int
    created_at: datetime
    unit_name: str  # این فیلد از relationship می‌آید

    # استفاده از ConfigDict به جای class Config
    model_config = ConfigDict(from_attributes=True)


class PesticideUpdate(BaseModel):
    pesticide_name: Optional[str] = None
    measure_unit_id: Optional[int] = None


class PaginatedPesticideResponse(BaseModel):
    items: List[PesticideOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool