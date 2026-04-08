"""
Transaction-related API Schemas
Compatible with Pydantic v2
"""

from typing import Optional
from pydantic import BaseModel, Field


# =========================================================
# Incoming Transaction Request
# =========================================================

class TransactionRequest(BaseModel):
    """
    Input data for transaction fraud prediction
    """

    amount: float = Field(..., gt=0)
    age: int = Field(..., ge=0, le=120)
    hour: int = Field(..., ge=0, le=23)

    category: str
    device_fingerprint: str
    location: str

    description: Optional[str] = ""


# =========================================================
# Transaction Prediction Result
# =========================================================

class TransactionPrediction(BaseModel):
    """
    Output of transaction-only fraud model
    """

    probability: float = Field(..., ge=0, le=1)
    is_fraud: bool


# =========================================================
# Full Transaction Record (DB / Logs)
# =========================================================

class TransactionRecord(BaseModel):
    """
    Complete transaction data including prediction result
    """

    transaction_id: Optional[str] = None
    user_id: Optional[int] = None

    amount: float
    age: int
    hour: int

    category: str
    device: str
    location: str
    description: Optional[str] = ""

    probability: Optional[float] = None
    is_fraud: Optional[bool] = None

    timestamp: Optional[str] = None


# =========================================================
# Transaction Risk Summary
# =========================================================

class TransactionRiskSummary(BaseModel):
    """
    Summary risk label for UI / dashboards
    """

    risk_score: float
    risk_level: str  # LOW / MEDIUM / HIGH