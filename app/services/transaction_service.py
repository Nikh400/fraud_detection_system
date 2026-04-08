# app/services/transaction_service.py

from app.services.model_service import ModelService
from app.schemas.request_response import FraudRequest, FraudResponse
from sqlalchemy.orm import Session
from app.db.models import UserDevice
from datetime import datetime, timezone, timedelta



class TransactionService:
    """
    Handles transaction validation, feature preparation,
    fraud scoring, and response generation.
    """

    def __init__(self, model_service: ModelService):
        self.model_service = model_service

    # --------------------------------------------------
    # MAIN PIPELINE
    # --------------------------------------------------

    def evaluate_transaction(
        self,
        request: FraudRequest,
        user_id: int,
        db: Session
    ) -> FraudResponse:

        self._validate_transaction(request)

        # Feature Engineering: Stateful Device Fingerprinting
        device_fingerprint = request.device_fingerprint
        now = datetime.now(timezone.utc)
        
        user_device = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.device_fingerprint == device_fingerprint
        ).first()
        
        if user_device:
            is_known_device = 1
            # Calculate age safely assuming timezone aware timestamps
            age_td = now - user_device.first_seen_at.replace(tzinfo=timezone.utc) if user_device.first_seen_at.tzinfo is None else now - user_device.first_seen_at
            device_age_days = age_td.days
            
            user_device.last_seen_at = now
            db.commit()
        else:
            is_known_device = 0
            device_age_days = 0
            new_device = UserDevice(
                user_id=user_id,
                device_fingerprint=device_fingerprint,
                first_seen_at=now,
                last_seen_at=now
            )
            db.add(new_device)
            db.commit()

        # Device Velocity in last 30 days
        thirty_days_ago = now - timedelta(days=30)
        device_velocity_30d = db.query(UserDevice).filter(
            UserDevice.user_id == user_id,
            UserDevice.last_seen_at >= thirty_days_ago
        ).count()

        features = self._prepare_features(
            request, 
            is_known_device=is_known_device, 
            device_age_days=device_age_days,
            device_velocity_30d=device_velocity_30d
        )

        # ✅ Get FraudService from ModelService
        fraud_service = self.model_service.get_fraud_service()

        # ✅ Predict using FraudService
        result = fraud_service.predict(features)

        probability = result.get("probability", 0.0)
        risk_score = result.get("risk_score", probability)
        is_fraud = result.get("is_fraud", probability > 0.8)

        status = self._get_status_label(probability)

        return FraudResponse(
            user_id=user_id,
            probability=probability,
            risk_score=risk_score,
            status=status,
            is_fraud=is_fraud,
        )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    def _validate_transaction(self, request: FraudRequest) -> None:

        if request.amount <= 0:
            raise ValueError("Transaction amount must be positive")

        if request.age <= 0:
            raise ValueError("Invalid age")

        if not (0 <= request.hour <= 23):
            raise ValueError("Hour must be between 0 and 23")

    # --------------------------------------------------
    # FEATURE ENGINEERING
    # --------------------------------------------------

    def _prepare_features(
        self, 
        request: FraudRequest, 
        is_known_device: int, 
        device_age_days: int, 
        device_velocity_30d: int
    ) -> dict:

        return {
            "amount": request.amount,
            "age": request.age,
            "hour": request.hour,
            "is_night": 1 if request.hour < 6 or request.hour > 22 else 0,
            "category": request.category,
            "is_known_device": is_known_device,
            "device_age_days": device_age_days,
            "device_velocity_30d": device_velocity_30d,
            "location": request.location,
            "description": request.description,
            "description_length": len(request.description or ""),
        }

    # --------------------------------------------------
    # SCORE → LABEL
    # --------------------------------------------------

    def _get_status_label(self, probability: float) -> str:

        if probability >= 0.85:
            return "HIGH_RISK"

        if probability >= 0.60:
            return "MEDIUM_RISK"

        return "LOW_RISK"