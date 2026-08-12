"""
Unit Tests for Ingestion Security Validation.
"""

import os
import pytest
from pathlib import Path
from clipper.core.ingestion.security_validator import IngestionSecurityValidator
from clipper.core.errors import SecurityError, InputError, UnsupportedMediaFormatError


def test_missing_file_raises_input_error(temp_job_dir):
    missing_path = temp_job_dir / "non_existent_video.mp4"
    with pytest.raises(InputError):
        IngestionSecurityValidator.validate_file(missing_path)


def test_directory_input_raises_input_error(temp_job_dir):
    with pytest.raises(InputError):
        IngestionSecurityValidator.validate_file(temp_job_dir)


def test_unsupported_extension_raises_error(temp_job_dir):
    unsupported_file = temp_job_dir / "document.pdf"
    unsupported_file.write_text("dummy content")
    with pytest.raises(UnsupportedMediaFormatError):
        IngestionSecurityValidator.validate_file(unsupported_file)


def test_empty_file_raises_input_error(temp_job_dir):
    empty_file = temp_job_dir / "empty.mp4"
    empty_file.write_bytes(b"")
    with pytest.raises(InputError):
        IngestionSecurityValidator.validate_file(empty_file)


def test_file_size_exceeds_max_limit(temp_job_dir):
    large_file = temp_job_dir / "large.mp4"
    large_file.write_bytes(b"1234567890")
    with pytest.raises(SecurityError):
        # Set max_bytes to 5 bytes
        IngestionSecurityValidator.validate_file(large_file, max_bytes=5)


def test_path_traversal_rejection(temp_job_dir):
    sub_dir = temp_job_dir / "sub"
    sub_dir.mkdir()
    file_outside = temp_job_dir / "outside.mp4"
    file_outside.write_bytes(b"12345")

    with pytest.raises(SecurityError):
        IngestionSecurityValidator.validate_file(file_outside, allowed_parent_dir=sub_dir)
