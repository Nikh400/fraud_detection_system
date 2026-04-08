"""
Fraud Detection API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request  # type: ignore
from typing import Dict

from app.schemas.request_response import FraudRequest, FraudResponse  # type: ignore
from app.api.dependencies import get_current_user, get_db  # type: ignore
from sqlalchemy.orm import Session
from app.services.transaction_service import TransactionService  # type: ignore
from app.db.models import User  # type: ignore
from app.core.logger import logger  # type: ignore


# ================================
# Router
# ================================
router = APIRouter()


# ================================
# Health / Model Status Endpoint
# ================================
@router.get("/health")
async def fraud_health(request: Request):
    """
    Returns ML model health status.
    """

    try:
        model_service = request.app.state.model_service
        status_data = model_service.health_status()

        return {
            "status": "ok",
            "models": status_data,
        }

    except Exception as e:
        logger.error(f"Health check failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud service unavailable",
        )


# ================================
# User Risk Summary Endpoint
# ================================
@router.get("/score")
async def fraud_score(
    user: User = Depends(get_current_user),
):
    """
    Returns user fraud risk profile.
    (Currently static — can be DB-driven later)
    """

    logger.info(f"Fraud score requested by user {user.email}")

    return {
        "user": user.email,
        "risk_score": 12.0,
        "status": "LOW_RISK",
    }


# ================================
# Real-Time Prediction Endpoint
# ================================
@router.post("/predict", response_model=FraudResponse)
async def predict_fraud(
    req: FraudRequest,
    request: Request,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Real-time transaction fraud detection.
    Uses TransactionService pipeline.
    """

    logger.info(f"Fraud prediction requested by user {user.email}")

    try:
        # Get global ModelService
        model_service = request.app.state.model_service

        # Create TransactionService
        transaction_service = TransactionService(model_service)

        # Run evaluation pipeline
        response = transaction_service.evaluate_transaction(
            request=req,
            user_id=user.id,
            db=db
        )

        return response

    except ValueError as e:
        logger.warning(f"Validation error: {e}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except RuntimeError as e:
        logger.error(f"Model error: {e}")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Fraud model not available",
        )

    except Exception as e:
        logger.exception("Prediction failed")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed",
        )