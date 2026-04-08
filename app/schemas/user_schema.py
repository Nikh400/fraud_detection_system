# app/schemas/user_schema.py

from pydantic import BaseModel, EmailStr  # type: ignore
from typing import Optional


# =========================================================
# CREATE USER (REGISTER)
# =========================================================

class UserCreate(BaseModel):
    email: EmailStr
    password: str


# =========================================================
# LOGIN USER
# =========================================================

class UserLogin(BaseModel):
    email: EmailStr
    password: str


# =========================================================
# UPDATE USER
# =========================================================

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None


# =========================================================
# USER RESPONSE (SAFE OUTPUT)
# =========================================================

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool = True

    class Config:
        orm_mode = True   # Required for SQLAlchemy models


# =========================================================
# TOKEN RESPONSE
# =========================================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"