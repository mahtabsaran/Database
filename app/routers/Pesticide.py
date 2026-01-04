# app/routers/Pesticide.py - نسخه اصلاح شده
from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Pesticide import PesticideCreate, PesticideOut, PaginatedPesticideResponse
from ..models.Pesticide import Pesticide
from ..models.MeasureUnit import MeasureUnit

router = APIRouter(prefix="/pesticides", tags=["Pesticides"])


@router.post("/", response_model=PesticideOut)
def create_pesticide(session: SessionDep, pesticide: PesticideCreate):
    """
    ایجاد سم جدید
    """
    # بررسی وجود MeasureUnit
    measure_unit = session.execute(
        select(MeasureUnit).where(MeasureUnit.id == pesticide.measure_unit_id)
    ).scalar_one_or_none()

    if not measure_unit:
        raise HTTPException(status_code=404, detail="Measure unit not found")

    # بررسی تکراری بودن نام سم
    existing_pesticide = session.execute(
        select(Pesticide).where(Pesticide.pesticide_name == pesticide.pesticide_name)
    ).scalar_one_or_none()

    if existing_pesticide:
        raise HTTPException(status_code=400, detail="Pesticide name already exists")

    # ایجاد سم جدید
    pesticide_db = Pesticide(
        pesticide_name=pesticide.pesticide_name,
        measure_unit_id=pesticide.measure_unit_id
    )

    session.add(pesticide_db)
    session.commit()
    session.refresh(pesticide_db)

    # ساخت پاسخ دستی (بدون استفاده از from_orm)
    return PesticideOut(
        id=pesticide_db.id,
        pesticide_name=pesticide_db.pesticide_name,
        measure_unit_id=pesticide_db.measure_unit_id,
        created_at=pesticide_db.created_at,
        unit_name=measure_unit.unit_name
    )


@router.get("/", response_model=PaginatedPesticideResponse)
def get_pesticides(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None),
        measure_unit_id: Optional[int] = Query(None)
):
    """
    دریافت لیست سم‌ها با صفحه‌بندی
    """
    # ساخت کوئری پایه
    query = select(Pesticide)

    # اعمال فیلتر measure_unit_id
    if measure_unit_id:
        query = query.where(Pesticide.measure_unit_id == measure_unit_id)

    # اعمال جستجو
    if search:
        query = query.where(Pesticide.pesticide_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Pesticide, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Pesticide.id))
            else:
                query = query.order_by(asc(Pesticide.id))
    else:
        query = query.order_by(Pesticide.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    pesticide_objects = result.scalars().all()

    # گرفتن unit_name برای هر pesticide
    items = []
    for pesticide in pesticide_objects:
        # گرفتن unit_name جداگانه
        measure_unit = session.execute(
            select(MeasureUnit).where(MeasureUnit.id == pesticide.measure_unit_id)
        ).scalar_one_or_none()

        items.append(PesticideOut(
            id=pesticide.id,
            pesticide_name=pesticide.pesticide_name,
            measure_unit_id=pesticide.measure_unit_id,
            created_at=pesticide.created_at,
            unit_name=measure_unit.unit_name if measure_unit else "نامشخص"
        ))

    return PaginatedPesticideResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{pesticide_id}")
def delete_pesticide(session: SessionDep, pesticide_id: int):
    """
    حذف یک سم
    """
    pesticide = session.execute(
        select(Pesticide).where(Pesticide.id == pesticide_id)
    ).scalar_one_or_none()

    if not pesticide:
        raise HTTPException(status_code=404, detail="Pesticide not found")

    session.delete(pesticide)
    session.commit()

    return {"message": f"Pesticide {pesticide_id} deleted successfully"}