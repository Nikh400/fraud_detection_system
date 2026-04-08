"""
Feature preprocessing utilities for Fraud Detection System

Transforms raw API input into model-ready numerical features.
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List


# =========================================================
# TABULAR PREPROCESSING
# =========================================================

def preprocess_tabular(
    data: Dict[str, Any],
    label_maps: Dict[str, Dict[str, int]] | None = None,
    scaler_mean: pd.Series | None = None,
    scaler_std: pd.Series | None = None,
    fit: bool = False,
):
    """
    Convert transaction dictionary into normalized numeric vector.
    """

    df = pd.DataFrame([data]).copy()

    cat_cols = ["category", "device", "location"]
    num_cols = ["amount", "age", "hour"]

    if label_maps is None:
        label_maps = {}

    # -------- CATEGORICAL ENCODING --------
    for col in cat_cols:
        if col in df.columns:
            if fit or col not in label_maps:
                uniques = df[col].astype(str).unique()
                label_maps[col] = {v: i for i, v in enumerate(uniques)}

            df[col] = df[col].astype(str).map(
                lambda x: label_maps[col].get(x, -1)
            )

    # -------- NUMERIC NORMALIZATION --------
    if num_cols:
        if fit:
            scaler_mean = df[num_cols].mean()
            scaler_std = df[num_cols].std() + 1e-8

        if scaler_mean is not None and scaler_std is not None:
            df[num_cols] = (df[num_cols] - scaler_mean) / scaler_std

    return (
        df.fillna(0).values.astype(np.float32),
        label_maps,
        scaler_mean,
        scaler_std,
    )


# =========================================================
# TEXT PREPROCESSING
# =========================================================

def preprocess_text(
    texts: List[str],
    vocab: Dict[str, int] | None = None,
    max_features: int = 50,
    fit: bool = False,
):
    """
    Bag-of-words vectorization for transaction descriptions.
    """

    if vocab is None:
        vocab = {}

    # -------- BUILD VOCAB --------
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

        vocab = {w: i for i, (w, _) in enumerate(top_words)}

    size = max(len(vocab), 1)
    features = np.zeros((len(texts), size), dtype=np.float32)

    # -------- VECTORIZE --------
    for i, text in enumerate(texts):
        words = re.findall(r"\b\w{3,}\b", str(text).lower())
        for w in words:
            if w in vocab:
                features[i, vocab[w]] += 1

    return features, vocab


# =========================================================
# IMAGE PREPROCESSING (Placeholder)
# =========================================================

def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Basic image preprocessing for fraud image models.
    Replace with actual CV pipeline if needed.
    """

    if not image_bytes:
        return np.zeros((1,), dtype=np.float32)

    # Example: convert byte size into feature
    size_feature = len(image_bytes) / 1_000_000  # MB scale

    return np.array([size_feature], dtype=np.float32)


# =========================================================
# FULL PIPELINE
# =========================================================

def build_feature_vector(
    txn: Dict[str, Any],
    label_maps=None,
    scaler_mean=None,
    scaler_std=None,
    vocab=None,
):
    """
    Combine tabular + text features into single vector.
    """

    X_tab, label_maps, scaler_mean, scaler_std = preprocess_tabular(
        txn,
        label_maps,
        scaler_mean,
        scaler_std,
        fit=False,
    )

    X_text, vocab = preprocess_text(
        [txn.get("description", "")],
        vocab,
        fit=False,
    )

    X = np.hstack([X_tab, X_text]).astype(np.float32)

    return X, label_maps, scaler_mean, scaler_std, vocab