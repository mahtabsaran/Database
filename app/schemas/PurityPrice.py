from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class PurityPriceBase(BaseModel):
    crop_year_id: int
    base_purity: float = Field(ge=0, le=100, description="خلوص پایه (درصد، بین 0 تا 100)")
    base_purity_price: float = Field(ge=0, description="قیمت پایه")
    price_difference: float = Field(description="تفاوت قیمت به ازای هر درصد")


class PurityPriceCreate(PurityPriceBase):
    pass


class PurityPriceOut(BaseModel):
    id: int
    crop_year_id: int
    base_purity: float
    base_purity_price: float
    price_difference: float
    created_at: datetime
    crop_year_name: str  # از رابطه با CropYear

    model_config = ConfigDict(from_attributes=True)


class PurityPriceUpdate(BaseModel):
    crop_year_id: Optional[int] = None
    base_purity: Optional[float] = Field(None, ge=0, le=100)
    base_purity_price: Optional[float] = Field(None, ge=0)
    price_difference: Optional[float] = None


class PaginatedPurityPriceResponse(BaseModel):
    items: List[PurityPriceOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool