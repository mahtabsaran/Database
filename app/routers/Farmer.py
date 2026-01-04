from fastapi import APIRouter, Query, HTTPException, Path
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Farmer import (
    FarmerCreate, FarmerOut, FarmerUpdate,
    PaginatedFarmerResponse, FarmerIdToUserIdResponse
)
from ..models.Farmer import Farmer
from ..models.User import User  # برای endpoint آخر

router = APIRouter(prefix="/farmer", tags=["Farmer"])


@router.post("/", response_model=FarmerOut)
def create_farmer(session: SessionDep, farmer: FarmerCreate):
    """
    Create a new farmer
    """
    # بررسی وجود کشاورز با کدملی تکراری
    existing_farmer = session.execute(
        select(Farmer).where(Farmer.national_id == farmer.national_id)
    ).scalar_one_or_none()

    if existing_farmer:
        raise HTTPException(status_code=400, detail="Farmer with this national ID already exists")

    # ایجاد کشاورز جدید
    farmer_db = Farmer(**farmer.dict())
    session.add(farmer_db)
    session.commit()
    session.refresh(farmer_db)

    return farmer_db


@router.get("/", response_model=PaginatedFarmerResponse)
def get_all_farmers(
        session: SessionDep,
        page: int = Query(1, description="Page number", ge=1),
        size: int = Query(50, description="Page size", ge=1, le=100),
        sort_by: str = Query("id", description="Sort field"),
        sort_order: str = Query("asc", description="Sort order", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None, description="Search term"),
        national_id: Optional[str] = Query(None, description="Filter by national ID"),
        full_name: Optional[str] = Query(None, description="Filter by full name")
):
    """
    Get all farmers with pagination, sorting and filtering
    """
    # ساخت کوئری پایه
    query = select(Farmer)

    # اعمال فیلترها
    if national_id:
        query = query.where(Farmer.national_id.ilike(f"%{national_id}%"))

    if full_name:
        query = query.where(Farmer.full_name.ilike(f"%{full_name}%"))

    if search:
        search_filter = (
                Farmer.national_id.ilike(f"%{search}%") |
                Farmer.full_name.ilike(f"%{search}%") |
                Farmer.father_name.ilike(f"%{search}%") |
                Farmer.phone_number.ilike(f"%{search}%")
        )
        query = query.where(search_filter)

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total_result = session.execute(count_query)
    total = total_result.scalar()

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Farmer, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Farmer.id))
            else:
                query = query.order_by(asc(Farmer.id))
    else:
        query = query.order_by(Farmer.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedFarmerResponse(
        total=total,
        size=size,
        pages=pages,
        items=items
    )


@router.get("/{national_id}", response_model=FarmerOut)
def get_farmer_by_national_id(
        session: SessionDep,
        national_id: str = Path(..., description="National ID of the farmer")
):
    """
    Get farmer by national ID
    """
    farmer = session.execute(
        select(Farmer).where(Farmer.national_id == national_id)
    ).scalar_one_or_none()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    return farmer


@router.put("/{national_id}", response_model=FarmerOut)
def update_farmer(
        session: SessionDep,
        national_id: str = Path(..., description="National ID of the farmer"),
        farmer_update: FarmerUpdate = ...
):
    """
    Update farmer by national ID
    """
    # یافتن کشاورز
    farmer = session.execute(
        select(Farmer).where(Farmer.national_id == national_id)
    ).scalar_one_or_none()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # به‌روزرسانی فیلدها
    update_data = farmer_update.dict(exclude_unset=True)

    for field, value in update_data.items():
        if value is not None:
            setattr(farmer, field, value)

    session.commit()
    session.refresh(farmer)

    return farmer


@router.delete("/{national_id}")
def delete_farmer(
        session: SessionDep,
        national_id: str = Path(..., description="National ID of the farmer")
):
    """
    Delete farmer by national ID
    """
    farmer = session.execute(
        select(Farmer).where(Farmer.national_id == national_id)
    ).scalar_one_or_none()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    session.delete(farmer)
    session.commit()

    return {"message": f"Farmer with national ID {national_id} deleted successfully"}


@router.get("/farmer-id-to-user-id/{farmer_id}", response_model=FarmerIdToUserIdResponse)
def get_user_id_from_farmer_id(
        session: SessionDep,
        farmer_id: int = Path(..., description="Farmer ID", ge=1)
):
    """
    Get user ID from farmer ID
    """
    # یافتن کشاورز
    farmer = session.execute(
        select(Farmer).where(Farmer.id == farmer_id)
    ).scalar_one_or_none()

    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")

    # یافتن کاربر مرتبط (فرض می‌کنیم رابطه‌ای بین Farmer و User وجود دارد)
    # این قسمت بستگی به ساختار جدول User شما دارد
    user = session.execute(
        select(User).where(User.farmer_id == farmer_id)
    ).scalar_one_or_none()

    return FarmerIdToUserIdResponse(
        farmer_id=farmer_id,
        user_id=user.id if user else None
    )