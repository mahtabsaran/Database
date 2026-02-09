# app/db.py -
from typing import Annotated
from fastapi import Depends
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker, declarative_base
import logging

logger = logging.getLogger(__name__)

sqlite_file_name = "../database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# 🚨 **تنظیمات مهم برای SQLite**
connect_args = {
    "check_same_thread": False,
    "timeout": 30,  # افزایش timeout برای قفل
    "isolation_level": None  # برای auto-commit mode
}

engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    echo=True,  # برای دیدن کوئری‌ها
    pool_pre_ping=True,
    pool_size=1,  # برای SQLite بهتر است
    max_overflow=0
)

# Enable foreign key enforcement for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")  # 🚨 حالت WAL برای concurrent access
    cursor.execute("PRAGMA busy_timeout=5000")  # 🚨 افزایش timeout
    cursor.close()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=Session
)

Base = declarative_base()

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)

# 🚨 **Dependency اصلاح شده**
def get_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()  # حتماً commit کن
        logger.info("✅ Session committed successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Session rollback due to error: {e}")
        raise
    finally:
        db.close()
        logger.debug("Session closed")

SessionDep = Annotated[Session, Depends(get_session)]