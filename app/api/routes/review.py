# app/api/routes/review.py

from fastapi import APIRouter, HTTPException, Depends  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from app.schemas.review_schema import ReviewRequest, ReviewResponse  # type: ignore
from app.db.database import SessionLocal  # type: ignore
# Assuming Review model will be added to app.db.models
from app.db.models import Review  # type: ignore

router = APIRouter(prefix="/review", tags=["Human Review"])


# ================= SCHEMA =================
# Moved to app/schemas/review_schema.py

# ================= DATABASE DEPENDENCY =================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ================= ENDPOINT =================

from datetime import datetime

@router.post("/submit", response_model=ReviewResponse)
def submit_review(review: ReviewRequest, db: Session = Depends(get_db)):
    """
    Submit human verification for a transaction.

    Used for:
    - Feedback loop
    - Model improvement
    - Audit trails
    """

    try:
        db_review = Review(
            transaction_id=review.transaction_id,
            predicted_label=review.predicted_label,
            actual_label=review.actual_label,
            reviewer_id=review.reviewer_id,
            notes=review.notes
        )
        db.add(db_review)
        db.commit()
        db.refresh(db_review)

        return ReviewResponse(
            status="success",
            message="Review submitted successfully to the database",
            timestamp=datetime.utcnow()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ping")
def review_service_health():
    return {"status": "review service active"}