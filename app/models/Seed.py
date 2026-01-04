from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, DateTime, func, ForeignKey
from datetime import datetime
from app.db import Base


class Seed(Base):
    __tablename__ = "seeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seed_name: Mapped[str] = mapped_column(String(255), nullable=False)
    measure_unit_id: Mapped[int] = mapped_column(Integer, ForeignKey("measure_units.id", ondelete="CASCADE"),
                                                 nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # رابطه با MeasureUnit
    measure_unit: Mapped["MeasureUnit"] = relationship("MeasureUnit")