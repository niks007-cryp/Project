"""
Unit Tests for YouTube URL Validation & Safe Ingestion Engine.
"""

import pytest
from clipper.core.errors import ValidationError, SecurityError
from clipper.core.ingestion.youtube import (
    validate_youtube_url,
    extract_youtube_video_id,
    verify_ytdlp_version,
)


def test_validate_youtube_url_valid():
    valid_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "https://www.youtube.com/shorts/dQw4w9WgXcQ",
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
    ]
    for url in valid_urls:
        validated = validate_youtube_url(url)
        assert "https://www.youtube.com/watch?v=dQw4w9WgXcQ" in validated
        assert extract_youtube_video_id(url) == "dQw4w9WgXcQ"


def test_validate_youtube_url_ssrf_rejection():
    invalid_urls = [
        "http://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Non-HTTPS
        "https://localhost/watch?v=dQw4w9WgXcQ",  # Localhost
        "https://127.0.0.1/watch?v=dQw4w9WgXcQ",  # Loopback IP
        "https://192.168.1.1/watch?v=dQw4w9WgXcQ",  # Private subnet
        "https://10.0.0.1/watch?v=dQw4w9WgXcQ",  # Private subnet
        "https://vimeo.com/12345",  # Unsupported host
        "https://evil-site.com/watch?v=dQw4w9WgXcQ",  # Unsupported host
    ]
    for url in invalid_urls:
        with pytest.raises((ValidationError, SecurityError)):
            validate_youtube_url(url)


def test_verify_ytdlp_version():
    version_str = verify_ytdlp_version()
    assert version_str is not None
    year = int(version_str.split(".")[0])
    assert year >= 2024
