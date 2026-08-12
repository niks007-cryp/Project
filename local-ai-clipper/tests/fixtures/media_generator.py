"""
Synthetic Media Fixture Generator for Local AI Clipper Testing.
"""

from pathlib import Path
from clipper.infrastructure.security import SafeSubprocess
from clipper.infrastructure.ffmpeg import SafeFFmpeg


class SyntheticMediaGenerator:
    """Generates small, deterministic media files using FFmpeg for testing."""

    @classmethod
    def generate_valid_mp4(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path.resolve())
        ]
        res = SafeSubprocess.run(cmd)
        if res.returncode != 0 or not output_path.exists():
            raise RuntimeError(f"Failed to generate synthetic MP4: {res.stderr}")
        return output_path

    @classmethod
    def generate_valid_m4v(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k",
            str(output_path.resolve())
        ]
        res = SafeSubprocess.run(cmd)
        if res.returncode != 0 or not output_path.exists():
            raise RuntimeError(f"Failed to generate synthetic M4V: {res.stderr}")
        return output_path

    @classmethod
    def generate_valid_mov(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            str(output_path.resolve())
        ]
        SafeSubprocess.run(cmd)
        return output_path

    @classmethod
    def generate_valid_mkv(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-c:v", "libx264", "-c:a", "aac",
            str(output_path.resolve())
        ]
        SafeSubprocess.run(cmd)
        return output_path

    @classmethod
    def generate_valid_webm(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-c:v", "libvpx-vp9", "-c:a", "libopus",
            str(output_path.resolve())
        ]
        SafeSubprocess.run(cmd)
        return output_path

    @classmethod
    def generate_video_only(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-c:v", "libx264", "-an",
            str(output_path.resolve())
        ]
        SafeSubprocess.run(cmd)
        return output_path

    @classmethod
    def generate_corrupt_file(cls, output_path: Path) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(b"\x00\x01\x02\x03CORRUPTED_HEADER_DATA_99999")
        return output_path

    @classmethod
    def generate_rotated_video(cls, output_path: Path, duration_sec: int = 2) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            SafeFFmpeg.get_binary_path(), "-y",
            "-f", "lavfi", "-i", f"testsrc=duration={duration_sec}:size=640x360:rate=30",
            "-f", "lavfi", "-i", f"sine=frequency=440:duration={duration_sec}",
            "-metadata:s:v", "rotate=90",
            "-c:v", "libx264", "-c:a", "aac",
            str(output_path.resolve())
        ]
        SafeSubprocess.run(cmd)
        return output_path
