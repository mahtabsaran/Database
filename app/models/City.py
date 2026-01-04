from app.db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey
from typing import List


class City(SQLAlchemyBase):
    __tablename__ = "city"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    province_id: Mapped[int] = mapped_column(Integer, ForeignKey("provinces.id", ondelete="CASCADE"), nullable=False)

    # رابطه با استان
    province: Mapped["Provinces"] = relationship("Provinces", back_populates="cities")

    # رابطه با روستاها (روستاهای این شهر)
    villages: Mapped[List["Village"]] = relationship("Village", back_populates="city", cascade="all, delete-orphan")