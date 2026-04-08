# app/api/routes/auth.py

from fastapi import APIRouter, Depends, HTTPException, status  # type: ignore

from sqlalchemy.orm import Session  # type: ignore

from app.schemas.auth_schema import (  # type: ignore
    SignupRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)

from app.db.database import SessionLocal  # type: ignore
from app.db.models import User  # type: ignore
from app.core.security import (  # type: ignore
    get_password_hash,
    verify_password,
    create_access_token,
)

router = APIRouter()

# ================= SCHEMAS ================= 
# Moved to app/schemas/auth_schema.py




def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= SIGNUP =================

@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):

    email = payload.email.lower()

    # Check if user exists
    existing = db.query(User).filter(User.email == email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    user = User(
        email=email,
        hashed_password=get_password_hash(payload.password),
        role="user",
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ================= LOGIN =================

from fastapi.security import OAuth2PasswordRequestForm  # type: ignore

@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    email = form_data.username.strip().lower()

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive",
        )

    if not verify_password(form_data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role,
        }
    )

    return TokenResponse(access_token=token)


