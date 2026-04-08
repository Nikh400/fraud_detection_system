# app/ml_models/behavior_model.py

import numpy as np
from typing import Optional


class BehaviorModel:
    """
    Behavioral anomaly detection model.

    Detects suspicious patterns such as:
    - Sudden spending spikes
    - Multiple devices
    - Geo diversity
    - High transaction velocity

    Lightweight neural scoring model.
    """

    def __init__(self, input_dim: int, lr: float = 0.001, seed: Optional[int] = None):
        if seed is not None:
            np.random.seed(seed)

        self.input_dim = input_dim
        self.lr = lr

        # Simple 2-layer network
        hidden_dim = max(16, input_dim // 2)

        self.W1 = np.random.randn(input_dim, hidden_dim) * np.sqrt(2 / input_dim)
        self.b1 = np.zeros((1, hidden_dim))

        self.W2 = np.random.randn(hidden_dim, 1) * np.sqrt(2 / hidden_dim)
        self.b2 = np.zeros((1, 1))

    # ---------------- Activations ---------------- #

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -10, 10)))

    # ---------------- Forward Pass ---------------- #

    def forward(self, X: np.ndarray) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X, dtype=np.float32)

        self.X = X.astype(np.float32)

        self.z1 = np.dot(self.X, self.W1) + self.b1
        self.a1 = self.relu(self.z1)

        self.z2 = np.dot(self.a1, self.W2) + self.b2
        output = self.sigmoid(self.z2)

        return output

    # ---------------- Prediction ---------------- #

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        return self.forward(X)

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        probs = self.forward(X)
        return (probs > threshold).astype(int)

    # ---------------- Training ---------------- #

    def train(
        self,
        X: np.ndarray,
        y: np.ndarray,
        epochs: int = 50,
        batch_size: int = 32,
        verbose: bool = True,
    ):

        X = np.asarray(X, dtype=np.float32)
        y = np.asarray(y, dtype=np.float32).reshape(-1, 1)

        n = len(X)

        for epoch in range(epochs):

            idx = np.random.permutation(n)

            for i in range(0, n, batch_size):
                batch_idx = idx[i:i + batch_size]
                Xb = X[batch_idx]
                yb = y[batch_idx]

                # Forward
                output = self.forward(Xb)

                # Binary cross-entropy gradient
                error = output - yb
                grad_output = error * output * (1 - output)

                # Backprop second layer
                dW2 = np.dot(self.a1.T, grad_output) / len(Xb)
                db2 = np.mean(grad_output, axis=0, keepdims=True)

                # Backprop first layer
                grad_hidden = np.dot(grad_output, self.W2.T)
                grad_hidden[self.z1 <= 0] = 0

                dW1 = np.dot(Xb.T, grad_hidden) / len(Xb)
                db1 = np.mean(grad_hidden, axis=0, keepdims=True)

                # Update
                self.W2 -= self.lr * dW2
                self.b2 -= self.lr * db2
                self.W1 -= self.lr * dW1
                self.b1 -= self.lr * db1

            if verbose and epoch % 10 == 0:
                preds = (self.forward(X) > 0.5).flatten()
                acc = np.mean(preds == y.flatten())
                print(f"[BehaviorModel] Epoch {epoch}: accuracy={acc:.3f}")

    # ---------------- Persistence ---------------- #

    def get_parameters(self):
        return {
            "W1": self.W1,
            "b1": self.b1,
            "W2": self.W2,
            "b2": self.b2,
        }

    def set_parameters(self, params: dict):
        self.W1 = params["W1"]
        self.b1 = params["b1"]
        self.W2 = params["W2"]
        self.b2 = params["b2"]