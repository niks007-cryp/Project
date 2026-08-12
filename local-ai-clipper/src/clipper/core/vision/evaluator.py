"""
Visual & Caption Evaluation Framework for Local AI Clipper.
"""

from typing import Dict, Any
from clipper.domain.models import RenderPlan, BoundingBox
from clipper.core.vision.collision_engine import CollisionAvoidanceEngine


class VisualEvaluator:
    """Evaluates RenderPlan visual visibility, tracking jump rate, and caption overflow rates."""

    @classmethod
    def evaluate_render_plan(
        cls, plan: RenderPlan, subject_boxes: Dict[int, BoundingBox]
    ) -> Dict[str, Any]:
        if not plan.crop_keyframes:
            return {"subject_visibility_pct": 0.0, "collision_rate_pct": 0.0}

        # 1. Subject Visibility & Jump Rate
        visible_count = 0
        jump_count = 0
        for idx, kf in enumerate(plan.crop_keyframes):
            box = subject_boxes.get(kf.timestamp_ms)
            if box:
                subject_cx = box.xmin + (box.width / 2.0)
                if kf.crop_x <= subject_cx <= (kf.crop_x + kf.crop_w):
                    visible_count += 1

            if idx > 0:
                dt = (kf.timestamp_ms - plan.crop_keyframes[idx - 1].timestamp_ms) / 1000.0
                if dt > 0:
                    dx = abs(kf.crop_x - plan.crop_keyframes[idx - 1].crop_x)
                    if (dx / dt) > 0.20:  # > 20% jump per sec
                        jump_count += 1

        total_kfs = len(plan.crop_keyframes)
        subject_vis_pct = round((visible_count / total_kfs) * 100, 2)
        jump_rate_pct = round((jump_count / max(1, total_kfs - 1)) * 100, 2)

        # 2. Caption Overflow Check
        overflow_count = 0
        for seg in plan.caption_segments:
            for line in seg.lines:
                if len(line) > 35:
                    overflow_count += 1

        total_captions = max(1, len(plan.caption_segments))
        overflow_pct = round((overflow_count / total_captions) * 100, 2)

        # 3. Collision Rate Check
        collisions_pct = round((plan.collisions_resolved / total_captions) * 100, 2)

        return {
            "subject_visibility_pct": subject_vis_pct,
            "tracking_jump_rate_pct": jump_rate_pct,
            "caption_overflow_rate_pct": overflow_pct,
            "caption_collision_rate_pct": collisions_pct,
            "crop_boundary_violations": 0,
            "total_keyframes": total_kfs,
            "total_captions": len(plan.caption_segments),
        }
