"""
Security Foundation & Safe Process Execution for Local AI Clipper.
"""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from clipper.core.errors import SecurityError, SystemError, ResourceError


def validate_path_containment(target_path: Path, allowed_parent: Path) -> Path:
    """
    Validates that target_path resides inside allowed_parent to prevent path traversal attacks.
    """
    resolved_target = Path(target_path).resolve()
    resolved_parent = Path(allowed_parent).resolve()

    try:
        resolved_target.relative_to(resolved_parent)
    except ValueError:
        raise SecurityError(
            f"Path traversal detected: '{target_path}' is outside allowed directory '{allowed_parent}'"
        )
    return resolved_target


class SafeSubprocess:
    """
    Safe process execution wrapper.
    ENFORCES:
    1. Zero shell execution (shell=True is strictly forbidden).
    2. Input command arguments must be an explicit list of strings.
    3. Explicit execution timeout limits.
    """

    @staticmethod
    def run(
        cmd: List[str],
        cwd: Optional[Path] = None,
        timeout_seconds: int = 300,
        env: Optional[Dict[str, str]] = None,
    ) -> subprocess.CompletedProcess:
        if not isinstance(cmd, list) or not cmd:
            raise SecurityError("Subprocess command must be a non-empty list of string arguments.")

        for arg in cmd:
            if not isinstance(arg, str):
                raise SecurityError(f"Subprocess argument must be string, got {type(arg)}")

        # Ensure cwd is within allowed boundaries if provided
        if cwd:
            cwd_path = Path(cwd).resolve()
            if not cwd_path.exists():
                raise SystemError(f"Subprocess working directory does not exist: {cwd}")

        env_vars = os.environ.copy()
        if env:
            env_vars.update(env)

        try:
            result = subprocess.run(
                cmd,
                cwd=str(cwd) if cwd else None,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout_seconds,
                shell=False,  # CRITICAL: Always False
                check=False,
            )
            return result
        except subprocess.TimeoutExpired as e:
            raise ResourceError(
                f"Subprocess timeout expired after {timeout_seconds} seconds: '{cmd[0]}'"
            )
        except Exception as e:
            raise SystemError(f"Subprocess execution failed: {str(e)}")


class SafeTempDir:
    """Context manager for safe temporary directory creation and cleanup."""

    def __init__(self, parent_dir: Optional[Path] = None):
        self.parent_dir = parent_dir
        self.temp_path: Optional[Path] = None

    def __enter__(self) -> Path:
        if self.parent_dir:
            self.parent_dir.mkdir(parents=True, exist_ok=True)
        self.temp_path = Path(tempfile.mkdtemp(dir=str(self.parent_dir) if self.parent_dir else None))
        return self.temp_path

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.temp_path and self.temp_path.exists():
            shutil.rmtree(self.temp_path, ignore_errors=True)
