"""
Unit Tests for Manifest Atomicity & Corruption Recovery.
"""

import json
import pytest
from clipper.core.manifest import ManifestManager, calculate_json_checksum
from clipper.core.errors import ManifestCorruptionError
from clipper.domain.models import JobManifest
from clipper.core.state import JobState


def test_atomic_manifest_save_and_load(temp_job_dir):
    manager = ManifestManager(temp_job_dir)
    manifest = JobManifest(job_id="job_001", status=JobState.QUEUED)
    
    manager.save(manifest)
    assert manager.manifest_path.exists()

    loaded = manager.load()
    assert loaded.job_id == "job_001"
    assert loaded.status == JobState.QUEUED
    assert loaded.checksum_sha256 is not None


def test_manifest_checksum_tamper_detection(temp_job_dir):
    manager = ManifestManager(temp_job_dir)
    manifest = JobManifest(job_id="job_002", status=JobState.QUEUED)
    manager.save(manifest)

    # Tamper with the file contents manually
    with open(manager.manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["status"] = "SUCCEEDED"  # Unauthorized modification
    with open(manager.manifest_path, "w", encoding="utf-8") as f:
        json.dump(data, f)

    # Load should fail due to checksum mismatch
    with pytest.raises(ManifestCorruptionError):
        manager.load()


def test_manifest_backup_recovery(temp_job_dir):
    manager = ManifestManager(temp_job_dir)
    manifest = JobManifest(job_id="job_003", status=JobState.QUEUED)
    manager.save(manifest)

    # Update manifest to create backup
    manifest.status = JobState.RUNNING
    manager.save(manifest)

    assert manager.backup_path.exists()

    # Corrupt main manifest file
    with open(manager.manifest_path, "w", encoding="utf-8") as f:
        f.write("{ INVALID JSON payload ...")

    # Load should automatically recover from backup file
    recovered = manager.load()
    assert recovered.job_id == "job_003"
