from app.db import Base as SQLAlchemyBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, ForeignKey


class Village(SQLAlchemyBase):
    __tablename__ = "village"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    city_id: Mapped[int] = mapped_column(Integer, ForeignKey("city.id", ondelete="CASCADE"), nullable=False)

    # رابطه با شهر
    city: Mapped["City"] = relationship("City", back_populates="villages")