"""
Structured JSON Logger for Local AI Clipper.
"""

import json
import logging
import re
import sys
from datetime import datetime
from typing import Any, Dict, Optional


SECRET_PATTERNS = [
    re.compile(r"AIzaSy[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]+"),
]


def redact_secrets(text: str) -> str:
    """Masks secret patterns in log strings."""
    for pattern in SECRET_PATTERNS:
        text = pattern.sub("[REDACTED_SECRET]", text)
    return text


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "message": redact_secrets(record.getMessage()),
            "logger": record.name,
        }

        # Attach contextual attributes if present
        for attr in ["job_id", "pipeline_run_id", "stage", "duration_ms", "status", "error_type"]:
            if hasattr(record, attr):
                log_data[attr] = getattr(record, attr)

        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data)


class ContextLogger:
    """Logger wrapper providing contextual metadata bindings."""

    def __init__(self, logger: logging.Logger, context: Optional[Dict[str, Any]] = None):
        self._logger = logger
        self.context = context or {}

    def bind(self, **kwargs: Any) -> "ContextLogger":
        new_context = {**self.context, **kwargs}
        return ContextLogger(self._logger, new_context)

    def _log(self, level: int, msg: str, **kwargs: Any) -> None:
        extra = {**self.context, **kwargs.get("extra", {})}
        self._logger.log(level, msg, extra=extra)

    def info(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.INFO, msg, **kwargs)

    def warning(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.WARNING, msg, **kwargs)

    def error(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.ERROR, msg, **kwargs)

    def debug(self, msg: str, **kwargs: Any) -> None:
        self._log(logging.DEBUG, msg, **kwargs)


def get_logger(name: str = "clipper") -> ContextLogger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)
    return ContextLogger(logger)
