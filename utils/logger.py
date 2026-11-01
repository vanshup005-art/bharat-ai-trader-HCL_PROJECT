"""
Application Logger Utility.
Provides structured, privacy-safe logging without leaking secrets or credentials.
"""
import logging
import sys

_LOGGER_NAME = "BharatAI-Trader"
_logger = logging.getLogger(_LOGGER_NAME)

if not _logger.handlers:
    _logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)
    _logger.addHandler(handler)


def get_logger() -> logging.Logger:
    """Return configured logger instance."""
    return _logger
