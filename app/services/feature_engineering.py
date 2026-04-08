import numpy as np 
import pandas as pd
import re


class FeatureEngineer:
    """
    Converts raw transaction data into model-ready features.
    Handles tabular + text modalities.
    """

    def __init__(self):
        self.label_maps = {}       # For categorical encoding
        self.scaler_mean = None    # For numeric scaling
        self.scaler_std = None
        self.vocab = {}            # For text features

    # ================= TABULAR =================
    def transform_tabular(self, df: pd.DataFrame, fit=False) -> np.ndarray:
        df = df.copy()

        cat_cols = ["category", "device", "location"]
        num_cols = ["amount", "age", "hour"]

        # Encode categorical columns
        for col in cat_cols:
            if col not in df:
                continue

            if fit or col not in self.label_maps:
                unique_vals = df[col].astype(str).unique()
                self.label_maps[col] = {v: i for i, v in enumerate(unique_vals)}

            df[col] = df[col].astype(str).map(lambda x: self.label_maps[col].get(x, -1))

        # Scale numeric columns
        if fit:
            self.scaler_mean = df[num_cols].mean()
            self.scaler_std = df[num_cols].std() + 1e-8  # avoid divide by zero

        if self.scaler_mean is not None and self.scaler_std is not None:
            df[num_cols] = ((df[num_cols].to_numpy() - self.scaler_mean[num_cols].to_numpy()) /
                            self.scaler_std[num_cols].to_numpy())

        return df.fillna(0).values.astype(np.float32)


    # ================= TEXT =================
    def transform_text(self, texts, max_features=50, fit=False) -> np.ndarray:
        """
        Convert list of text entries into numeric bag-of-words features.
        """
        if isinstance(texts, str):
            texts = [texts]

        if fit:
            counts: dict[str, int] = {}
            for t in texts:
                words = re.findall(r"\b\w{3,}\b", str(t).lower())
                for w in words:
                    counts[w] = counts.get(w, 0) + 1

            # Take top max_features words
            top = sorted(counts.items(), key=lambda x: -x[1])[:max_features]
            self.vocab = {w: i for i, (w, _) in enumerate(top)}

        # Ensure output has shape (n_samples, max_features)
        n_features = max(len(self.vocab), max_features)
        X = np.zeros((len(texts), n_features), dtype=np.float32)

        for i, t in enumerate(texts):
            words = re.findall(r"\b\w{3,}\b", str(t).lower())
            for w in words:
                if w in self.vocab:
                    X[i, self.vocab[w]] += 1

        return X

    # ================= COMBINED =================
    def build_features(self, df: pd.DataFrame, texts, fit=False) -> np.ndarray:
        """
        Combine tabular and text features into a single feature array.
        """
        X_tab = self.transform_tabular(df, fit)
        X_txt = self.transform_text(texts, fit)
        return np.hstack([X_tab, X_txt])
