"""
Model-related API Schemas
Compatible with Pydantic v2
"""

from typing import Dict, List, Optional
from pydantic import BaseModel


# =========================================================
# Individual Model Status
# =========================================================

class ModelStatus(BaseModel):
    name: str
    loaded: bool
    version: Optional[str] = None
    accuracy: Optional[float] = None
    last_updated: Optional[str] = None


# =========================================================
# Health Check Response
# =========================================================

class ModelHealthResponse(BaseModel):
    status: str
    models: Dict[str, ModelStatus]


# =========================================================
# Model Metadata
# =========================================================

class ModelMetadata(BaseModel):
    name: str
    version: str
    description: Optional[str] = None
    input_features: Optional[List[str]] = None
    output: str = "fraud_probability"


# =========================================================
# Ensemble Details
# =========================================================

class EnsembleInfo(BaseModel):
    method: str
    models_used: List[str]
    weights: Optional[List[float]] = None


# =========================================================
# Model Load / Reload Response
# =========================================================

class ModelLoadResponse(BaseModel):
    success: bool
    message: str
    loaded_models: Optional[List[str]] = None


# =========================================================
# Error Response
# =========================================================

class ModelErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None