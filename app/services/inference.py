# app/services/inference.py

import numpy as np
from app.ml_models.ensemble_model import SimpleNN


class InferenceEngine:
    """
    Loads model and produces fraud probability
    """

    def __init__(self, model: SimpleNN):
        self.model = model

    def score(self, features: np.ndarray) -> float:

        prob = self.model.predict_proba(features)[0][0]
        return float(prob)

    def classify(self, prob: float):

        if prob >= 0.7:
            return "high_risk"
        elif prob >= 0.4:
            return "medium_risk"
        return "low_risk"
