"""
Unit Tests for Quality Control Engine.
"""

from pathlib import Path
from clipper.core.rendering.qc_engine import QualityControlEngine
from clipper.core.rendering.profiles import RenderProfileRegistry
from clipper.domain.models import QCStatus


def test_qc_engine_missing_file_fails():
    profile = RenderProfileRegistry.get_profile("short_1080")
    qc_res = QualityControlEngine.evaluate_output(Path("non_existent_file.mp4"), profile)
    assert qc_res.status == QCStatus.FAILED
    assert qc_res.ffprobe_valid is False
    assert len(qc_res.errors) > 0
