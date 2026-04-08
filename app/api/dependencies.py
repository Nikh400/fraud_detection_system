# app/api/dependencies.py

from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import User
from app.services.model_service import ModelService
from app.core.security import decode_token


# =========================================================
# OAUTH2 SCHEME
# =========================================================

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================================================
# DATABASE SESSION
# =========================================================

def get_db() -> Generator[Session, None, None]:
    """
    Provides a database session per request.
    Ensures proper cleanup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================================================
# MODEL SERVICE (Safe Singleton)
# =========================================================

_model_service_instance: ModelService | None = None


def get_model_service() -> ModelService:
    """
    Lazy-loaded singleton model service.
    Prevents reloading ML model per request.
    """
    global _model_service_instance

    if _model_service_instance is None:
        _model_service_instance = ModelService()

    return _model_service_instance


# =========================================================
# AUTHENTICATED USER DEPENDENCY
# =========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Extract and validate current authenticated user from JWT token.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = decode_token(token)

        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception

        # Convert safely
        user_id_int = int(user_id)

    except (JWTError, ValueError):
        raise credentials_exception

    # SQLAlchemy 2.0 safe retrieval
    user = db.get(User, user_id_int)

    if user is None:
        raise credentials_exception

    if user.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    return user