"""
Unit Tests for Subject Tracker & Crop Planner.
"""

from clipper.core.vision.tracker import SubjectTracker
from clipper.core.vision.crop_planner import CropPlanner
from clipper.domain.models import BoundingBox, CropKeyframe


def test_tracker_trajectory_and_crop_planner():
    boxes = {
        0: BoundingBox(xmin=0.10, ymin=0.1, width=0.2, height=0.5),
        1000: BoundingBox(xmin=0.50, ymin=0.1, width=0.2, height=0.5),
        2000: BoundingBox(xmin=0.80, ymin=0.1, width=0.2, height=0.5),
    }

    raw_kfs = SubjectTracker.generate_trajectory(boxes, start_ms=0, end_ms=2000)
    assert len(raw_kfs) == 3

    valid_kfs = CropPlanner.validate_and_constrain_keyframes(raw_kfs)
    assert len(valid_kfs) == 3
    for kf in valid_kfs:
        assert 0.0 <= kf.crop_x <= (1.0 - kf.crop_w)
