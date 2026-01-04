from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime


class PaymentReasonBase(BaseModel):
    reason_name: str


class PaymentReasonCreate(PaymentReasonBase):
    pass


class PaymentReasonOut(BaseModel):
    id: int
    reason_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PaymentReasonUpdate(BaseModel):
    reason_name: Optional[str] = None


class PaginatedPaymentReasonResponse(BaseModel):
    items: List[PaymentReasonOut]
    total: int
    page: int
    size: int
    pages: int
    has_next: bool
    has_prev: bool