from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Integer, Boolean, DateTime, func
from datetime import datetime
from app.db import Base

class Auth(Base):
    __tablename__ = "auth"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    access_token: Mapped[str] = mapped_column(String(500), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(500), nullable=False)
    token_type: Mapped[str] = mapped_column(String(50), default="bearer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())