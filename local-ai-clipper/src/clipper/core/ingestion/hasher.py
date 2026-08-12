"""
Media Hasher for Ingestion Subsystem.
"""

import hashlib
from pathlib import Path


class MediaHasher:
    """Calculates SHA-256 content hashes of media files."""

    @staticmethod
    def calculate_sha256(file_path: Path, chunk_size_bytes: int = 65536) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            while chunk := f.read(chunk_size_bytes):
                sha256.update(chunk)
        return sha256.hexdigest()
