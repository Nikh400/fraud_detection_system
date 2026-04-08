# app/core/logger.py
from loguru import logger
import sys

LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)

# Remove default logger
logger.remove()

# Console logger (for Docker / dev)
logger.add(
    sys.stdout,
    level="INFO",
    format=LOG_FORMAT,
    enqueue=True,
    backtrace=False,
    diagnose=False,
)

# File logger (for production + audits)
logger.add(
    "logs/app.log",
    rotation="10 MB",        # Rotate at 10MB
    retention="14 days",     # Keep logs for 14 days
    compression="zip",       # Compress old logs
    level="INFO",
    format=LOG_FORMAT,
    enqueue=True,
    backtrace=True,
    diagnose=False,
)

__all__ = ["logger"]
