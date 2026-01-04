from pydantic import BaseModel as PydanticBase, Field
from typing import Optional, List


class CityBase(PydanticBase):
    name: str
    province_id: int


class CityCreate(CityBase):
    pass


class CityOut(CityBase):
    id: int

    class Config:
        from_attributes = True


# مدل برای پاسخ صفحه‌بندی شده شهرها
class PaginatedCityResponse(PydanticBase):
    items: List[CityOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool