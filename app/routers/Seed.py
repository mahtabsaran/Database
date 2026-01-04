from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Seed import SeedCreate, SeedOut, PaginatedSeedResponse
from ..models.Seed import Seed
from ..models.MeasureUnit import MeasureUnit

router = APIRouter(prefix="/seeds", tags=["Seeds"])


@router.post("/", response_model=SeedOut)
def create_seed(session: SessionDep, seed: SeedCreate):
    """
    ایجاد بذر جدید
    """
    # بررسی وجود MeasureUnit
    measure_unit = session.execute(
        select(MeasureUnit).where(MeasureUnit.id == seed.measure_unit_id)
    ).scalar_one_or_none()

    if not measure_unit:
        raise HTTPException(status_code=404, detail="Measure unit not found")

    # بررسی تکراری بودن نام بذر
    existing_seed = session.execute(
        select(Seed).where(Seed.seed_name == seed.seed_name)
    ).scalar_one_or_none()

    if existing_seed:
        raise HTTPException(status_code=400, detail="Seed name already exists")

    # ایجاد بذر جدید
    seed_db = Seed(
        seed_name=seed.seed_name,
        measure_unit_id=seed.measure_unit_id
    )

    session.add(seed_db)
    session.commit()
    session.refresh(seed_db)

    # ساخت پاسخ دستی
    return SeedOut(
        id=seed_db.id,
        seed_name=seed_db.seed_name,
        measure_unit_id=seed_db.measure_unit_id,
        created_at=seed_db.created_at,
        unit_name=measure_unit.unit_name
    )


@router.get("/", response_model=PaginatedSeedResponse)
def get_seeds(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None),
        measure_unit_id: Optional[int] = Query(None)
):
    """
    دریافت لیست بذرها با صفحه‌بندی
    """
    # ساخت کوئری پایه
    query = select(Seed)

    # اعمال فیلتر measure_unit_id
    if measure_unit_id:
        query = query.where(Seed.measure_unit_id == measure_unit_id)

    # اعمال جستجو
    if search:
        query = query.where(Seed.seed_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Seed, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Seed.id))
            else:
                query = query.order_by(asc(Seed.id))
    else:
        query = query.order_by(Seed.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    seed_objects = result.scalars().all()

    # ساختن آیتم‌های پاسخ
    items = []
    for seed in seed_objects:
        # گرفتن unit_name جداگانه
        measure_unit = session.execute(
            select(MeasureUnit).where(MeasureUnit.id == seed.measure_unit_id)
        ).scalar_one_or_none()

        items.append(SeedOut(
            id=seed.id,
            seed_name=seed.seed_name,
            measure_unit_id=seed.measure_unit_id,
            created_at=seed.created_at,
            unit_name=measure_unit.unit_name if measure_unit else "نامشخص"
        ))

    return PaginatedSeedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{seed_id}")
def delete_seed(session: SessionDep, seed_id: int):
    """
    حذف یک بذر
    """
    seed = session.execute(
        select(Seed).where(Seed.id == seed_id)
    ).scalar_one_or_none()

    if not seed:
        raise HTTPException(status_code=404, detail="Seed not found")

    session.delete(seed)
    session.commit()

    return {"message": f"Seed {seed_id} deleted successfully"}