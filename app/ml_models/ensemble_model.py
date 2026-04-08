# app/models/ensemble_model.py

import numpy as np
import math


class SimpleNN:
    """
    Core neural network engine for ensemble fraud scoring.

    Responsibilities:
    - Forward pass (inference)
    - Optional training
    - Parameter management

    NO preprocessing
    NO business logic
    NO API dependencies
    """

    def __init__(self, layer_sizes, lr=0.01, seed=None):
        if seed is not None:
            np.random.seed(seed)

        self.layer_sizes = layer_sizes
        self.lr = lr
        self.weights = []
        self.biases = []

        # Xavier initialization
        for i in range(len(layer_sizes) - 1):
            limit = math.sqrt(6 / (layer_sizes[i] + layer_sizes[i + 1]))
            w = np.random.uniform(-limit, limit,
                                  (layer_sizes[i], layer_sizes[i + 1]))
            b = np.zeros((1, layer_sizes[i + 1]))

            self.weights.append(w.astype(np.float32))
            self.biases.append(b.astype(np.float32))

    # ---------- Activations ----------

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-np.clip(x, -10, 10)))

    @staticmethod
    def relu(x):
        return np.maximum(0, x)

    # ---------- Forward ----------

    def forward(self, X):
        if not isinstance(X, np.ndarray):
            X = np.array(X, dtype=np.float32)

        self.activations = [X]

        for i in range(len(self.weights) - 1):
            z = np.dot(self.activations[-1], self.weights[i]) + self.biases[i]
            a = self.relu(z)
            self.activations.append(a)

        z = np.dot(self.activations[-1], self.weights[-1]) + self.biases[-1]
        return self.sigmoid(z)

    # ---------- Prediction ----------

    def predict_proba(self, X):
        return self.forward(X)

    def predict(self, X, threshold=0.5):
        probs = self.forward(X)
        return (probs > threshold).astype(int)

    # ---------- Training (optional) ----------

    def train(self, X, y, epochs=50, batch_size=32, verbose=True):

        X = np.array(X, dtype=np.float32)
        y = np.array(y, dtype=np.float32).reshape(-1, 1)

        n = len(X)

        for epoch in range(epochs):

            idx = np.random.permutation(n)

            for i in range(0, n, batch_size):
                batch_idx = idx[i:i + batch_size]
                Xb = X[batch_idx]
                yb = y[batch_idx]

                output = self.forward(Xb)
                error = output - yb
                grad = error * output * (1 - output)

                for l in range(len(self.weights) - 1, -1, -1):
                    dw = np.dot(self.activations[l].T, grad) / len(Xb)
                    self.weights[l] -= self.lr * dw

                    if l > 0:
                        grad = np.dot(grad, self.weights[l].T)
                        grad *= (self.activations[l] > 0)

            if verbose and epoch % 10 == 0:
                pred = (self.forward(X) > 0.5).flatten()
                acc = np.mean(pred == y.flatten())
                print(f"Epoch {epoch}: accuracy={acc:.3f}")

    # ---------- Persistence ----------

    def get_parameters(self):
        return self.weights, self.biases

    def set_parameters(self, weights, biases):
        self.weights = weights
        self.biases = biases


__all__ = ["SimpleNN"]
