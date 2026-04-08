# ml/training/train_ensemble.py

import numpy as np
import pandas as pd

from app.ml_models.ensemble_model import SimpleNN
from app.services.feature_engineering import FeatureEngineer


def train():

    # -------- Synthetic training data --------

    df = pd.DataFrame({
        "amount": np.random.exponential(120, 500),
        "age": np.random.randint(18, 70, 500),
        "hour": np.random.randint(0, 24, 500),
        "category": np.random.choice(
            ["Electronics", "Food", "Travel", "Gaming"],
            500
        ),
        "device": np.random.choice(
            ["Mobile", "Desktop"],
            500
        ),
        "location": np.random.choice(
            ["Local", "International"],
            500
        )
    })

    texts = ["online purchase"] * 500

    labels = (df["amount"] > 300).astype(int).values

    # -------- Feature Engineering --------

    fe = FeatureEngineer()
    X = fe.build_features(df, texts, fit=True)

    # -------- Train Model --------

    model = SimpleNN([X.shape[1], 64, 32, 1])
    model.train(X, labels, epochs=30)

    print("Training complete")


if __name__ == "__main__":
    train()
