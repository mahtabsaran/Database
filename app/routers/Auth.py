from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from datetime import datetime, timedelta
from app.db import SessionDep
from ..schemas.Auth import (
    TokenRequest, TokenResponse, RefreshTokenRequest,
    RefreshTokenResponse, ChangePasswordRequest, LogoutRequest
)
from ..models.User import User
from ..models.Auth import Auth
from app.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="", tags=["Auth"])


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(session: SessionDep, token_request: TokenRequest):
    user = session.execute(
        select(User).where(
            (User.username == token_request.username) |
            (User.email == token_request.username)
        )
    ).scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid username or password")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is inactive")

    if not verify_password(token_request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    existing_tokens = session.execute(
        select(Auth).where(
            (Auth.user_id == user.id) &
            (Auth.is_active == True)
        )
    ).scalars().all()

    for token in existing_tokens:
        token.is_active = False
    session.commit()

    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    auth_db = Auth(
        user_id=user.id,
        access_token=access_token,
        refresh_token=refresh_token,
        expires_at=expires_at
    )

    session.add(auth_db)
    session.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/refresh-token", response_model=RefreshTokenResponse)
def refresh_access_token(session: SessionDep, refresh_request: RefreshTokenRequest):
    payload = verify_token(refresh_request.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    auth_db = session.execute(
        select(Auth).where(
            (Auth.refresh_token == refresh_request.refresh_token) &
            (Auth.is_active == True)
        )
    ).scalar_one_or_none()

    if not auth_db:
        raise HTTPException(status_code=401, detail="Refresh token not found or expired")

    user = session.execute(
        select(User).where(User.id == auth_db.user_id)
    ).scalar_one_or_none()

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")

    auth_db.is_active = False
    session.commit()

    token_data = {"sub": str(user.id), "username": user.username}
    new_access_token = create_access_token(token_data)

    expires_at = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_auth_db = Auth(
        user_id=user.id,
        access_token=new_access_token,
        refresh_token=auth_db.refresh_token,
        expires_at=expires_at
    )

    session.add(new_auth_db)
    session.commit()

    return RefreshTokenResponse(
        access_token=new_access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/logout")
def logout(session: SessionDep, logout_request: LogoutRequest):
    auth_db = session.execute(
        select(Auth).where(
            (Auth.refresh_token == logout_request.refresh_token) &
            (Auth.is_active == True)
        )
    ).scalar_one_or_none()

    if auth_db:
        auth_db.is_active = False
        session.commit()

    return {"message": "Successfully logged out"}


@router.post("/changepassword/")
def change_password(session: SessionDep, change_request: ChangePasswordRequest):
    user = session.execute(select(User).order_by(User.id)).first()

    if not user:
        raise HTTPException(status_code=404, detail="No user found")

    user = user[0]

    if not verify_password(change_request.current_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    user.password_hash = get_password_hash(change_request.new_password)

    auth_tokens = session.execute(
        select(Auth).where(Auth.user_id == user.id)
    ).scalars().all()

    for auth_token in auth_tokens:
        auth_token.is_active = False

    session.commit()

    return {"message": "Password changed successfully"}