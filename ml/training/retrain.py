import sys
import os
sys.path.append("../../")
import pandas as pd
from app.services.fraud_service import FraudService

def retrain_model():
    print("Initializing Fraud Service for Retraining...")
    service = FraudService()

    # Generate realistic dummy training data that matches our API schema
    data = []
    descriptions = []
    labels = []

    # Safe Transactions
    for _ in range(500):
        hour = int(np.random.uniform(8, 20))
        desc = "Standard grocery shopping"
        data.append({
            "amount": float(np.random.uniform(5, 50)),
            "age": int(np.random.uniform(18, 60)),
            "hour": hour,
            "is_night": 0,
            "category": "groceries",
            "device": "desktop",
            "location": "NY",
            "description": desc,
            "description_length": len(desc)
        })
        descriptions.append(desc)
        labels.append(0)  # Safe

    # Fraudulent Transactions
    for _ in range(500):
        hour = int(np.random.randint(0, 5))
        desc = "Suspicious bulk transfer wire payment"
        data.append({
            "amount": float(np.random.uniform(1000, 5000)),
            "age": int(np.random.uniform(18, 30)),
            "hour": hour,
            "is_night": 1,
            "category": "electronics",
            "device": "mobile",
            "location": "Overseas",
            "description": desc,
            "description_length": len(desc)
        })
        descriptions.append(desc)
        labels.append(1)  # Fraud
        
    df = pd.DataFrame(data)

    print("Training the neural network...")
    service.train(df, descriptions, labels, epochs=80)

    print("Saving the updated model weights...")
    os.makedirs("../saved_models", exist_ok=True)
    service.save_model("../saved_models/fraud_model.npz")
    print("Training Complete! New Model Saved.")

if __name__ == "__main__":
    import numpy as np
    retrain_model()
