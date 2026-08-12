"""
Toolchain Verification & Diagnostic Doctor for Local AI Clipper.
"""

import sys
import os
import shutil
import platform
import psutil
from typing import Dict, Any
from clipper.infrastructure.security import SafeSubprocess
from clipper.infrastructure.config import load_config


class SystemDoctor:
    """Runs functional smoke tests and diagnostic checks across the host toolchain."""

    @staticmethod
    def check_python() -> Dict[str, Any]:
        v = sys.version_info
        valid = (v.major == 3 and v.minor == 11)
        return {
            "name": "Python Runtime",
            "version": f"{v.major}.{v.minor}.{v.micro}",
            "executable": sys.executable,
            "passed": valid,
            "notes": "Target runtime Python 3.11 verified" if valid else "WARNING: Expected Python 3.11 runtime environment",
        }

    @staticmethod
    def check_git() -> Dict[str, Any]:
        git_path = shutil.which("git")
        if not git_path:
            return {"name": "Git VCS", "passed": False, "notes": "git command not found on PATH"}
        res = SafeSubprocess.run(["git", "--version"])
        return {
            "name": "Git VCS",
            "version": res.stdout.strip(),
            "passed": res.returncode == 0,
        }

    @staticmethod
    def check_node() -> Dict[str, Any]:
        node_path = shutil.which("node")
        if not node_path:
            return {"name": "Node.js", "passed": False, "notes": "node command not found on PATH"}
        res = SafeSubprocess.run(["node", "-v"])
        return {
            "name": "Node.js",
            "version": res.stdout.strip(),
            "passed": res.returncode == 0,
        }

    @staticmethod
    def check_docker() -> Dict[str, Any]:
        docker_path = shutil.which("docker")
        if not docker_path:
            return {"name": "Docker", "passed": False, "notes": "docker command not found on PATH"}
        res = SafeSubprocess.run(["docker", "--version"])
        return {
            "name": "Docker",
            "version": res.stdout.strip(),
            "passed": res.returncode == 0,
        }

    @staticmethod
    def check_ffmpeg() -> Dict[str, Any]:
        config = load_config()
        bin_ffmpeg = config.workspace_dir / ".bin" / ("ffmpeg.exe" if sys.platform == "win32" else "ffmpeg")
        ffmpeg_cmd = str(bin_ffmpeg) if bin_ffmpeg.exists() else shutil.which("ffmpeg")
        if not ffmpeg_cmd:
            return {
                "name": "FFmpeg Media Engine",
                "passed": False,
                "notes": "ffmpeg command not found on PATH or .bin directory. Required for Floor 2 media processing.",
            }
        res = SafeSubprocess.run([ffmpeg_cmd, "-version"])
        first_line = res.stdout.splitlines()[0] if res.stdout else "Unknown"
        return {
            "name": "FFmpeg Media Engine",
            "version": first_line,
            "passed": res.returncode == 0,
        }

    @staticmethod
    def check_hardware() -> Dict[str, Any]:
        ram = psutil.virtual_memory()
        config = load_config()
        
        # Check disk space on workspace drive
        target_drive = config.workspace_dir.anchor or "C:\\"
        disk = psutil.disk_usage(target_drive)
        free_gb = round(disk.free / (1024**3), 2)
        
        passed = free_gb >= config.min_free_disk_gb

        return {
            "name": "Hardware Resources",
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_total_gb": round(ram.total / (1024**3), 2),
            "ram_available_gb": round(ram.available / (1024**3), 2),
            "disk_free_gb": free_gb,
            "passed": passed,
            "notes": f"Disk space free: {free_gb} GB (Required >= {config.min_free_disk_gb} GB)",
        }

    @classmethod
    def run_all_checks(cls) -> Dict[str, Dict[str, Any]]:
        return {
            "python": cls.check_python(),
            "git": cls.check_git(),
            "node": cls.check_node(),
            "docker": cls.check_docker(),
            "ffmpeg": cls.check_ffmpeg(),
            "hardware": cls.check_hardware(),
        }
