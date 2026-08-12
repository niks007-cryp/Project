"""
Deterministic Quality Control (QC) Engine for Local AI Clipper.
Inspects rendered video artifacts for visual, audio, and A/V sync integrity.
"""

from pathlib import Path
from clipper.infrastructure.ffmpeg import SafeFFprobe
from clipper.domain.models import QCResult, QCStatus, RenderProfile


class QualityControlEngine:
    """Executes post-render deterministic quality control checks."""

    @classmethod
    def evaluate_output(cls, rendered_path: Path, profile: RenderProfile) -> QCResult:
        file_path = Path(rendered_path).resolve()
        if not file_path.exists() or file_path.stat().st_size == 0:
            return QCResult(
                status=QCStatus.FAILED,
                ffprobe_valid=False,
                video_stream_valid=False,
                audio_stream_valid=False,
                errors=["Rendered output file is missing or zero bytes."],
            )

        try:
            probe_info = SafeFFprobe.probe_media(file_path)
        except Exception as e:
            return QCResult(
                status=QCStatus.FAILED,
                ffprobe_valid=False,
                video_stream_valid=False,
                audio_stream_valid=False,
                errors=[f"FFprobe inspection failed: {str(e)}"],
            )

        errors = []
        warnings = []

        # 1. Video Stream QC
        if not probe_info.video:
            errors.append("Rendered asset is missing video stream.")
        else:
            if probe_info.video.width != profile.target_width or probe_info.video.height != profile.target_height:
                errors.append(
                    f"Resolution mismatch: Expected {profile.target_width}x{profile.target_height}, got {probe_info.video.width}x{probe_info.video.height}."
                )

        # 2. Audio Stream & Sync QC
        audio_dur = 0.0
        video_dur = probe_info.container.duration_seconds
        drift_sec = 0.0

        if probe_info.audio:
            audio_dur = probe_info.audio.duration_seconds or video_dur
            drift_sec = round(abs(video_dur - audio_dur), 3)
            if drift_sec > 0.20:
                warnings.append(f"A/V sync drift ({drift_sec}s) exceeds optimal tolerance (0.20s).")

        status = QCStatus.FAILED if errors else (QCStatus.WARNING if warnings else QCStatus.PASSED)

        return QCResult(
            status=status,
            ffprobe_valid=True,
            video_stream_valid=probe_info.video is not None,
            audio_stream_valid=probe_info.audio is not None,
            av_sync_drift_seconds=drift_sec,
            errors=errors,
            warnings=warnings,
        )
