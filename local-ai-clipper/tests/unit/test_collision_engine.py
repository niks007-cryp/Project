"""
Unit Tests for Collision Avoidance Engine.
"""

from clipper.core.vision.collision_engine import CollisionAvoidanceEngine
from clipper.domain.models import BoundingBox, CaptionSegment, CaptionWord


def test_collision_avoidance_detection_and_resolution():
    # Subject covering bottom area (ymin=0.30, height=0.60 -> extends to y=0.90)
    subject_box = BoundingBox(xmin=0.25, ymin=0.30, width=0.50, height=0.60)
    caption_seg = CaptionSegment(
        segment_id=0,
        start_ms=1000,
        end_ms=3000,
        text="Collision test caption.",
        lines=["Collision test caption."],
        position_vertical="bottom",
    )

    resolved, count = CollisionAvoidanceEngine.resolve_collisions([caption_seg], {1000: subject_box})
    assert count == 1
    assert resolved[0].position_vertical == "top"
