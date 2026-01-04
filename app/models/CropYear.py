from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, DateTime, func
from datetime import datetime
from app.db import Base


class CropYear(Base):
    __tablename__ = "crop_years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    crop_year_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())