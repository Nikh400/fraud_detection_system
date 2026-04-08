# app/api/routes/model.py

from fastapi import APIRouter, HTTPException
from app.services.model_service import ModelService

router = APIRouter(prefix="/model", tags=["Model Management"])

model_service = ModelService()


@router.get("/health")
def model_health():
    """
    Check whether all models are loaded and ready.
    """
    try:
        return {
            "status": "ok",
            "models": model_service.health_status()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
def reload_fraud_model(model_path: str):
    """
    Hot reload fraud model without restarting server.
    """
    try:
        model_service.reload_fraud_model(model_path)

        return {
            "status": "success",
            "message": "Fraud model reloaded successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
def model_info():
    """
    Basic info about loaded models.
    """
    status = model_service.health_status()

    return {
        "service": "Fraud Detection Model Service",
        "loaded_models": status
    }