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


def test_youtube_50gb_size_policy():
    from clipper.core.ingestion.youtube import download_youtube_video
    import inspect
    sig = inspect.signature(download_youtube_video)
    default_max = sig.parameters["max_size_bytes"].default
    assert default_max == 50 * 1024 * 1024 * 1024  # 50 GB limit


def test_youtube_disk_preflight_check(tmp_path, monkeypatch):
    from clipper.core.ingestion.youtube import download_youtube_video
    from clipper.core.errors import ResourceError
    import psutil

    class FakeDisk:
        free = 1.0 * (1024**3)  # Only 1 GB free space

    monkeypatch.setattr(psutil, "disk_usage", lambda path: FakeDisk())

    with pytest.raises(ResourceError) as exc_info:
        download_youtube_video("https://www.youtube.com/watch?v=dQw4w9WgXcQ", output_dir=tmp_path)
    assert "Insufficient disk space" in str(exc_info.value)
