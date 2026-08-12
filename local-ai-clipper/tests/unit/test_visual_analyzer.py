"""
Unit Tests for Visual Analyzer.
"""

from clipper.core.vision.analyzer import VisualAnalyzer
from clipper.domain.models import MediaAsset


def test_visual_analyzer_bounding_box_extraction():
    asset = MediaAsset(
        asset_id="ast_test",
        file_path="dummy.mp4",
        filename="dummy.mp4",
        extension=".mp4",
        file_hash_sha256="abc12345",
        size_bytes=1000,
        duration_seconds=10.0,
    )

    boxes = VisualAnalyzer.analyze_asset(asset, sample_interval_ms=1000)
    assert len(boxes) >= 10
    assert 0 in boxes
    assert 0.0 <= boxes[0].xmin <= 1.0
    assert boxes[0].width > 0.0
