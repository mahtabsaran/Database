from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from datetime import datetime


class FarmerBase(BaseModel):
    national_id: str = Field(..., min_length=1, max_length=20)
    full_name: str = Field(..., min_length=1, max_length=255)
    father_name: str = Field(..., min_length=1, max_length=255)
    phone_number: str = Field(..., min_length=1, max_length=20)
    sheba_number_1: Optional[str] = Field(None, max_length=30)
    sheba_number_2: Optional[str] = Field(None, max_length=30)
    card_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class FarmerCreate(FarmerBase):
    pass


class FarmerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    father_name: Optional[str] = Field(None, min_length=1, max_length=255)
    phone_number: Optional[str] = Field(None, min_length=1, max_length=20)
    sheba_number_1: Optional[str] = Field(None, max_length=30)
    sheba_number_2: Optional[str] = Field(None, max_length=30)
    card_number: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = Field(None, max_length=500)


class FarmerOut(FarmerBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaginatedFarmerResponse(BaseModel):
    total: int
    size: int
    pages: int
    items: List[FarmerOut]


class FarmerIdToUserIdResponse(BaseModel):
    farmer_id: int
    user_id: Optional[int] = None