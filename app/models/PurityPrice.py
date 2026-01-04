from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, Numeric, DateTime, func, ForeignKey
from datetime import datetime
from app.db import Base


class PurityPrice(Base):
    __tablename__ = "purity_prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_year_id: Mapped[int] = mapped_column(Integer, ForeignKey("crop_years.id", ondelete="CASCADE"), nullable=False)
    base_purity: Mapped[float] = mapped_column(Numeric(5, 2), nullable=False)  # خلوص پایه (درصد)
    base_purity_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # قیمت پایه
    price_difference: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)  # تفاوت قیمت به ازای هر درصد
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # رابطه با CropYear
    crop_year: Mapped["CropYear"] = relationship("CropYear")