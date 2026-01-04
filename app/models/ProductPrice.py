from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Numeric, DateTime, func, ForeignKey
from datetime import datetime
from app.db import Base


class ProductPrice(Base):
    __tablename__ = "product_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_year_id: Mapped[int] = mapped_column(Integer, ForeignKey("crop_years.id", ondelete="CASCADE"), nullable=False)
    sugar_amount_per_ton_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # مقدار شکر بر تن (کیلوگرم)
    sugar_price_per_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # قیمت شکر بر کیلوگرم
    pulp_amount_per_ton_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # مقدار تفاله بر تن (کیلوگرم)
    pulp_price_per_kg: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # قیمت تفاله بر کیلوگرم
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # رابطه با CropYear
    crop_year: Mapped["CropYear"] = relationship("CropYear")