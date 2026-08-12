"""
Atomic Job Manifest Manager for Local AI Clipper.
"""

import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from clipper.core.errors import ManifestCorruptionError, SystemError
from clipper.core.state import JobState, JobStateMachine
from clipper.domain.models import JobManifest, StageStatus


def calculate_file_hash(file_path: Path, chunk_size: int = 65536) -> str:
    """Calculates SHA256 hash of a file on disk."""
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()


def calculate_json_checksum(data: Dict[str, Any]) -> str:
    """Calculates SHA256 checksum of dict data excluding existing checksum field."""
    clean_data = {k: v for k, v in data.items() if k != "checksum_sha256"}
    serialized = json.dumps(clean_data, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


class ManifestManager:
    """Manages atomic reads, writes, and integrity validation for job manifests."""

    def __init__(self, job_dir: Path):
        self.job_dir = Path(job_dir)
        self.manifest_path = self.job_dir / "job_manifest.json"
        self.backup_path = self.job_dir / "job_manifest.json.bak"

    def save(self, manifest: JobManifest) -> None:
        """
        Atomically saves a JobManifest to disk.
        """
        self.job_dir.mkdir(parents=True, exist_ok=True)
        manifest.updated_at = datetime.utcnow()

        manifest_dict = manifest.model_dump(mode="json")
        checksum = calculate_json_checksum(manifest_dict)
        manifest.checksum_sha256 = checksum
        manifest_dict["checksum_sha256"] = checksum

        tmp_path = self.job_dir / "job_manifest.json.tmp"
        
        try:
            with open(tmp_path, "w", encoding="utf-8") as f:
                json.dump(manifest_dict, f, indent=2, default=str)
                f.flush()
                os.fsync(f.fileno())

            if self.manifest_path.exists():
                shutil_copy = self.backup_path
                with open(self.manifest_path, "rb") as src, open(shutil_copy, "wb") as dst:
                    dst.write(src.read())

            os.replace(tmp_path, self.manifest_path)
        except Exception as e:
            if tmp_path.exists():
                try:
                    os.remove(tmp_path)
                except OSError:
                    pass
            raise SystemError(f"Failed to atomically write manifest: {str(e)}")

    def load(self) -> JobManifest:
        if not self.manifest_path.exists():
            if self.backup_path.exists():
                return self._load_from_file(self.backup_path)
            raise ManifestCorruptionError(f"Job manifest not found: {self.manifest_path}")

        try:
            return self._load_from_file(self.manifest_path)
        except ManifestCorruptionError as e:
            if self.backup_path.exists():
                try:
                    recovered = self._load_from_file(self.backup_path)
                    self.save(recovered)
                    return recovered
                except Exception:
                    pass
            raise e

    def _load_from_file(self, file_path: Path) -> JobManifest:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            raise ManifestCorruptionError(f"Manifest JSON syntax invalid in '{file_path}': {str(e)}")

        expected_checksum = data.get("checksum_sha256")
        if expected_checksum:
            actual_checksum = calculate_json_checksum(data)
            if actual_checksum != expected_checksum:
                raise ManifestCorruptionError(
                    f"Manifest checksum mismatch in '{file_path}'. "
                    f"Expected: {expected_checksum}, Actual: {actual_checksum}"
                )

        try:
            manifest = JobManifest.model_validate(data)
            return manifest
        except Exception as e:
            raise ManifestCorruptionError(f"Manifest schema validation failed: {str(e)}")
