"""
Media Normalizer for Ingestion Subsystem.
"""

from pathlib import Path
from typing import Optional, Tuple
from clipper.domain.models import MediaProbeInfo, NormalizationDecision
from clipper.infrastructure.ffmpeg import SafeFFmpeg


class MediaNormalizer:
    """Evaluates normalization decisions and manages derived asset creation."""

    @classmethod
    def evaluate_normalization(cls, probe: MediaProbeInfo) -> NormalizationDecision:
        reasons = []
        video = probe.video
        container = probe.container

        if video:
            # Check rotation/orientation
            if video.rotation != 0:
                reasons.append(f"Video stream has non-zero rotation metadata ({video.rotation} deg)")
            
            # Check pixel format
            if video.pixel_format not in ["yuv420p", "yuvj420p"]:
                reasons.append(f"Non-standard pixel format '{video.pixel_format}' (target: yuv420p)")

            # Check container
            if "mp4" not in container.format_name.lower():
                reasons.append(f"Non-standard container format '{container.format_name}' (target: mp4)")

        needs_norm = len(reasons) > 0
        return NormalizationDecision(
            needs_normalization=needs_norm,
            reasons=reasons,
        )

    @classmethod
    def normalize_if_needed(
        cls,
        source_path: Path,
        output_dir: Path,
        probe: MediaProbeInfo,
        file_hash: str,
    ) -> Tuple[NormalizationDecision, Optional[Path]]:
        decision = cls.evaluate_normalization(probe)
        if not decision.needs_normalization:
            return decision, None

        normalized_output_path = output_dir / f"norm_{file_hash[:12]}.mp4"
        if normalized_output_path.exists() and normalized_output_path.stat().st_size > 0:
            # Idempotent skip
            return decision, normalized_output_path

        SafeFFmpeg.normalize_media(source_path, normalized_output_path)
        return decision, normalized_output_path
