from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class ProductBase(BaseModel):
    product_name: str
    measure_unit_id: int
    crop_year_id: int


class ProductCreate(ProductBase):
    pass


class ProductOut(BaseModel):
    id: int
    product_name: str
    measure_unit_id: int
    crop_year_id: int
    created_at: datetime
    unit_name: str  # از رابطه با MeasureUnit
    crop_year_name: str  # از رابطه با CropYear

    model_config = ConfigDict(from_attributes=True)


class ProductUpdate(BaseModel):
    product_name: Optional[str] = None
    measure_unit_id: Optional[int] = None
    crop_year_id: Optional[int] = None


class PaginatedProductResponse(BaseModel):
    items: List[ProductOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool