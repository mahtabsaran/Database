from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.Product import ProductCreate, ProductOut, PaginatedProductResponse
from ..models.Product import Product
from ..models.MeasureUnit import MeasureUnit
from ..models.CropYear import CropYear

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("/", response_model=ProductOut)
def create_product(session: SessionDep, product: ProductCreate):
    """
    ایجاد محصول جدید
    """
    # بررسی وجود MeasureUnit
    measure_unit = session.execute(
        select(MeasureUnit).where(MeasureUnit.id == product.measure_unit_id)
    ).scalar_one_or_none()

    if not measure_unit:
        raise HTTPException(status_code=404, detail="Measure unit not found")

    # بررسی وجود CropYear
    crop_year = session.execute(
        select(CropYear).where(CropYear.id == product.crop_year_id)
    ).scalar_one_or_none()

    if not crop_year:
        raise HTTPException(status_code=404, detail="Crop year not found")

    # بررسی تکراری بودن نام محصول
    existing_product = session.execute(
        select(Product).where(Product.product_name == product.product_name)
    ).scalar_one_or_none()

    if existing_product:
        raise HTTPException(status_code=400, detail="Product name already exists")

    # ایجاد محصول جدید
    product_db = Product(
        product_name=product.product_name,
        measure_unit_id=product.measure_unit_id,
        crop_year_id=product.crop_year_id
    )

    session.add(product_db)
    session.commit()
    session.refresh(product_db)

    # ساخت پاسخ دستی
    return ProductOut(
        id=product_db.id,
        product_name=product_db.product_name,
        measure_unit_id=product_db.measure_unit_id,
        crop_year_id=product_db.crop_year_id,
        created_at=product_db.created_at,
        unit_name=measure_unit.unit_name,
        crop_year_name=crop_year.crop_year_name
    )


@router.get("/", response_model=PaginatedProductResponse)
def get_products(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None),
        measure_unit_id: Optional[int] = Query(None),
        crop_year_id: Optional[int] = Query(None)
):
    """
    دریافت لیست محصولات با صفحه‌بندی
    """
    # ساخت کوئری پایه
    query = select(Product)

    # اعمال فیلتر measure_unit_id
    if measure_unit_id:
        query = query.where(Product.measure_unit_id == measure_unit_id)

    # اعمال فیلتر crop_year_id
    if crop_year_id:
        query = query.where(Product.crop_year_id == crop_year_id)

    # اعمال جستجو
    if search:
        query = query.where(Product.product_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(Product, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(Product.id))
            else:
                query = query.order_by(asc(Product.id))
    else:
        query = query.order_by(Product.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    product_objects = result.scalars().all()

    # ساختن آیتم‌های پاسخ
    items = []
    for product in product_objects:
        # گرفتن unit_name و crop_year_name جداگانه
        measure_unit = session.execute(
            select(MeasureUnit).where(MeasureUnit.id == product.measure_unit_id)
        ).scalar_one_or_none()

        crop_year = session.execute(
            select(CropYear).where(CropYear.id == product.crop_year_id)
        ).scalar_one_or_none()

        items.append(ProductOut(
            id=product.id,
            product_name=product.product_name,
            measure_unit_id=product.measure_unit_id,
            crop_year_id=product.crop_year_id,
            created_at=product.created_at,
            unit_name=measure_unit.unit_name if measure_unit else "نامشخص",
            crop_year_name=crop_year.crop_year_name if crop_year else "نامشخص"
        ))

    return PaginatedProductResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{product_id}")
def delete_product(session: SessionDep, product_id: int):
    """
    حذف یک محصول
    """
    product = session.execute(
        select(Product).where(Product.id == product_id)
    ).scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    session.delete(product)
    session.commit()

    return {"message": f"Product {product_id} deleted successfully"}