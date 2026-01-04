from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.CropYear import CropYearCreate, CropYearOut, PaginatedCropYearResponse
from ..models.CropYear import CropYear

router = APIRouter(prefix="/crop-years", tags=["Crop Years"])


@router.post("/", response_model=CropYearOut)
def create_crop_year(session: SessionDep, crop_year: CropYearCreate):
    """
    ایجاد سال زراعی جدید
    """
    existing_crop_year = session.execute(
        select(CropYear).where(CropYear.crop_year_name == crop_year.crop_year_name)
    ).scalar_one_or_none()

    if existing_crop_year:
        raise HTTPException(status_code=400, detail="Crop year name already exists")

    crop_year_db = CropYear(crop_year_name=crop_year.crop_year_name)
    session.add(crop_year_db)
    session.commit()
    session.refresh(crop_year_db)

    return crop_year_db


@router.get("/", response_model=PaginatedCropYearResponse)
def get_crop_years(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None)
):
    """
    دریافت لیست سال‌های زراعی با صفحه‌بندی
    """
    query = select(CropYear)

    if search:
        query = query.where(CropYear.crop_year_name.ilike(f"%{search}%"))

    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0
    pages = (total + size - 1) // size if total > 0 else 1

    if sort_by:
        try:
            sort_column = getattr(CropYear, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(CropYear.id))
            else:
                query = query.order_by(asc(CropYear.id))
    else:
        query = query.order_by(CropYear.id)

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedCropYearResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{crop_year_id}")
def delete_crop_year(session: SessionDep, crop_year_id: int):
    """
    حذف یک سال زراعی
    """
    crop_year = session.execute(
        select(CropYear).where(CropYear.id == crop_year_id)
    ).scalar_one_or_none()

    if not crop_year:
        raise HTTPException(status_code=404, detail="Crop year not found")

    session.delete(crop_year)
    session.commit()

    return {"message": f"Crop year {crop_year_id} deleted successfully"}