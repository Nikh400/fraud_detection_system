#!/bin/bash
export PYTHONPATH=".:/home/nikhil/fraud_detector/fraud_detection"
source venv/bin/activate
cd fraud_detection
uvicorn app.main:app --reload
