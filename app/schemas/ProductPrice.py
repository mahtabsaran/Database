from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class ProductPriceBase(BaseModel):
    crop_year_id: int
    sugar_amount_per_ton_kg: float = Field(ge=0, description="مقدار شکر بر تن (کیلوگرم)")
    sugar_price_per_kg: float = Field(ge=0, description="قیمت شکر بر کیلوگرم")
    pulp_amount_per_ton_kg: float = Field(ge=0, description="مقدار تفاله بر تن (کیلوگرم)")
    pulp_price_per_kg: float = Field(ge=0, description="قیمت تفاله بر کیلوگرم")


class ProductPriceCreate(ProductPriceBase):
    pass


class ProductPriceOut(BaseModel):
    id: int
    crop_year_id: int
    sugar_amount_per_ton_kg: float
    sugar_price_per_kg: float
    pulp_amount_per_ton_kg: float
    pulp_price_per_kg: float
    created_at: datetime
    crop_year_name: str  # از رابطه با CropYear

    model_config = ConfigDict(from_attributes=True)


class ProductPriceUpdate(BaseModel):
    crop_year_id: Optional[int] = None
    sugar_amount_per_ton_kg: Optional[float] = Field(None, ge=0)
    sugar_price_per_kg: Optional[float] = Field(None, ge=0)
    pulp_amount_per_ton_kg: Optional[float] = Field(None, ge=0)
    pulp_price_per_kg: Optional[float] = Field(None, ge=0)


class PaginatedProductPriceResponse(BaseModel):
    items: List[ProductPriceOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool