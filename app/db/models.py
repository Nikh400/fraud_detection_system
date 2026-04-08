from datetime import datetime

from sqlalchemy import String, Boolean, DateTime, Index, func, Integer, Text  # type: ignore
from sqlalchemy.orm import Mapped, mapped_column  # type: ignore

from app.db.database import Base  # type: ignore


class User(Base):
    __tablename__ = "users"

    # ================= PRIMARY KEY =================
    id: Mapped[int] = mapped_column(primary_key=True)

    # ================= AUTH FIELDS =================
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # ================= AUTHORIZATION =================
    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="user",
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # ================= TIMESTAMPS =================
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    # ================= INDEXES =================
    __table_args__ = (
        Index("ix_users_email_lower", func.lower(email), unique=True),
    )

    # ================= DEBUG REPRESENTATION =================
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


class UserDevice(Base):
    __tablename__ = "user_devices"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    device_fingerprint: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    
    first_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    last_seen_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )

    trust_score: Mapped[float] = mapped_column(
        Integer,
        nullable=False,
        default=0.0
    )

    def __repr__(self) -> str:
        return f"<UserDevice user_id={self.user_id} fingerprint={self.device_fingerprint}>"


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    predicted_label: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_label: Mapped[int] = mapped_column(Integer, nullable=False)
    reviewer_id: Mapped[str] = mapped_column(String(100), nullable=True)
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    def __repr__(self) -> str:
        return f"<Review id={self.id} transaction_id={self.transaction_id}>"