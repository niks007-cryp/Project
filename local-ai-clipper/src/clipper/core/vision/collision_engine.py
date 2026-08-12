"""
Caption & Subject Collision Avoidance Engine for Content Intelligence System.
Detects visual collision between subject bounding boxes and caption regions.
"""

from typing import List, Dict, Tuple
from clipper.domain.models import (
    BoundingBox,
    CaptionSegment,
    CollisionBox,
)


class CollisionAvoidanceEngine:
    """Detects and resolves visual overlap between subject and subtitle regions."""

    @classmethod
    def calculate_box_overlap(cls, box1: BoundingBox, box2: BoundingBox) -> float:
        """Calculates Intersection-over-Min Area ratio between two normalized bounding boxes."""
        x_left = max(box1.xmin, box2.xmin)
        y_top = max(box1.ymin, box2.ymin)
        x_right = min(box1.xmin + box1.width, box2.xmin + box2.width)
        y_bottom = min(box1.ymin + box1.height, box2.ymin + box2.height)

        if x_right <= x_left or y_bottom <= y_top:
            return 0.0

        intersection_area = (x_right - x_left) * (y_bottom - y_top)
        area1 = box1.width * box1.height
        area2 = box2.width * box2.height

        min_area = min(area1, area2)
        if min_area <= 0:
            return 0.0

        return round(intersection_area / min_area, 4)

    @classmethod
    def resolve_collisions(
        cls,
        caption_segments: List[CaptionSegment],
        subject_boxes: Dict[int, BoundingBox],
    ) -> Tuple[List[CaptionSegment], int]:
        resolved_segments: List[CaptionSegment] = []
        collisions_count = 0

        # Define default bottom caption box: ymin=0.80, height=0.15
        default_caption_box = BoundingBox(xmin=0.20, ymin=0.80, width=0.60, height=0.15)

        for seg in caption_segments:
            # Check subject box at segment start timestamp
            ts = seg.start_ms
            subject_box = subject_boxes.get(ts) or BoundingBox(xmin=0.35, ymin=0.15, width=0.30, height=0.70)

            overlap = cls.calculate_box_overlap(subject_box, default_caption_box)

            if overlap > 0.05:
                # Collision detected -> relocate caption to top region
                seg.position_vertical = "top"
                seg.vertical_margin_pct = 85.0
                collisions_count += 1
            else:
                seg.position_vertical = "bottom"
                seg.vertical_margin_pct = 10.0

            resolved_segments.append(seg)

        return resolved_segments, collisions_count
