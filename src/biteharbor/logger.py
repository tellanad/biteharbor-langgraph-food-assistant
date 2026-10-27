"""Centralized logging configuration for the application."""

import logging
import sys


def setup_logger(name: str, level=logging.INFO) -> logging.Logger:
    """Create or retrun a configured logger with clean formatting."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(level)
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
