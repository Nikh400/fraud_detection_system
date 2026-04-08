# app/db/database.py

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ================= CONFIG =================

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fraud.db")

# ================= ENGINE =================

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    # For Postgres/MySQL in production
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=1800,
    )

# ================= SESSION =================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # Important for FastAPI
)

# ================= BASE =================

Base = declarative_base()
