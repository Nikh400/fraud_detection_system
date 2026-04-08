# app/models/ensemble_model.py

import numpy as np  # type: ignore
import math


class SimpleNN:
    def __init__(self, layer_sizes, lr=0.01):
        self.layer_sizes = layer_sizes
        self.lr = lr
        self.weights = []
        self.biases = []
        self.activations = []
        self.z_values = []

        for i in range(len(layer_sizes) - 1):
            limit = math.sqrt(6 / (layer_sizes[i] + layer_sizes[i + 1]))
            w = np.random.uniform(
                -limit, limit,
                (layer_sizes[i], layer_sizes[i + 1])
            )
            b = np.zeros((1, layer_sizes[i + 1]))

            self.weights.append(w.astype(np.float32))
            self.biases.append(b.astype(np.float32))

    # ---------------- ACTIVATIONS ----------------

    def sigmoid(self, x):
        return 1 / (1 + np.exp(-x))

    def relu(self, x):
        return np.maximum(0, x)

    def relu_deriv(self, x):
        return (x > 0).astype(np.float32)

    # ---------------- FORWARD ----------------

    def forward(self, X):
        self.activations = [X]
        self.z_values = []

        A = X

        for i in range(len(self.weights) - 1):
            Z = A @ self.weights[i] + self.biases[i]
            A = self.relu(Z)

            self.z_values.append(Z)
            self.activations.append(A)

        # Output layer
        Z = A @ self.weights[-1] + self.biases[-1]
        A = self.sigmoid(Z)

        self.z_values.append(Z)
        self.activations.append(A)

        return A

    # ---------------- BACKWARD ----------------

    def backward(self, X, y):
        m = X.shape[0]
        A_out = self.activations[-1]
        dA = A_out - y

        for i in reversed(range(len(self.weights))):
            A_prev = self.activations[i]
            Z = self.z_values[i]

            if i == len(self.weights) - 1:
                dZ = dA
            else:
                dZ = dA * self.relu_deriv(Z)  # type: ignore

            dW = (A_prev.T @ dZ) / m
            dB = np.sum(dZ, axis=0, keepdims=True) / m

            if i > 0:
                dA = dZ @ self.weights[i].T

            self.weights[i] -= self.lr * dW
            self.biases[i] -= self.lr * dB