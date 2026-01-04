from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func
from datetime import datetime
from app.db import Base


class PaymentReason(Base):
    __tablename__ = "payment_reasons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reason_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())