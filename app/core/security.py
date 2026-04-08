# app/core/security.py

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.core.config import settings

# ================= CONFIG =================

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

JWT_ISSUER = settings.JWT_ISSUER
JWT_AUDIENCE = settings.JWT_AUDIENCE

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# =========================================================
# PASSWORD UTILITIES
# =========================================================

def get_password_hash(password: str) -> str:
    """
    Hash a plaintext password.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# =========================================================
# JWT TOKEN CREATION
# =========================================================

def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create a signed JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "iss": JWT_ISSUER,
            "aud": JWT_AUDIENCE,
        }
    )

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# =========================================================
# JWT TOKEN DECODING
# =========================================================

def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate JWT token.
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=JWT_AUDIENCE,
            issuer=JWT_ISSUER,
        )
        return payload

    except JWTError as e:
        raise e


# =========================================================
# HELPER: EXTRACT USER ID
# =========================================================

def get_user_id_from_token(token: str) -> int:
    """
    Extract user ID from token subject.
    """

    payload = decode_token(token)

    sub = payload.get("sub")

    if sub is None:
        raise ValueError("Token missing subject")

    return int(sub)