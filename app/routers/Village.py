from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import List
from ..db import SessionDep
from ..schemas.Village import VillageCreate, VillageOut, PaginatedVillageResponse
from ..models.Village import Village
from ..models.City import City

router = APIRouter(prefix="/village", tags=["Village"])


@router.post("/", response_model=VillageOut)
def create_village(session: SessionDep, village: VillageCreate):
    """
    ایجاد یک روستای جدید
    """
    # بررسی وجود شهر
    city = session.execute(
        select(City).where(City.id == village.city_id)
    ).scalar_one_or_none()

    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    # بررسی وجود روستای تکراری در این شهر
    existing_village = session.execute(
        select(Village).where(
            Village.name == village.name,
            Village.city_id == village.city_id
        )
    ).scalar_one_or_none()

    if existing_village:
        raise HTTPException(status_code=400, detail="Village already exists in this city")

    # ایجاد روستای جدید
    village_db = Village(name=village.name, city_id=village.city_id)
    session.add(village_db)
    session.commit()
    session.refresh(village_db)

    return village_db


@router.get("/", response_model=PaginatedVillageResponse)
def get_villages(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: str = Query(None),
        city_id: int = Query(None)
):
    """
    دریافت لیست روستاها با صفحه‌بندی، مرتب‌سازی، جستجو و فیلتر
    """
    # ساخت کوئری پایه
    query = select(Village)

    # اعمال فیلتر شهر
    if city_id:
        query = query.where(Village.city_id == city_id)

    # اعمال جستجو
    if search:
        query = query.where(Village.name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total_result = session.execute(count_query)
    total = total_result.scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Village, sort_by)
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(Village.id))
            else:
                query = query.order_by(asc(Village.id))
    else:
        query = query.order_by(Village.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری و تبدیل به دیکشنری
    result = session.execute(query)
    village_objects = result.scalars().all()

    # تبدیل آبجکت‌های SQLAlchemy به دیکشنری
    items = []
    for village in village_objects:
        items.append({
            "id": village.id,
            "name": village.name,
            "city_id": village.city_id
        })

    return PaginatedVillageResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{village_id}")
def delete_village(session: SessionDep, village_id: int):
    """
    حذف یک روستا
    """
    village = session.execute(
        select(Village).where(Village.id == village_id)
    ).scalar_one_or_none()

    if not village:
        raise HTTPException(status_code=404, detail="Village not found")

    session.delete(village)
    session.commit()

    return {"message": f"Village {village_id} deleted successfully"}