# loggers/logger.py
import logging
import os
from pathlib import Path

# Static defaults
DEFAULT_LOGGER_NAME = "app_logger"
DEFAULT_LOG_LEVEL = os.environ.get("LOGLEVEL", "INFO").upper()
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)


def setup_logger(
    name: str = DEFAULT_LOGGER_NAME,
    level: str = DEFAULT_LOG_LEVEL,
):
    """
    Set up a logger with console + file handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False  # Prevent duplicate logs

    # Clear old handlers if they exist
    if logger.handlers:
        logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(filename)s:%(lineno)d - [%(levelname)s] - %(message)s"
    )

    # File handler
    file_handler = logging.FileHandler(LOG_DIR / f"{name}.log")
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def get_logger(name: str = DEFAULT_LOGGER_NAME) -> logging.Logger:
    """
    Returns an existing logger or sets up a new one.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:  # If not configured yet
        setup_logger(name)
    return logger
