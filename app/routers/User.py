from fastapi import APIRouter, Query, HTTPException
from sqlalchemy import select, asc, desc, func
from typing import Optional
from app.db import SessionDep
from ..schemas.User import UserCreate, UserUpdate, UserOut, PaginatedUserResponse
from ..models.User import User
from app.security import get_password_hash

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/admin/", response_model=UserOut)
def create_user_by_admin(session: SessionDep, user: UserCreate):
    existing_user = session.execute(
        select(User).where(User.username == user.username)
    ).scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = session.execute(
        select(User).where(User.email == user.email)
    ).scalar_one_or_none()

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    user_db = User(
        username=user.username,
        email=user.email,
        password_hash=get_password_hash(user.password),
        full_name=user.full_name,
        is_active=True
    )

    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@router.get("/{user_id}", response_model=UserOut)
def get_user(session: SessionDep, user_id: int):
    user = session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.put("/{user_id}", response_model=UserOut)
def update_user(session: SessionDep, user_id: int, user_update: UserUpdate):
    user = session.execute(
        select(User).where(User.id == user_id)
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_update.username and user_update.username != user.username:
        existing_user = session.execute(
            select(User).where(
                User.username == user_update.username,
                User.id != user_id
            )
        ).scalar_one_or_none()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = user_update.username

    if user_update.email and user_update.email != user.email:
        existing_email = session.execute(
            select(User).where(
                User.email == user_update.email,
                User.id != user_id
            )
        ).scalar_one_or_none()

        if existing_email:
            raise HTTPException(status_code=400, detail="Email already exists")
        user.email = user_update.email

    if user_update.full_name is not None:
        user.full_name = user_update.full_name

    if user_update.is_active is not None:
        user.is_active = user_update.is_active

    session.commit()
    session.refresh(user)

    return user


@router.get("/", response_model=PaginatedUserResponse)
def get_all_users(
        session: SessionDep,
        page: int = Query(1, ge=1),
        size: int = Query(50, ge=1, le=100),
        sort_by: str = Query("id"),
        sort_order: str = Query("asc", regex="^(asc|desc)$"),
        search: Optional[str] = Query(None)
):
    query = select(User)

    if search:
        query = query.where(
            (User.username.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.full_name.ilike(f"%{search}%"))
        )

    count_query = select(func.count()).select_from(query.subquery())
    total = session.execute(count_query).scalar() or 0
    pages = (total + size - 1) // size if total > 0 else 1

    if sort_by:
        try:
            sort_column = getattr(User, sort_by)
            if sort_order.lower() == "desc":
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(asc(sort_column))
        except AttributeError:
            if sort_order.lower() == "desc":
                query = query.order_by(desc(User.id))
            else:
                query = query.order_by(asc(User.id))
    else:
        query = query.order_by(User.id)

    offset = (page - 1) * size
    query = query.offset(offset).limit(size)

    result = session.execute(query)
    items = result.scalars().all()

    return PaginatedUserResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1
    )