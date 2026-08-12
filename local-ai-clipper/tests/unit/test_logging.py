"""
Unit Tests for Structured Logging & Secret Redaction.
"""

import json
import logging
from clipper.infrastructure.logger import JsonFormatter, redact_secrets, get_logger


def test_redact_secrets():
    raw_text = "Connecting with API key AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6 and token sk-1234567890abcdef1234567890abcdef"
    redacted = redact_secrets(raw_text)
    assert "AIzaSy" not in redacted
    assert "sk-" not in redacted
    assert "[REDACTED_SECRET]" in redacted


def test_json_formatter():
    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Stage completed",
        args=(),
        exc_info=None,
    )
    record.job_id = "job_123"
    record.stage = "ingestion"
    record.status = "SUCCEEDED"

    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["level"] == "INFO"
    assert data["message"] == "Stage completed"
    assert data["job_id"] == "job_123"
    assert data["stage"] == "ingestion"
    assert data["status"] == "SUCCEEDED"
