# app/schemas/review_schema.py

from pydantic import BaseModel  # type: ignore
from typing import Optional
from datetime import datetime

class ReviewRequest(BaseModel):
    transaction_id: str
    predicted_label: int   # 0 = legit, 1 = fraud
    actual_label: int      # human verified
    reviewer_id: Optional[str] = None
    notes: Optional[str] = None

class ReviewResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
