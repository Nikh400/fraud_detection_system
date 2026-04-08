import re
from typing import Dict, Any, List, Optional

import numpy as np
import pandas as pd

from app.ml_models.transaction_model import TransactionModel
from app.ml_models.behavior_model import BehaviorModel
from app.ml_models.image_model import ImageModel
from app.ml_models.ensemble_model import SimpleNN


# =========================================================
# ENSEMBLE API SCORING
# =========================================================

class EnsembleScorer:
    """
    Combines individual model predictions.
    """

    def __init__(
        self,
        transaction_model: TransactionModel,
        behavior_model: BehaviorModel,
        image_model: ImageModel,
    ):
        self.transaction_model = transaction_model
        self.behavior_model = behavior_model
        self.image_model = image_model

        self.weights = np.array([0.4, 0.3, 0.3], dtype=np.float32)

    def detect_fraud(self, request) -> Dict[str, Any]:

        txn_score = float(
            self.transaction_model.predict_proba(
                np.array([request.transaction])
            )[0][0]
        )

        behavior_score = float(
            self.behavior_model.predict_proba(
                np.array([request.behavior])
            )[0][0]
        )

        image_score = float(
            self.image_model.predict_proba(
                np.array([request.image])
            )[0][0]
        )

        scores = np.array(
            [txn_score, behavior_score, image_score],
            dtype=np.float32,
        )

        final_score = float(np.dot(scores, self.weights))

        return {
            "is_fraud": final_score > 0.5,
            "probability": final_score,
            "risk_score": final_score * 100.0,
            "model_scores": {
                "transaction": txn_score,
                "behavior": behavior_score,
                "image": image_score,
            },
        }


# =========================================================
# NEURAL NETWORK FRAUD SERVICE
# =========================================================

