# app/api/routes/health.py

from fastapi import APIRouter, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timezone

from app.db.database import engine

router = APIRouter(prefix="/health", tags=["System Health"])


# ================================
# LIVENESS PROBE
# ================================
@router.get("/", status_code=status.HTTP_200_OK)
def health_check():
    """
    Liveness probe — checks if service process is running.
    Used by orchestrators to detect crashed containers.
    """

    return {
        "status": "ok",
        "service": "fraud-detection-api",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ================================
# READINESS PROBE
# ================================
@router.get("/ready", status_code=status.HTTP_200_OK)
def readiness_check():
    """
    Readiness probe — checks if service is ready to serve traffic.
    Validates database connectivity.
    """

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        return {
            "status": "ready",
            "service": "fraud-detection-api",
            "database": "connected",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    except SQLAlchemyError:
        return {
            "status": "not_ready",
            "service": "fraud-detection-api",
            "database": "unavailable",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


# ================================
# DEEP HEALTH CHECK (OPTIONAL)
# ================================
@router.get("/deep", status_code=status.HTTP_200_OK)
def deep_health_check():
    """
    Deep health check — verifies all critical dependencies.
    Extend this for:
      - ML model loaded
      - Cache availability
      - External services
      - Fraud model readiness
    """

    db_status = "connected"

    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_status = "unavailable"

    overall_status = "ok" if db_status == "connected" else "degraded"

    return {
        "status": overall_status,
        "service": "fraud-detection-api",
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }