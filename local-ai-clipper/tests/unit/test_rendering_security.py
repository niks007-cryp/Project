"""
Security & Injection Defense Unit Tests for Floor 6 Video Rendering Engine.
"""

import pytest
from pathlib import Path
from clipper.core.errors import SecurityError, ValidationError, InputError
from clipper.core.rendering.plan_validator import RenderPlanPreValidator
from clipper.domain.models import RenderPlan, MediaAsset, CropKeyframe, RenderPlanProvenance


def test_plan_validator_missing_source_raises():
    prov = RenderPlanProvenance(candidate_id="c1", transcript_id="tx1")
    plan = RenderPlan(
        plan_id="p1", candidate_id="c1", source_asset_id="a1",
        start_ms=0, end_ms=5000, duration_seconds=5.0, provenance=prov
    )
    asset = MediaAsset(
        asset_id="a1", file_path="non_existent_file.mp4", filename="non_existent_file.mp4",
        extension="mp4", file_hash_sha256="abc", size_bytes=100, duration_seconds=5.0
    )

    with pytest.raises(InputError):
        RenderPlanPreValidator.validate_for_rendering(plan, asset)


def test_plan_validator_malicious_crop_x_raises(tmp_path):
    mp4_file = tmp_path / "valid.mp4"
    mp4_file.write_bytes(b"dummy_media")

    prov = RenderPlanProvenance(candidate_id="c1", transcript_id="tx1")
    kf_bad = CropKeyframe(timestamp_ms=0, crop_x=1.5, crop_y=0.0, crop_w=0.5625, crop_h=1.0)
    plan = RenderPlan(
        plan_id="p1", candidate_id="c1", source_asset_id="a1",
        start_ms=0, end_ms=5000, duration_seconds=5.0, crop_keyframes=[kf_bad], provenance=prov
    )
    asset = MediaAsset(
        asset_id="a1", file_path=str(mp4_file), filename="valid.mp4",
        extension="mp4", file_hash_sha256="abc", size_bytes=100, duration_seconds=5.0
    )

    with pytest.raises(ValidationError):
        RenderPlanPreValidator.validate_for_rendering(plan, asset)
