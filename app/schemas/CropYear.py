from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class CropYearBase(BaseModel):
    crop_year_name: str


class CropYearCreate(CropYearBase):
    pass


class CropYearOut(BaseModel):
    id: int
    crop_year_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CropYearUpdate(BaseModel):
    crop_year_name: Optional[str] = None


class PaginatedCropYearResponse(BaseModel):
    items: List[CropYearOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool