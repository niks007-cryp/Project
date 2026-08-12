"""
Unit Tests for RenderPlan Validator.
"""

import pytest
from clipper.core.vision.renderplan_validator import RenderPlanValidator
from clipper.core.errors import ValidationError
from clipper.domain.models import RenderPlan, RenderPlanProvenance, CropKeyframe, CaptionSegment


def test_renderplan_validator_valid():
    prov = RenderPlanProvenance(candidate_id="cand_1", transcript_id="tx_1")
    plan = RenderPlan(
        plan_id="plan_valid",
        candidate_id="cand_1",
        source_asset_id="ast_1",
        start_ms=0,
        end_ms=20000,
        duration_seconds=20.0,
        crop_keyframes=[CropKeyframe(timestamp_ms=0, crop_x=0.25, crop_y=0.0, crop_w=0.5625, crop_h=1.0)],
        caption_segments=[CaptionSegment(segment_id=0, start_ms=1000, end_ms=3000, text="Valid line.", lines=["Valid line."])],
        provenance=prov,
    )

    RenderPlanValidator.validate_plan(plan)  # Should not raise


def test_renderplan_validator_invalid_crop_raises():
    prov = RenderPlanProvenance(candidate_id="cand_1", transcript_id="tx_1")
    plan = RenderPlan(
        plan_id="plan_invalid",
        candidate_id="cand_1",
        source_asset_id="ast_1",
        start_ms=0,
        end_ms=20000,
        duration_seconds=20.0,
        crop_keyframes=[CropKeyframe(timestamp_ms=0, crop_x=0.80, crop_y=0.0, crop_w=0.5625, crop_h=1.0)],  # Exceeds 1.0
        caption_segments=[CaptionSegment(segment_id=0, start_ms=1000, end_ms=3000, text="Valid", lines=["Valid"])],
        provenance=prov,
    )

    with pytest.raises(ValidationError):
        RenderPlanValidator.validate_plan(plan)
