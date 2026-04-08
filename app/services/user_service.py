# app/services/user_service.py

from typing import Optional, List

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.schemas.user_schema import UserCreate, UserUpdate
from app.core.security import get_password_hash, verify_password


class UserService:
    """
    Handles user-related business logic:
    - Create users
    - Authenticate users
    - Fetch users
    - Update users
    - Delete users
    """

    def __init__(self, db: Session):
        self.db = db

    # --------------------------------------------------
    # CREATE USER
    # --------------------------------------------------

    def create_user(self, user_data: UserCreate) -> User:
        """
        Register a new user.
        """

        hashed_password = get_password_hash(user_data.password)

        new_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            is_active=True,
        )

        self.db.add(new_user)

        try:
            self.db.commit()
            self.db.refresh(new_user)
        except IntegrityError:
            self.db.rollback()
            raise ValueError("User with this email already exists")

        return new_user

    # --------------------------------------------------
    # AUTHENTICATE USER (FIXED)
    # --------------------------------------------------

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """
        Validate email & password.
        """

        user = self.get_user_by_email(email)

        if not user:
            return None

        if not verify_password(password, str(user.hashed_password)):
            return None

        if not user.is_active:
            return None

        return user

    # --------------------------------------------------
    # GET USER BY ID
    # --------------------------------------------------

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    # --------------------------------------------------
    # GET USER BY EMAIL
    # --------------------------------------------------

    def get_user_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    # --------------------------------------------------
    # GET ALL USERS (FIXED)
    # --------------------------------------------------

    def get_all_users(self) -> List[User]:
        return self.db.query(User).all()

    # --------------------------------------------------
    # UPDATE USER
    # --------------------------------------------------

    def update_user(self, user_id: int, data: UserUpdate) -> User:

        user = self.get_user_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        if data.email is not None:
            user.email = str(data.email)

        if data.password is not None:
            user.hashed_password = get_password_hash(data.password)

        self.db.commit()
        self.db.refresh(user)

        return user

    # --------------------------------------------------
    # DELETE USER
    # --------------------------------------------------

    def delete_user(self, user_id: int) -> bool:

        user = self.get_user_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        self.db.delete(user)
        self.db.commit()

        return True

    # --------------------------------------------------
    # DEACTIVATE USER
    # --------------------------------------------------

    def deactivate_user(self, user_id: int) -> User:

        user = self.get_user_by_id(user_id)

        if not user:
            raise ValueError("User not found")

        user.is_active = False

        self.db.commit()
        self.db.refresh(user)

        return user