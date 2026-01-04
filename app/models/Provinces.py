from app.db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer
from typing import List


class Provinces(SQLAlchemyBase):
    __tablename__ = "provinces"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    # رابطه با شهرها
    cities: Mapped[List["City"]] = relationship("City", back_populates="province", cascade="all, delete-orphan")