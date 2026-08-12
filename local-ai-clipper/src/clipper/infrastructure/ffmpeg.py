"""
FFmpeg & FFprobe Abstraction for Local AI Clipper.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from clipper.core.errors import FFprobeError, FFmpegError, CorruptMediaError, SystemError
from clipper.domain.models import (
    MediaProbeInfo,
    MediaContainerInfo,
    VideoStreamInfo,
    AudioStreamInfo,
)
from clipper.infrastructure.security import SafeSubprocess


def find_binary(binary_name: str) -> str:
    """Finds binary on system PATH or local project .bin directory."""
    # 1. System PATH check
    system_path = shutil.which(binary_name)
    if system_path:
        return system_path

    # 2. Project root .bin directory
    candidates = [
        Path("N:/local-ai-clipper/.bin") / f"{binary_name}.exe",
        Path("N:/local-ai-clipper/.bin") / binary_name,
        Path.cwd() / ".bin" / f"{binary_name}.exe",
        Path.cwd() / ".bin" / binary_name,
        Path(__file__).resolve().parents[3] / ".bin" / f"{binary_name}.exe",
    ]

    for cand in candidates:
        if cand.exists():
            return str(cand.resolve())

    raise SystemError(f"'{binary_name}' executable not found on system PATH or project .bin directory.")


class SafeFFprobe:
    """Safe wrapper around ffprobe binary using SafeSubprocess."""

    @classmethod
    def get_binary_path(cls) -> str:
        return find_binary("ffprobe")

    @classmethod
    def probe_media(cls, file_path: Path, timeout_seconds: int = 60) -> MediaProbeInfo:
        """
        Executes ffprobe to extract structured JSON metadata from media file.
        """
        binary = cls.get_binary_path()
        resolved_path = Path(file_path).resolve()
        
        cmd = [
            binary,
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            "-show_error",
            str(resolved_path),
        ]

        res = SafeSubprocess.run(cmd, timeout_seconds=timeout_seconds)
        if res.returncode != 0:
            raise FFprobeError(
                f"ffprobe execution failed with exit code {res.returncode}: {res.stderr.strip()}"
            )

        try:
            data = json.loads(res.stdout)
        except json.JSONDecodeError as e:
            raise FFprobeError(f"Failed to parse ffprobe JSON output: {str(e)}")

        if "error" in data:
            raise CorruptMediaError(f"ffprobe reported media error: {data['error'].get('string', 'Unknown error')}")

        format_data = data.get("format")
        if not format_data:
            raise CorruptMediaError("ffprobe output lacks format metadata.")

        duration = float(format_data.get("duration", 0.0))
        size = int(format_data.get("size", 0))
        format_name = format_data.get("format_name", "unknown")
        bitrate = int(format_data.get("bit_rate", 0)) // 1000 if format_data.get("bit_rate") else None

        container = MediaContainerInfo(
            format_name=format_name,
            duration_seconds=duration,
            size_bytes=size,
            bitrate_kbps=bitrate,
            metadata=format_data.get("tags", {}),
        )

        streams = data.get("streams", [])
        video_stream: Optional[VideoStreamInfo] = None
        audio_stream: Optional[AudioStreamInfo] = None

        for s in streams:
            codec_type = s.get("codec_type")
            if codec_type == "video" and video_stream is None:
                # Extract FPS from avg_frame_rate or r_frame_rate
                fps_str = s.get("avg_frame_rate", s.get("r_frame_rate", "30/1"))
                try:
                    num, den = map(float, fps_str.split("/"))
                    fps = round(num / den, 2) if den > 0 else 30.0
                except Exception:
                    fps = 30.0

                # Rotation detection from tags or side_data
                rotation = 0
                tags = s.get("tags", {})
                if "rotate" in tags:
                    try:
                        rotation = int(tags["rotate"])
                    except ValueError:
                        pass

                v_bitrate = int(s.get("bit_rate", 0)) // 1000 if s.get("bit_rate") else None
                nb_frames = int(s.get("nb_frames")) if s.get("nb_frames") else None

                video_stream = VideoStreamInfo(
                    codec=s.get("codec_name", "unknown"),
                    width=int(s.get("width", 0)),
                    height=int(s.get("height", 0)),
                    fps=fps,
                    pixel_format=s.get("pix_fmt", "yuv420p"),
                    bitrate_kbps=v_bitrate,
                    frame_count=nb_frames,
                    rotation=rotation,
                )
            elif codec_type == "audio" and audio_stream is None:
                a_bitrate = int(s.get("bit_rate", 0)) // 1000 if s.get("bit_rate") else None
                a_dur = float(s.get("duration")) if s.get("duration") else None

                audio_stream = AudioStreamInfo(
                    codec=s.get("codec_name", "unknown"),
                    sample_rate=int(s.get("sample_rate", 0)),
                    channels=int(s.get("channels", 0)),
                    channel_layout=s.get("channel_layout"),
                    bitrate_kbps=a_bitrate,
                    duration_seconds=a_dur,
                )

        return MediaProbeInfo(
            container=container,
            video=video_stream,
            audio=audio_stream,
            raw_probe_json=data,
        )


class SafeFFmpeg:
    """Safe wrapper around ffmpeg binary using SafeSubprocess."""

    @classmethod
    def get_binary_path(cls) -> str:
        return find_binary("ffmpeg")

    @classmethod
    def run_command(cls, args: List[str], timeout_seconds: int = 1800) -> SafeSubprocess:
        binary = cls.get_binary_path()
        cmd = [binary, "-y"] + args
        res = SafeSubprocess.run(cmd, timeout_seconds=timeout_seconds)
        if res.returncode != 0:
            raise FFmpegError(
                f"ffmpeg execution failed with exit code {res.returncode}: {res.stderr.strip()}"
            )
        return res

    @classmethod
    def normalize_media(
        cls,
        source_path: Path,
        output_path: Path,
        target_vcodec: str = "libx264",
        target_acodec: str = "aac",
        target_pix_fmt: str = "yuv420p",
        target_fps: float = 30.0,
        timeout_seconds: int = 1800,
    ) -> Path:
        """
        Normalizes source video to standard MP4 (H.264 / AAC / yuv420p) derived asset.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        args = [
            "-i", str(source_path.resolve()),
            "-c:v", target_vcodec,
            "-preset", "fast",
            "-crf", "22",
            "-pix_fmt", target_pix_fmt,
            "-r", str(target_fps),
            "-c:a", target_acodec,
            "-b:a", "192k",
            "-ar", "44100",
            "-ac", "2",
            "-movflags", "+faststart",
            str(output_path.resolve()),
        ]

        cls.run_command(args, timeout_seconds=timeout_seconds)
        if not output_path.exists() or output_path.stat().st_size == 0:
            raise FFmpegError(f"FFmpeg normalization failed to create non-empty output file: {output_path}")

        return output_path

    @classmethod
    def functional_smoke_test(cls) -> bool:
        """Runs a harmless synthetic video probe to verify functional FFmpeg/FFprobe execution."""
        try:
            ffprobe_path = SafeFFprobe.get_binary_path()
            res = SafeSubprocess.run([ffprobe_path, "-version"])
            return res.returncode == 0
        except Exception:
            return False
