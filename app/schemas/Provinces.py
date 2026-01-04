from pydantic import BaseModel as PydanticBase
from typing import List


class ProvincesCreate(PydanticBase):
    name: str


class ProvincesOut(PydanticBase):
    id: int
    name: str

    class Config:
        from_attributes = True


class PaginatedResponse(PydanticBase):
    items: List[ProvincesOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool