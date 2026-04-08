import pandas as pd
import numpy as np
import random
from app.services.fraud_service import FraudService

def get_random_training_data(num_samples=5000):
    categories = ["groceries", "electronics", "health", "shopping", "travel", "entertainment", "dining", "other"]
    locations = ["NY", "CA", "TX", "Mumbai, MH", "Delhi", "Unknown"]
    
    data = []
    descriptions = []
    labels = []
    
    for _ in range(num_samples):
        # 80% normal, 20% fraud simulation
        is_fraud = random.random() < 0.2
        
        if is_fraud:
            # Fraud profile: high amount, weird hours, unknown device, high velocity, random category
            amount = random.uniform(500, 25000)
            age = random.choice([random.randint(18, 25), random.randint(65, 85)])
            hour = random.choice([1, 2, 3, 4, 5, 23])
            category = random.choice(categories)
            location = random.choice(locations)
            desc = random.choice(["URGENT TRANSFER", "Crypto", "Test", "Help", "Unknown charge"])
            
            # New stateful metrics dictating fraud
            is_known_device = random.choice([0, 0, 0, 1]) # Highly likely to be unknown
            device_age_days = random.randint(0, 2)
            device_velocity_30d = random.randint(5, 50)
            
            labels.append(1)
        else:
            # Normal profile
            amount = random.uniform(5, 300)
            age = random.randint(25, 60)
            hour = random.randint(8, 21)
            category = random.choice(["groceries", "dining", "travel"])
            location = random.choice(["NY", "Mumbai, MH"])
            desc = random.choice(["Weekly groceries", "Coffee", "Transport", "Subscription", "Bill", ""])
            
            # New stateful metrics dictating trust
            is_known_device = random.choice([1, 1, 1, 0]) # Usually known
            device_age_days = random.randint(30, 800)
            device_velocity_30d = random.randint(1, 3)
            
            labels.append(0)

        data.append({
            "amount": amount,
            "age": age,
            "hour": hour,
            "category": category,
            "location": location,
            "is_known_device": is_known_device,
            "device_age_days": device_age_days,
            "device_velocity_30d": device_velocity_30d
        })
        descriptions.append(desc)
        
    return pd.DataFrame(data), descriptions, labels

if __name__ == "__main__":
    df, desc, labels = get_random_training_data(7000)
    service = FraudService()
    service.train(df, desc, labels, epochs=50) # Train specific to new input dimensions
    service.save_model("ml/saved_models/fraud_model.npz")
    print("Model successfully retrained and persisted!")
