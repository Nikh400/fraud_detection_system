"""
Input validation utilities for Fraud Detection System
"""

import re
from typing import Any


# =========================================================
# Numeric Validators
# =========================================================

def validate_amount(amount: float) -> float:
    """Ensure transaction amount is valid."""
    if amount <= 0:
        raise ValueError("Amount must be positive")
    if amount > 10_000_000:  # safety cap
        raise ValueError("Amount exceeds allowed limit")
    return amount


def validate_age(age: int) -> int:
    """Validate user age."""
    if age < 0 or age > 120:
        raise ValueError("Invalid age")
    return age


def validate_hour(hour: int) -> int:
    """Validate transaction hour (0–23)."""
    if hour < 0 or hour > 23:
        raise ValueError("Hour must be between 0 and 23")
    return hour


# =========================================================
# String Validators
# =========================================================

def validate_non_empty(value: str, field_name: str) -> str:
    """Ensure string field is not empty."""
    if not value or not value.strip():
        raise ValueError(f"{field_name} cannot be empty")
    return value.strip()


def validate_category(category: str) -> str:
    """Validate transaction category."""
    category = validate_non_empty(category, "category")

    allowed = {
        "electronics",
        "grocery",
        "fashion",
        "travel",
        "entertainment",
        "food",
        "utility",
        "other",
    }

    if category.lower() not in allowed:
        raise ValueError("Invalid transaction category")

    return category.lower()


def validate_device(device: str) -> str:
    """Validate device type."""
    device = validate_non_empty(device, "device")

    allowed = {"mobile", "desktop", "tablet", "atm", "pos"}

    if device.lower() not in allowed:
        raise ValueError("Invalid device type")

    return device.lower()


def validate_location(location: str) -> str:
    """Validate location string."""
    location = validate_non_empty(location, "location")

    if len(location) > 100:
        raise ValueError("Location too long")

    return location


# =========================================================
# Text Validators
# =========================================================

def validate_description(description: str) -> str:
    """Clean and validate description text."""
    if description is None:
        return ""

    description = description.strip()

    if len(description) > 500:
        raise ValueError("Description too long")

    return description


# =========================================================
# Email Validator
# =========================================================

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


def validate_email(email: str) -> str:
    """Validate email format."""
    if not EMAIL_REGEX.match(email):
        raise ValueError("Invalid email address")
    return email.lower()


# =========================================================
# Generic Safety Checks
# =========================================================

def ensure_type(value: Any, expected_type: type, field_name: str):
    """Ensure value is of expected type."""
    if not isinstance(value, expected_type):
        raise TypeError(f"{field_name} must be {expected_type.__name__}")
    return value