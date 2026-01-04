from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.PaymentReason import PaymentReasonCreate, PaymentReasonOut, PaginatedPaymentReasonResponse
from ..models.PaymentReason import PaymentReason

router = APIRouter(prefix="/payment-reasons", tags=["Payment Reasons"])


@router.post("/", response_model=PaymentReasonOut)
def create_payment_reason(session: SessionDep, payment_reason: PaymentReasonCreate):
    """
    ایجاد دلیل پرداخت جدید
    """
    existing_reason = session.execute(
        select(PaymentReason).where(PaymentReason.reason_name == payment_reason.reason_name)
    ).scalar_one_or_none()

    if existing_reason:
        raise HTTPException(status_code=400, detail="Reason name already exists")

    reason_db = PaymentReason(reason_name=payment_reason.reason_name)
    session.add(reason_db)
    session.commit()
    session.refresh(reason_db)

    return reason_db


@router.get("/", response_model=PaginatedPaymentReasonResponse)
def get_payment_reasons(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None)
):
    """
    دریافت لیست دلایل پرداخت با صفحه‌بندی
    """
    # ساخت کوئری پایه
    query = select(PaymentReason)

    # اعمال جستجو
    if search:
        query = query.where(PaymentReason.reason_name.ilike(f"%{search}%"))

    # محاسبه کل تعداد
    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0

    # محاسبه تعداد صفحات
    pages = (total + size - 1) // size if total > 0 else 1

    # اعمال مرتب‌سازی
    if sort_by:
        try:
            sort_column = getattr(PaymentReason, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(PaymentReason.id))
            else:
                query = query.order_by(asc(PaymentReason.id))
    else:
        query = query.order_by(PaymentReason.id)

    # اعمال صفحه‌بندی
    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    # اجرای کوئری
    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedPaymentReasonResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )


@router.delete("/{reason_id}")
def delete_payment_reason(session: SessionDep, reason_id: int):
    """
    حذف یک دلیل پرداخت
    """
    reason = session.execute(
        select(PaymentReason).where(PaymentReason.id == reason_id)
    ).scalar_one_or_none()

    if not reason:
        raise HTTPException(status_code=404, detail="Payment reason not found")

    session.delete(reason)
    session.commit()

    return {"message": f"Payment reason {reason_id} deleted successfully"}