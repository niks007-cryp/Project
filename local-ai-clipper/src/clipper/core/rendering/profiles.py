"""
Configurable Render Profiles Registry for Local AI Clipper.
"""

from typing import Dict
from clipper.domain.models import RenderProfile


class RenderProfileRegistry:
    """Registry of pre-configured short-form video rendering profiles."""

    PROFILES: Dict[str, RenderProfile] = {
        "short_1080": RenderProfile(
            profile_id="short_1080",
            target_width=1080,
            target_height=1920,
            fps=30.0,
            video_codec="h264",
            pixel_format="yuv420p",
            audio_codec="aac",
            audio_bitrate_kbps=192,
            crf=23,
            preset="medium",
        ),
        "short_720": RenderProfile(
            profile_id="short_720",
            target_width=720,
            target_height=1280,
            fps=30.0,
            video_codec="h264",
            pixel_format="yuv420p",
            audio_codec="aac",
            audio_bitrate_kbps=128,
            crf=25,
            preset="fast",
        ),
        "preview": RenderProfile(
            profile_id="preview",
            target_width=480,
            target_height=854,
            fps=24.0,
            video_codec="h264",
            pixel_format="yuv420p",
            audio_codec="aac",
            audio_bitrate_kbps=96,
            crf=28,
            preset="ultrafast",
        ),
    }

    @classmethod
    def get_profile(cls, profile_id: str = "short_1080") -> RenderProfile:
        pid = profile_id.lower()
        if pid not in cls.PROFILES:
            return cls.PROFILES["short_1080"]
        return cls.PROFILES[pid]
