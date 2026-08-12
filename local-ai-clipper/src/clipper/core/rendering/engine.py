"""
Hardware / Software Video Rendering Engine for Local AI Clipper.
Executes safe FFmpeg encoding commands with automatic GPU -> CPU fallback.
"""

import time
from pathlib import Path
from typing import Tuple, Optional
from clipper.core.errors import FFmpegError
from clipper.domain.models import RenderPlan, MediaAsset, RenderProfile
from clipper.infrastructure.ffmpeg import find_binary
from clipper.infrastructure.security import SafeSubprocess
from clipper.core.rendering.crop_builder import CropExpressionBuilder
from clipper.core.rendering.caption_builder import ASSFileBuilder


class RenderEngine:
    """Executes FFmpeg video rendering pipeline with GPU/CPU fallback handling."""

    @classmethod
    def render_clip(
        cls,
        plan: RenderPlan,
        media_asset: MediaAsset,
        profile: RenderProfile,
        temp_output_path: Path,
        temp_ass_path: Path,
        preferred_backend: str = "auto",
    ) -> Tuple[Path, str, Optional[str], float]:
        ffmpeg_bin = find_binary("ffmpeg.exe")
        source_path = Path(media_asset.file_path).resolve()

        # Build ASS subtitle file
        ASSFileBuilder.generate_ass_file(plan, temp_ass_path)

        # On Windows FFmpeg subtitles filter: escape backslashes as forward slashes, and colon as \:
        ass_str = str(temp_ass_path.resolve()).replace("\\", "/")
        if ":" in ass_str:
            drive, rest = ass_str.split(":", 1)
            ass_str = f"{drive}\\:{rest}"

        crop_filter = CropExpressionBuilder.build_crop_filter(
            plan.crop_keyframes,
            source_width=media_asset.video_stream.width if media_asset.video_stream else 1920,
            source_height=media_asset.video_stream.height if media_asset.video_stream else 1080,
            target_width=profile.target_width,
            target_height=profile.target_height,
        )

        filter_complex = f"{crop_filter},subtitles='{ass_str}'"

        start_sec = plan.start_ms / 1000.0
        dur_sec = plan.duration_seconds

        backend_used = "CPU"
        fallback_reason: Optional[str] = None
        t0 = time.time()

        if preferred_backend in ["gpu", "cuda"]:
            gpu_cmd = [
                str(ffmpeg_bin), "-y",
                "-ss", f"{start_sec:.3f}",
                "-i", str(source_path),
                "-t", f"{dur_sec:.3f}",
                "-vf", filter_complex,
                "-c:v", "h264_nvenc",
                "-preset", "p4",
                "-cq", str(profile.crf),
                "-pix_fmt", profile.pixel_format,
                "-c:a", profile.audio_codec,
                "-b:a", f"{profile.audio_bitrate_kbps}k",
                "-f", "mp4",
                str(temp_output_path),
            ]
            try:
                res = SafeSubprocess.run(gpu_cmd, timeout_seconds=300)
                if res.returncode == 0 and temp_output_path.exists() and temp_output_path.stat().st_size > 0:
                    render_dur = round((time.time() - t0) * 1000, 2)
                    return temp_output_path, "GPU", None, render_dur
                else:
                    fallback_reason = f"GPU encoder exited code {res.returncode}"
            except Exception as e:
                fallback_reason = f"GPU unavailable: {str(e)}"

        cpu_cmd = [
            str(ffmpeg_bin), "-y",
            "-ss", f"{start_sec:.3f}",
            "-i", str(source_path),
            "-t", f"{dur_sec:.3f}",
            "-vf", filter_complex,
            "-c:v", "libx264",
            "-preset", profile.preset,
            "-crf", str(profile.crf),
            "-pix_fmt", profile.pixel_format,
            "-c:a", profile.audio_codec,
            "-b:a", f"{profile.audio_bitrate_kbps}k",
            "-f", "mp4",
            str(temp_output_path),
        ]

        try:
            res = SafeSubprocess.run(cpu_cmd, timeout_seconds=300)
            if res.returncode != 0 or not temp_output_path.exists() or temp_output_path.stat().st_size == 0:
                err_msg = res.stderr[-500:] if res.stderr else "Unknown error"
                raise FFmpegError(f"FFmpeg rendering failed: {err_msg}")
            render_dur = round((time.time() - t0) * 1000, 2)
            return temp_output_path, "CPU", fallback_reason, render_dur
        except Exception as e:
            if isinstance(e, FFmpegError):
                raise e
            raise FFmpegError(f"CPU fallback rendering failed: {str(e)}")
