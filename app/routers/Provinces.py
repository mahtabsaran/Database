from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Provinces import ProvincesCreate, PaginatedResponse
from ..models.Provinces import Provinces

router = APIRouter(prefix="/provinces", tags=["Provinces"])


@router.post("/")
def create_province(session: SessionDep, province: ProvincesCreate):
    province_db = Provinces(name=province.name)
    session.add(province_db)
    session.commit()
    session.refresh(province_db)
    return province_db


@router.get("/", response_model=PaginatedResponse)
def get_provinces(
        session: SessionDep,
        page: int = Query(1, description="Page number", ge=1),
        size: int = Query(50, description="Page size", ge=1, le=100),
        sort_by: Optional[str] = Query("id", description="Sort field"),
        sort_order: Optional[str] = Query("asc", description="Sort order", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None, description="Search term")
):
    print(f"Parameters received: page={page}, size={size}, sort_by={sort_by}, sort_order={sort_order}, search={search}")

    # ساخت کوئری پایه برای محاسبه کل تعداد
    base_query = select(Provinces)

    # اعمال جستجو
    if search:
        base_query = base_query.where(Provinces.name.ilike(f"%{search}%"))

    # محاسبه کل تعداد رکوردها
    count_query = select(func.count()).select_from(base_query.subquery())
    total_result = session.execute(count_query)
    total = total_result.scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # ساخت کوئری اصلی برای دریافت داده
    query = select(Provinces)

    # اعمال جستجو (دوباره)
    if search:
        query = query.where(Provinces.name.ilike(f"%{search}%"))

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Provinces, sort_by)
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(Provinces.id))
            else:
                query = query.order_by(asc(Provinces.id))
    else:
        query = query.order_by(Provinces.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری و تبدیل به مدل Pydantic
    result = session.execute(query)
    province_objects = result.scalars().all()

    # تبدیل آبجکت‌های SQLAlchemy به دیکشنری
    items = []
    for province in province_objects:
        items.append({
            "id": province.id,
            "name": province.name
        })

    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{province_id}")
def delete_province(session: SessionDep, province_id: int):
    result = session.execute(select(Provinces).where(Provinces.id == province_id))
    province = result.scalar_one_or_none()

    if not province:
        raise HTTPException(status_code=404, detail="Province not found")

    session.delete(province)
    session.commit()

    return {"message": f"Province {province_id} deleted successfully"}