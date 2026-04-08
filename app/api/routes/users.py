#for userside application 

from fastapi import APIRouter, Depends, HTTPException, status # type: ignore
from sqlalchemy.orm import Session

from app.db.models import User # type: ignore

from app.db.database import SessionLocal# type: ignore
from app.schemas.user_schema import (
    UserCreate,
    UserUpdate,
    UserResponse,
)
from app.services.user_service import UserService # type: ignore
from app.api.dependencies import get_current_user  # ✅ FIXED IMPORT

router = APIRouter() 


# ================= DB DEP =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ================= CREATE =================

@router.post("/", response_model=UserResponse)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):

    service = UserService(db)

    return service.create_user(payload)


# ================= GET CURRENT USER =================

@router.get("/me", response_model=UserResponse)
def get_me(current_user = Depends(get_current_user)):
    return current_user


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    service = UserService(db)
    return service.get_all_users()


# ================= GET BY ID =================

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):

    service = UserService(db)

    user = service.get_user_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


# ================= UPDATE =================

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
):

    service = UserService(db)

    return service.update_user(user_id, payload)  # ✅ FIXED


@router.delete("/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )

    service = UserService(db)
    service.delete_user(user_id)

    return {"message": "User deleted"}