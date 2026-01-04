from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.City import CityCreate, CityOut, PaginatedCityResponse
from ..models.City import City
from ..models.Provinces import Provinces

router = APIRouter(prefix="/city", tags=["City"])


@router.post("/", response_model=CityOut)
def create_city(session: SessionDep, city: CityCreate):
    """
    Create a new city
    """
    # بررسی وجود استان
    province = session.execute(
        select(Provinces).where(Provinces.id == city.province_id)
    ).scalar_one_or_none()

    if not province:
        raise HTTPException(status_code=404, detail="Province not found")

    # بررسی وجود شهر تکراری
    existing_city = session.execute(
        select(City).where(
            City.name == city.name,
            City.province_id == city.province_id
        )
    ).scalar_one_or_none()

    if existing_city:
        raise HTTPException(status_code=400, detail="City already exists in this province")

    # ایجاد شهر جدید
    city_db = City(name=city.name, province_id=city.province_id)
    session.add(city_db)
    session.commit()
    session.refresh(city_db)

    return city_db


@router.get("/", response_model=PaginatedCityResponse)
def get_cities(
        session: SessionDep,
        page: int = Query(1, description="Page number", ge=1),
        size: int = Query(50, description="Page size", ge=1, le=100),
        sort_by: Optional[str] = Query("id", description="Sort field"),
        sort_order: Optional[str] = Query("asc", description="Sort order", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None, description="Search term"),
        province_id: Optional[int] = Query(None, description="Filter by province ID")
):
    """
    Get list of cities with pagination, sorting and filtering
    """
    # ساخت کوئری پایه
    query = select(City)

    # اعمال فیلتر استان
    if province_id:
        query = query.where(City.province_id == province_id)

    # اعمال جستجو
    if search:
        query = query.where(City.name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total_result = session.execute(count_query)
    total = total_result.scalar()

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(City, sort_by)
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order and sort_order.lower() == "desc":
                query = query.order_by(desc(City.id))
            else:
                query = query.order_by(asc(City.id))
    else:
        query = query.order_by(City.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedCityResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{city_id}")
def delete_city(session: SessionDep, city_id: int):
    """
    Delete a city by ID
    """
    city = session.execute(
        select(City).where(City.id == city_id)
    ).scalar_one_or_none()

    if not city:
        raise HTTPException(status_code=404, detail="City not found")

    session.delete(city)
    session.commit()

    return {"message": f"City {city_id} deleted successfully"}