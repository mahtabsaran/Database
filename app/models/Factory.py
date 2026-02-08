from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func
from datetime import datetime
from app.db import Base


class Factory(Base):
    __tablename__ = "factory"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    factory_name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(),
                                                 onupdate=func.now())