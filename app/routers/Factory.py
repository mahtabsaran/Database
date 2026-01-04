# app/routers/Factory.py
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Factory import FactoryCreate, FactoryOut, PaginatedFactoryResponse
from ..models.Factory import Factory

router = APIRouter(prefix="/factory", tags=["Factory"])


@router.post("/", response_model=FactoryOut)
def create_factory(session: SessionDep, factory: FactoryCreate):
    """
    ایجاد یک کارخانه جدید
    """
    # بررسی تکراری بودن نام کارخانه
    existing_factory = session.execute(
        select(Factory).where(Factory.factory_name == factory.factory_name)
    ).scalar_one_or_none()

    if existing_factory:
        raise HTTPException(status_code=400, detail="Factory with this name already exists")

    # ایجاد کارخانه جدید
    factory_db = Factory(factory_name=factory.factory_name)
    session.add(factory_db)
    session.commit()
    session.refresh(factory_db)

    return factory_db


@router.get("/", response_model=PaginatedFactoryResponse)
def get_factories(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None)
):
    """
    دریافت لیست کارخانه‌ها با صفحه‌بندی، مرتب‌سازی و جستجو
    """
    # ساخت کوئری پایه
    query = select(Factory)

    # اعمال جستجو
    if search:
        query = query.where(Factory.factory_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total_result = session.execute(count_query)
    total = total_result.scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Factory, sort_by)
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(Factory.id))
            else:
                query = query.order_by(asc(Factory.id))
    else:
        query = query.order_by(Factory.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedFactoryResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{factory_id}")
def delete_factory(session: SessionDep, factory_id: int):
    """
    حذف یک کارخانه
    """
    factory = session.execute(
        select(Factory).where(Factory.id == factory_id)
    ).scalar_one_or_none()

    if not factory:
        raise HTTPException(status_code=404, detail="Factory not found")

    session.delete(factory)
    session.commit()

    return {"message": f"Factory {factory_id} deleted successfully"}