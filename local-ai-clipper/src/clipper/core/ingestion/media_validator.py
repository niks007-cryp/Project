"""
Media Validator for Ingestion Subsystem.
"""

from typing import Tuple
from clipper.core.errors import (
    UnsupportedMediaFormatError,
    CorruptMediaError,
    ValidationError,
)
from clipper.domain.models import MediaProbeInfo, MediaAsset


class MediaValidator:
    """Evaluates probed media stream metadata against domain rules."""

    @classmethod
    def validate_probe_info(
        cls, probe: MediaProbeInfo, require_audio: bool = False
    ) -> Tuple[str, bool, bool]:
        """
        Validates container and streams.
        Returns Tuple: (validation_status_str, has_video, has_audio)
        """
        container = probe.container
        video = probe.video
        audio = probe.audio

        # Check duration
        if container.duration_seconds <= 0.0:
            raise CorruptMediaError(f"Invalid media duration: {container.duration_seconds} seconds.")

        # Check video stream
        has_video = video is not None and video.width > 0 and video.height > 0
        if not has_video:
            raise CorruptMediaError("Input file contains no valid video stream.")

        if video.fps <= 0.0:
            raise CorruptMediaError(f"Invalid video FPS: {video.fps}")

        has_audio = audio is not None and audio.sample_rate > 0 and audio.channels > 0
        if require_audio and not has_audio:
            raise ValidationError("Input video file lacks required audio stream for transcription.")

        return "SUPPORTED_VALID", has_video, has_audio
