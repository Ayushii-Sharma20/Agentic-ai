# backend/app/utils/logger.py
import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Create a configured logger with consistent formatting.

    Args:
        name: Logger name (usually __name__)
        level: Override log level (DEBUG, INFO, WARNING, ERROR)
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    log_level = getattr(logging, (level or 'INFO').upper(), logging.INFO)
    logger.setLevel(log_level)

    return logger


def log_pipeline_step(logger: logging.Logger, step: str, agent: str, duration: float, success: bool):
    """Structured log entry for pipeline step."""
    status = '✓' if success else '✗'
    logger.info(f"{status} Step '{step}' | Agent: {agent} | Duration: {duration:.2f}s")