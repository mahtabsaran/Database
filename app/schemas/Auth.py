from pydantic import BaseModel
from typing import Optional

class TokenRequest(BaseModel):
    grant_type: Optional[str] = "password"
    username: str
    password: str
    scope: Optional[str] = ""
    client_id: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class RefreshTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

class LogoutRequest(BaseModel):
    refresh_token: str