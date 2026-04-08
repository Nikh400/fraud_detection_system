# app/main.py

from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore

from app.db.database import engine, Base  # type: ignore
from app.api.routes import auth, fraud, users  # type: ignore
from app.services.model_service import ModelService  # type: ignore


# --------------------------------------------------
# DATABASE INIT
# --------------------------------------------------

Base.metadata.create_all(bind=engine)


# --------------------------------------------------
# APP INIT
# --------------------------------------------------

app = FastAPI(
    title="Fraud Detection Auth System",
    version="1.0.0",
)


# --------------------------------------------------
# CORS (Dev Config)
# --------------------------------------------------

from app.core.config import settings  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# ROUTES
# --------------------------------------------------

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(fraud.router, prefix="/fraud", tags=["Fraud"])


# --------------------------------------------------
# STARTUP EVENT
# --------------------------------------------------

@app.on_event("startup")
def load_models():
    """
    Load all ML models once at application startup.
    Store ModelService in app.state for global access.
    """

    model_service = ModelService()

    model_service.load_all(
        fraud_model_path="ml/saved_models/fraud_model.npz",
        transaction_input_dim=12,
        behavior_input_dim=8,
        image_input_dim=64,
    )

    # Store globally
    app.state.model_service = model_service

    print("✅ Fraud detection models loaded successfully.")