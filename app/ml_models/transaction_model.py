#app/ml_models/transaction_model.py

import numpy as np
from typing import Optional


class TransactionModel:
    """
    Transaction-based fraud detection model.

    Uses tabular transaction features such as:
    - amount
    - merchant category
    - location risk
    - time of day
    - device type
    - payment method

    Input:
        Numerical feature vector per transaction

    Output:
        Fraud probability (0–1)
    """

    def __init__(
        self,
        input_dim: int,
        lr: float = 0.001,
        seed: Optional[int] = None
    ):
        if seed is not None:
            np.random.seed(seed)

        self.input_dim = input_dim
        self.lr = lr

        hidden1 = max(32, input_dim * 2)
        hidden2 = max(16, hidden1 // 2)

        # He initialization
        self.W1 = np.random.randn(input_dim, hidden1) * np.sqrt(2 / input_dim)
        self.b1 = np.zeros((1, hidden1))

        self.W2 = np.random.randn(hidden1, hidden2) * np.sqrt(2 / hidden1)
        self.b2 = np.zeros((1, hidden2))

        self.W3 = np.random.randn(hidden2, 1) * np.sqrt(2 / hidden2)
        self.b3 = np.zeros((1, 1))

    # ---------------- Activations ---------------- #

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -10, 10)))

    # ---------------- Forward ---------------- #

    def forward(self, X: np.ndarray) -> np.ndarray:
        if not isinstance(X, np.ndarray):
            X = np.array(X, dtype=np.float32)

        self.X = X.astype(np.float32)

        self.z1 = np.dot(self.X, self.W1) + self.b1
        self.a1 = self.relu(self.z1)

        self.z2 = np.dot(self.a1, self.W2) + self.b2
        self.a2 = self.relu(self.z2)

        self.z3 = np.dot(self.a2, self.W3) + self.b3
        output = self.sigmoid(self.z3)

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
        verbose: bool = True
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

                # Backprop Layer 3
                dW3 = np.dot(self.a2.T, grad_output) / len(Xb)
                db3 = np.mean(grad_output, axis=0, keepdims=True)

                # Backprop Layer 2
                grad2 = np.dot(grad_output, self.W3.T)
                grad2[self.z2 <= 0] = 0

                dW2 = np.dot(self.a1.T, grad2) / len(Xb)
                db2 = np.mean(grad2, axis=0, keepdims=True)

                # Backprop Layer 1
                grad1 = np.dot(grad2, self.W2.T)
                grad1[self.z1 <= 0] = 0

                dW1 = np.dot(Xb.T, grad1) / len(Xb)
                db1 = np.mean(grad1, axis=0, keepdims=True)

                # Update weights
                self.W3 -= self.lr * dW3
                self.b3 -= self.lr * db3

                self.W2 -= self.lr * dW2
                self.b2 -= self.lr * db2

                self.W1 -= self.lr * dW1
                self.b1 -= self.lr * db1

            if verbose and epoch % 10 == 0:
                preds = (self.forward(X) > 0.5).flatten()
                acc = np.mean(preds == y.flatten())
                print(f"[TransactionModel] Epoch {epoch}: accuracy={acc:.3f}")

    # ---------------- Persistence ---------------- #

    def get_parameters(self):
        return {
            "W1": self.W1,
            "b1": self.b1,
            "W2": self.W2,
            "b2": self.b2,
            "W3": self.W3,
            "b3": self.b3,
        }

    def set_parameters(self, params: dict):
        self.W1 = params["W1"]
        self.b1 = params["b1"]
        self.W2 = params["W2"]
        self.b2 = params["b2"]
        self.W3 = params["W3"]
        self.b3 = params["b3"]