"""
Unit Tests for FFmpeg & FFprobe Abstraction.
"""

import pytest
from pathlib import Path
from clipper.infrastructure.ffmpeg import SafeFFprobe, SafeFFmpeg
from clipper.core.errors import CorruptMediaError, FFprobeError
from tests.fixtures.media_generator import SyntheticMediaGenerator


def test_ffprobe_valid_mp4(temp_job_dir):
    media_path = temp_job_dir / "sample.mp4"
    SyntheticMediaGenerator.generate_valid_mp4(media_path)

    probe = SafeFFprobe.probe_media(media_path)
    assert probe.container.duration_seconds > 0.0
    assert probe.video is not None
    assert probe.video.width == 640
    assert probe.video.height == 360
    assert probe.audio is not None
    assert probe.audio.sample_rate == 44100


def test_ffprobe_corrupt_media_raises(temp_job_dir):
    corrupt_path = temp_job_dir / "corrupt.mp4"
    SyntheticMediaGenerator.generate_corrupt_file(corrupt_path)

    with pytest.raises((CorruptMediaError, FFprobeError)):
        SafeFFprobe.probe_media(corrupt_path)


def test_ffmpeg_smoke_test():
    assert SafeFFmpeg.functional_smoke_test() is True
