"""
Unit Tests for Visual & Caption Evaluator.
"""

from clipper.core.vision.evaluator import VisualEvaluator
from clipper.domain.models import RenderPlan, RenderPlanProvenance, CropKeyframe, CaptionSegment, BoundingBox


def test_visual_evaluator_metrics():
    prov = RenderPlanProvenance(candidate_id="c1", transcript_id="tx1")
    plan = RenderPlan(
        plan_id="p1",
        candidate_id="c1",
        source_asset_id="a1",
        start_ms=0,
        end_ms=10000,
        duration_seconds=10.0,
        crop_keyframes=[
            CropKeyframe(timestamp_ms=0, crop_x=0.25, crop_y=0.0, crop_w=0.5625, crop_h=1.0),
            CropKeyframe(timestamp_ms=1000, crop_x=0.26, crop_y=0.0, crop_w=0.5625, crop_h=1.0),
        ],
        caption_segments=[
            CaptionSegment(segment_id=0, start_ms=0, end_ms=2000, text="Short caption", lines=["Short caption"])
        ],
        provenance=prov,
    )

    boxes = {
        0: BoundingBox(xmin=0.35, ymin=0.1, width=0.2, height=0.5),
        1000: BoundingBox(xmin=0.36, ymin=0.1, width=0.2, height=0.5),
    }

    res = VisualEvaluator.evaluate_render_plan(plan, boxes)
    assert res["subject_visibility_pct"] == 100.0
    assert res["tracking_jump_rate_pct"] == 0.0
    assert res["crop_boundary_violations"] == 0
