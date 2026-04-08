# app/services/model_service.py

from typing import Optional, Dict, Any
import threading

from app.services.fraud_service import FraudService, EnsembleScorer
from app.ml_models.transaction_model import TransactionModel
from app.ml_models.behavior_model import BehaviorModel
from app.ml_models.image_model import ImageModel


class ModelService:
    """
    Central model lifecycle manager (Singleton).

    Responsibilities:
    - Load models at startup
    - Cache models in memory
    - Provide access to FraudService & Ensemble
    - Thread-safe reloads
    - Health & readiness reporting
    - Model metadata exposure
    """

    _instance: Optional["ModelService"] = None
    _lock = threading.Lock()

    # ================= SINGLETON =================

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    # ================= INIT =================

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        self.fraud_service: Optional[FraudService] = None
        self.transaction_model: Optional[TransactionModel] = None
        self.behavior_model: Optional[BehaviorModel] = None
        self.image_model: Optional[ImageModel] = None
        self.ensemble_scorer: Optional[EnsembleScorer] = None

        # Metadata & status
        self._config: Dict[str, Any] = {}
        self._loaded: bool = False

        self._initialized = True

    # =========================================================
    # LOAD ALL MODELS (Startup)
    # =========================================================

    def load_all(
        self,
        fraud_model_path: str,
        transaction_input_dim: int,
        behavior_input_dim: int,
        image_input_dim: int,
    ) -> None:
        """
        Load all ML models into memory.
        Should be called once at application startup.
        """

        with self._lock:
            # Fraud model (tabular/text)
            self.fraud_service = FraudService(fraud_model_path)

            # Base models
            self.transaction_model = TransactionModel(transaction_input_dim)
            self.behavior_model = BehaviorModel(behavior_input_dim)
            self.image_model = ImageModel(image_input_dim)

            # Ensemble
            self.ensemble_scorer = EnsembleScorer(
                transaction_model=self.transaction_model,
                behavior_model=self.behavior_model,
                image_model=self.image_model,
            )

            # Save config for reload
            self._config = {
                "fraud_model_path": fraud_model_path,
                "transaction_input_dim": transaction_input_dim,
                "behavior_input_dim": behavior_input_dim,
                "image_input_dim": image_input_dim,
            }

            self._loaded = True

    # =========================================================
    # ACCESSORS
    # =========================================================

    def get_fraud_service(self) -> FraudService:
        if not self._loaded or self.fraud_service is None:
            raise RuntimeError("FraudService not loaded.")
        return self.fraud_service

    def get_ensemble(self) -> EnsembleScorer:
        if not self._loaded or self.ensemble_scorer is None:
            raise RuntimeError("EnsembleScorer not initialized.")
        return self.ensemble_scorer

    # =========================================================
    # HOT RELOAD (Fraud Model Only)
    # =========================================================

    def reload_fraud_model(self, model_path: str) -> None:
        """
        Reload fraud model without restarting server.
        """
        with self._lock:
            self.fraud_service = FraudService(model_path)
            self._config["fraud_model_path"] = model_path

    # =========================================================
    # FULL RELOAD (ALL MODELS)
    # =========================================================

    def reload_all(self) -> None:
        """
        Reload all models using stored configuration.
        """
        if not self._config:
            raise RuntimeError("No configuration available for reload.")

        self.load_all(**self._config)

    # =========================================================
    # MODEL INFO
    # =========================================================

    def get_model_info(self) -> Dict[str, Any]:
        """
        Returns model metadata/configuration.
        Useful for admin dashboards.
        """
        if not self._loaded:
            raise RuntimeError("Models not loaded.")

        return {
            "loaded": self._loaded,
            "config": self._config,
            "components": {
                "fraud_service": self.fraud_service is not None,
                "transaction_model": self.transaction_model is not None,
                "behavior_model": self.behavior_model is not None,
                "image_model": self.image_model is not None,
                "ensemble": self.ensemble_scorer is not None,
            },
        }

    # =========================================================
    # READINESS CHECK
    # =========================================================

    def is_ready(self) -> bool:
        """
        Returns True if system is ready to serve predictions.
        """
        return (
            self._loaded
            and self.fraud_service is not None
            and self.ensemble_scorer is not None
        )

    # =========================================================
    # HEALTH STATUS
    # =========================================================

    def health_status(self) -> Dict[str, bool]:
        """
        Lightweight health snapshot.
        Safe for public health endpoints.
        """
        return {
            "fraud_service_loaded": self.fraud_service is not None,
            "transaction_model_loaded": self.transaction_model is not None,
            "behavior_model_loaded": self.behavior_model is not None,
            "image_model_loaded": self.image_model is not None,
            "ensemble_ready": self.ensemble_scorer is not None,
            "system_ready": self.is_ready(),
        }