"""
Unit Tests for Media Validator & Audio Policy.
"""

import pytest
from clipper.core.ingestion.media_validator import MediaValidator
from clipper.core.errors import CorruptMediaError, ValidationError, UnsupportedMediaFormatError
from clipper.domain.models import (
    MediaProbeInfo,
    MediaContainerInfo,
    VideoStreamInfo,
    AudioStreamInfo,
)


def test_media_validator_valid_stream():
    probe = MediaProbeInfo(
        container=MediaContainerInfo(format_name="mp4", duration_seconds=10.0, size_bytes=10000),
        video=VideoStreamInfo(codec="h264", width=1920, height=1080, fps=30.0),
        audio=AudioStreamInfo(codec="aac", sample_rate=44100, channels=2),
    )
    status, has_video, has_audio = MediaValidator.validate_probe_info(probe)
    assert status == "SUPPORTED_VALID"
    assert has_video is True
    assert has_audio is True


def test_media_validator_no_video_raises():
    probe = MediaProbeInfo(
        container=MediaContainerInfo(format_name="mp4", duration_seconds=10.0, size_bytes=10000),
        video=None,
        audio=AudioStreamInfo(codec="aac", sample_rate=44100, channels=2),
    )
    with pytest.raises(CorruptMediaError):
        MediaValidator.validate_probe_info(probe)


def test_zero_duration_rejection():
    probe = MediaProbeInfo(
        container=MediaContainerInfo(format_name="mp4", duration_seconds=0.0, size_bytes=10000),
        video=VideoStreamInfo(codec="h264", width=1920, height=1080, fps=30.0),
        audio=AudioStreamInfo(codec="aac", sample_rate=44100, channels=2),
    )
    with pytest.raises(CorruptMediaError):
        MediaValidator.validate_probe_info(probe)


def test_media_validator_audio_required_flag():
    probe = MediaProbeInfo(
        container=MediaContainerInfo(format_name="mp4", duration_seconds=10.0, size_bytes=10000),
        video=VideoStreamInfo(codec="h264", width=1920, height=1080, fps=30.0),
        audio=None,
    )
    # Without audio requirement -> Valid
    status, has_vid, has_aud = MediaValidator.validate_probe_info(probe, require_audio=False)
    assert has_aud is False

    # With audio requirement -> Raises ValidationError
    with pytest.raises(ValidationError):
        MediaValidator.validate_probe_info(probe, require_audio=True)
