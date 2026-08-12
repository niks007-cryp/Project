"""
Pytest Fixtures for Local AI Clipper.
"""

import tempfile
import pytest
from pathlib import Path
from clipper.core.manifest import ManifestManager
from clipper.domain.models import JobManifest
from clipper.infrastructure.logger import get_logger, ContextLogger


@pytest.fixture
def temp_job_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        job_dir = Path(tmpdir) / "jobs" / "job_test_001"
        job_dir.mkdir(parents=True, exist_ok=True)
        yield job_dir


@pytest.fixture
def manifest_manager(temp_job_dir):
    manager = ManifestManager(temp_job_dir)
    manifest = JobManifest(job_id="job_test_001", project_id="test_project")
    manager.save(manifest)
    return manager


@pytest.fixture
def logger():
    return get_logger("test_clipper")
