from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.MeasureUnit import MeasureUnitCreate, MeasureUnitOut, PaginatedMeasureUnitResponse
from ..models.MeasureUnit import MeasureUnit

router = APIRouter(prefix="/measure-units", tags=["Measure Units"])


@router.post("/", response_model=MeasureUnitOut)
def create_measure_unit(session: SessionDep, measure_unit: MeasureUnitCreate):
    """
    ایجاد واحد اندازه‌گیری جدید
    """
    existing_unit = session.execute(
        select(MeasureUnit).where(MeasureUnit.unit_name == measure_unit.unit_name)
    ).scalar_one_or_none()

    if existing_unit:
        raise HTTPException(status_code=400, detail="Unit name already exists")

    unit_db = MeasureUnit(unit_name=measure_unit.unit_name)
    session.add(unit_db)
    session.commit()
    session.refresh(unit_db)

    return unit_db


@router.get("/", response_model=PaginatedMeasureUnitResponse)
def get_measure_units(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None)
):
    """
    دریافت لیست واحدهای اندازه‌گیری با صفحه‌بندی
    """
    # ساخت کوئری پایه
    query = select(MeasureUnit)

    # اعمال جستجو
    if search:
        query = query.where(MeasureUnit.unit_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(MeasureUnit, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(MeasureUnit.id))
            else:
                query = query.order_by(asc(MeasureUnit.id))
    else:
        query = query.order_by(MeasureUnit.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedMeasureUnitResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{unit_id}")
def delete_measure_unit(session: SessionDep, unit_id: int):
    """
    حذف یک واحد اندازه‌گیری
    """
    unit = session.execute(
        select(MeasureUnit).where(MeasureUnit.id == unit_id)
    ).scalar_one_or_none()

    if not unit:
        raise HTTPException(status_code=404, detail="Measure unit not found")

    session.delete(unit)
    session.commit()

    return {"message": f"Measure unit {unit_id} deleted successfully"}