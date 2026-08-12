"""
Unit Tests for RenderPlan & Visual Intelligence Domain Schemas.
"""

from clipper.domain.models import (
    RenderPlan,
    RenderPlanProvenance,
    CropKeyframe,
    CaptionSegment,
    CaptionWord,
    CaptionStyle,
    BoundingBox,
)


def test_renderplan_schema_initialization():
    prov = RenderPlanProvenance(candidate_id="cand_001", transcript_id="tx_123")
    keyframe = CropKeyframe(
        timestamp_ms=0,
        crop_x=0.25,
        crop_y=0.0,
        crop_w=0.5625,  # 9:16 ratio on 16:9 canvas
        crop_h=1.0,
    )
    caption = CaptionSegment(
        segment_id=0,
        start_ms=500,
        end_ms=2500,
        text="Welcome to local AI video clipping.",
        lines=["Welcome to local AI", "video clipping."],
        words=[CaptionWord(word="Welcome", start_ms=500, end_ms=900)],
    )

    plan = RenderPlan(
        plan_id="plan_001",
        candidate_id="cand_001",
        source_asset_id="asset_123",
        start_ms=0,
        end_ms=30000,
        duration_seconds=30.0,
        crop_keyframes=[keyframe],
        caption_segments=[caption],
        provenance=prov,
    )

    assert plan.plan_id == "plan_001"
    assert len(plan.crop_keyframes) == 1
    assert plan.crop_keyframes[0].crop_w == 0.5625
    assert len(plan.caption_segments) == 1
    assert plan.caption_segments[0].lines[0] == "Welcome to local AI"
