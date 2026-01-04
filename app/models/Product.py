from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from datetime import datetime
from app.db import Base


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    measure_unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("measure_units.id", ondelete="CASCADE"),
                                                 nullable=False)
    crop_year_id: Mapped[int] = mapped_column(Integer, ForeignKey("crop_years.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # رابطه با MeasureUnit
    measure_unit: Mapped["MeasureUnit"] = relationship("MeasureUnit")
    # رابطه با CropYear
    crop_year: Mapped["CropYear"] = relationship("CropYear")