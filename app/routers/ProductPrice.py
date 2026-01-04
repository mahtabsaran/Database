from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.ProductPrice import ProductPriceCreate
from ..models.ProductPrice import ProductPrice
from ..models.CropYear import CropYear

router = APIRouter(prefix="/product-prices", tags=["Product Prices"])


@router.post("/", response_model=dict)
def create_product_price(session: SessionDep, product_price: ProductPriceCreate):
    """
    ایجاد قیمت محصول جدید
    """
    # بررسی وجود CropYear
    crop_year = session.execute(
        select(CropYear).where(CropYear.id == product_price.crop_year_id)
    ).scalar_one_or_none()

    if not crop_year:
        raise HTTPException(status_code=404, detail="Crop year not found")

    # بررسی تکراری بودن قیمت برای این سال زراعی
    existing_price = session.execute(
        select(ProductPrice).where(ProductPrice.crop_year_id == product_price.crop_year_id)
    ).scalar_one_or_none()

    if existing_price:
        raise HTTPException(status_code=400, detail="Price already exists for this crop year")

    # ایجاد قیمت جدید
    price_db = ProductPrice(
        crop_year_id=product_price.crop_year_id,
        sugar_amount_per_ton_kg=product_price.sugar_amount_per_ton_kg,
        sugar_price_per_kg=product_price.sugar_price_per_kg,
        pulp_amount_per_ton_kg=product_price.pulp_amount_per_ton_kg,
        pulp_price_per_kg=product_price.pulp_price_per_kg
    )

    session.add(price_db)
    session.commit()
    session.refresh(price_db)

    # اضافه کردن crop_year_name به پاسخ
    result = convert_model_to_jalali(price_db)
    result["crop_year_name"] = crop_year.crop_year_name

    return result


@router.get("/", response_model=dict)
def get_product_prices(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None),
        crop_year_id: Optional[int] = Query(None)
):
    """
    دریافت لیست قیمت‌های محصول با صفحه‌بندی
    """
    # ساخت کوئری پایه با join روی CropYear
    query = select(ProductPrice).join(CropYear)

    # اعمال فیلتر crop_year_id
    if crop_year_id:
        query = query.where(ProductPrice.crop_year_id == crop_year_id)

    # اعمال جستجو (در نام سال زراعی)
    if search:
        query = query.where(CropYear.crop_year_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(ProductPrice, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(ProductPrice.id))
            else:
                query = query.order_by(asc(ProductPrice.id))
    else:
        query = query.order_by(ProductPrice.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    price_objects = result.scalars().all()

    # ساختن آیتم‌های پاسخ
    items = []
    for price in price_objects:
        # گرفتن crop_year_name
        crop_year = session.execute(
            select(CropYear).where(CropYear.id == price.crop_year_id)
        ).scalar_one_or_none()

        # تبدیل به دیکشنری
        price_dict = convert_model_to_jalali(price)
        price_dict["crop_year_name"] = crop_year.crop_year_name if crop_year else "نامشخص"
        items.append(price_dict)

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
        "has_next": page < pages,
        "has_prev": page > 1
    }


@router.delete("/{price_id}")
def delete_product_price(session: SessionDep, price_id: int):
    """
    حذف یک قیمت محصول
    """
    price = session.execute(
        select(ProductPrice).where(ProductPrice.id == price_id)
    ).scalar_one_or_none()

    if not price:
        raise HTTPException(status_code=404, detail="Product price not found")

    session.delete(price)
    session.commit()

    return {"message": f"Product price {price_id} deleted successfully"}