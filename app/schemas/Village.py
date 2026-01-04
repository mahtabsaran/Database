from pydantic import BaseModel as PydanticBase
from typing import List


class VillageBase(PydanticBase):
    name: str
    city_id: int


class VillageCreate(VillageBase):
    pass


class VillageOut(VillageBase):
    id: int

    class Config:
        from_attributes = True


# مدل برای پاسخ صفحه‌بندی شده روستاها
class PaginatedVillageResponse(PydanticBase):
    items: List[VillageOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool