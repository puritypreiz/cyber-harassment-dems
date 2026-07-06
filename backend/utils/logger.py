import logging
import os
from logging.handlers import RotatingFileHandler

_LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def _build_logger(name: str, filename: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logs_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "..", "..", "logs")
    os.makedirs(logs_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(logs_dir, filename), maxBytes=5 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(_LOG_FORMAT))
    logger.addHandler(console_handler)

    logger.propagate = False
    return logger


def get_app_logger() -> logging.Logger:
    return _build_logger("dems.application", "application.log")


def get_security_logger() -> logging.Logger:
    return _build_logger("dems.security", "security.log", level=logging.WARNING)


def get_audit_logger() -> logging.Logger:
    return _build_logger("dems.audit", "audit.log")
