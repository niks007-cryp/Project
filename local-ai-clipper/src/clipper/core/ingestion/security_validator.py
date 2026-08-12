"""
Security Validator for Ingestion Subsystem.
"""

import os
from pathlib import Path
from typing import List, Optional
from clipper.core.errors import SecurityError, InputError, UnsupportedMediaFormatError


SUPPORTED_EXTENSIONS = {".mp4", ".mov", ".mkv", ".webm", ".m4v"}
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024 * 1024  # 50 GB default limit


class IngestionSecurityValidator:
    """Pre-probe security and path validation for media files."""

    @classmethod
    def validate_file(
        cls,
        file_path: Path,
        allowed_parent_dir: Optional[Path] = None,
        max_bytes: int = MAX_FILE_SIZE_BYTES,
    ) -> Path:
        resolved_path = Path(file_path).resolve()

        # 1. Existence Check
        if not resolved_path.exists():
            raise InputError(f"Input file does not exist: '{file_path}'")

        # 2. Regular File Check (reject directories, block devices, sockets)
        if not resolved_path.is_file():
            raise InputError(f"Input path is not a regular file: '{file_path}'")

        # 3. Path Traversal & Containment Check
        if allowed_parent_dir:
            resolved_parent = Path(allowed_parent_dir).resolve()
            try:
                resolved_path.relative_to(resolved_parent)
            except ValueError:
                raise SecurityError(
                    f"Path traversal rejected: '{file_path}' is outside allowed parent directory '{allowed_parent_dir}'"
                )

        # 4. Extension Check
        ext = resolved_path.suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            raise UnsupportedMediaFormatError(
                f"Unsupported file extension '{ext}'. Supported extensions: {sorted(list(SUPPORTED_EXTENSIONS))}"
            )

        # 5. File Size Bounds
        st = resolved_path.stat()
        if st.st_size == 0:
            raise InputError(f"Input media file is empty (0 bytes): '{file_path}'")

        if st.st_size > max_bytes:
            raise SecurityError(
                f"Input media file size ({st.st_size} bytes) exceeds maximum configured limit ({max_bytes} bytes)."
            )

        # 6. Read Permissions Check
        if not os.access(resolved_path, os.R_OK):
            raise SecurityError(f"Permission denied: File '{file_path}' is not readable.")

        return resolved_path