class FraudService:
    """
    Neural-network based fraud scoring service
    for tabular + text transaction data.
    """

    def __init__(self, model_path: Optional[str] = None):
        self.scaler_mean: Optional[pd.Series] = None
        self.scaler_std: Optional[pd.Series] = None
        self.label_maps: Dict[str, Dict[str, int]] = {}
        self.vocab: Dict[str, int] = {}

        self.model: Optional[SimpleNN] = None
        self.input_dim: Optional[int] = None

        if model_path:
            self.load_model(model_path)

    # =====================================================
    # PREPROCESSING
    # =====================================================

    def preprocess_tabular(self, df: pd.DataFrame, fit: bool = False) -> np.ndarray:
        df_proc = df.copy()

        cat_cols = ["category", "location"]
        num_cols = ["amount", "age", "hour", "is_known_device", "device_age_days", "device_velocity_30d"]

        for col in cat_cols:
            if col in df_proc.columns:

                if fit or col not in self.label_maps:
                    uniques = df_proc[col].astype(str).unique()
                    self.label_maps[col] = {v: i for i, v in enumerate(uniques)}

                df_proc[col] = (
                    df_proc[col]
                    .astype(str)
                    .map(lambda x: self.label_maps[col].get(x, -1))
                )

        if num_cols:
            if fit:
                self.scaler_mean = df_proc[num_cols].mean()
                self.scaler_std = df_proc[num_cols].std() + 1e-8

            if self.scaler_mean is not None and self.scaler_std is not None:
                # Convert the specific num_cols to numpy first to avoid pandas index alignment issues
                # with the loaded scaler which has missing/integer indices
                target_mean = self.scaler_mean.to_numpy()[:len(num_cols)]
                target_std = self.scaler_std.to_numpy()[:len(num_cols)]
                df_proc[num_cols] = (
                    df_proc[num_cols].to_numpy() - target_mean
                ) / target_std
        # Drop pure text or unused features before casting to float tensor
        if "description" in df_proc.columns:
            df_proc = df_proc.drop(columns=["description"])
            
        final_cols = cat_cols + num_cols
        return df_proc[final_cols].fillna(0).to_numpy(dtype=np.float32)

    def preprocess_text(
        self,
        texts: List[str],
        fit: bool = False,
        max_features: int = 50,
    ) -> np.ndarray:

        if fit:
            word_counts: Dict[str, int] = {}

            for text in texts:
                words = re.findall(r"\b\w{3,}\b", str(text).lower())
                for w in words:
                    word_counts[w] = word_counts.get(w, 0) + 1

            top_words = sorted(
                word_counts.items(),
                key=lambda x: -x[1]
            )[:max_features]

            self.vocab = {w: i for i, (w, _) in enumerate(top_words)}

        size = max(len(self.vocab), 1)
        features = np.zeros((len(texts), size), dtype=np.float32)

        for i, text in enumerate(texts):
            words = re.findall(r"\b\w{3,}\b", str(text).lower())

            for w in words:
                if w in self.vocab:
                    features[i, self.vocab[w]] += 1

        return features

    # =====================================================
    # TRAINING
    # =====================================================

    def train(
        self,
        df: pd.DataFrame,
        descriptions: List[str],
        labels: List[int],
        epochs: int = 50,
    ):
        print("Training fraud model...")

        X_tab = self.preprocess_tabular(df, fit=True)
        X_text = self.preprocess_text(descriptions, fit=True)

        X = np.hstack([X_tab, X_text]).astype(np.float32)
        y = np.asarray(labels, dtype=np.float32)

        self.input_dim = X.shape[1]

        # Initialize neural network
        self.model = SimpleNN(
            [self.input_dim, 64, 32, 1],
            lr=0.001
        )

        self.model.train(X, y, epochs=epochs)

    # =====================================================
    # INFERENCE
    # =====================================================

    def predict(self, txn: Dict[str, Any]) -> Dict[str, Any]:

        if self.model is None:
            raise RuntimeError("Model not loaded.")

        df = pd.DataFrame([txn])
        text = [txn.get("description", "")]

        X_tab = self.preprocess_tabular(df, fit=False)
        X_text = self.preprocess_text(text, fit=False)

        X = np.hstack([X_tab, X_text]).astype(np.float32)

        prob = float(self.model.predict_proba(X)[0][0])

        return {
            "is_fraud": prob > 0.5,
            "probability": prob,
            "risk_score": prob * 100.0,
        }

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def save_model(self, path: str):

        if self.model is None:
            raise RuntimeError("No model to save.")

        weights, biases = self.model.get_parameters()

        # Build a flat dictionary to save variable length arrays without blowing up np.savez
        save_dict = {
            "scaler_mean": self.scaler_mean.to_numpy() if self.scaler_mean is not None else np.array([]),
            "scaler_std": self.scaler_std.to_numpy() if self.scaler_std is not None else np.array([]),
            "label_maps": np.array(self.label_maps, dtype=object),
            "vocab": np.array(self.vocab, dtype=object),
            "input_dim": np.array([self.input_dim], dtype=np.int32),
            "num_layers": np.array([len(weights)], dtype=np.int32),
        }
        
        for i, (w, b) in enumerate(zip(weights, biases)):
            save_dict[f"weight_{i}"] = w
            save_dict[f"bias_{i}"] = b

        np.savez(path, **save_dict)

    def load_model(self, path: str):

        data = np.load(path, allow_pickle=True)
        
        num_layers = int(data["num_layers"][0]) if "num_layers" in data else len([k for k in data.keys() if "weight_" in k])
        
        if num_layers > 0 and f"weight_0" in data:
            weights = [data[f"weight_{i}"] for i in range(num_layers)]
            biases = [data[f"bias_{i}"] for i in range(num_layers)]
        else:
            # Fallback for old model structure
            weights = list(data["weights"])
            biases = list(data["biases"])

        layer_sizes = [weights[0].shape[0]]
        for w in weights:
            layer_sizes.append(w.shape[1])

        self.model = SimpleNN(layer_sizes)
        self.model.set_parameters(weights, biases)

        self.input_dim = int(data["input_dim"][0])

        self.scaler_mean = pd.Series(data["scaler_mean"])
        self.scaler_std = pd.Series(data["scaler_std"])

        self.label_maps = dict(data["label_maps"].item())
        self.vocab = dict(data["vocab"].item())