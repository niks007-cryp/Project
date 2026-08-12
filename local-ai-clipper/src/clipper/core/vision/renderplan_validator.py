"""
Deterministic RenderPlan Quality Validator for Local AI Clipper.
"""

from clipper.core.errors import ValidationError
from clipper.domain.models import RenderPlan


class RenderPlanValidator:
    """Validates structural integrity, crop bounds, and subtitle timing of RenderPlans."""

    @classmethod
    def validate_plan(cls, plan: RenderPlan) -> None:
        if not plan.plan_id:
            raise ValidationError("RenderPlan missing plan_id.")

        if not plan.candidate_id:
            raise ValidationError("RenderPlan missing candidate_id.")

        if plan.duration_seconds <= 0:
            raise ValidationError(f"RenderPlan '{plan.plan_id}' has invalid duration ({plan.duration_seconds}s).")

        if not plan.crop_keyframes:
            raise ValidationError(f"RenderPlan '{plan.plan_id}' contains no crop keyframes.")

        for idx, kf in enumerate(plan.crop_keyframes):
            if kf.crop_x < 0.0 or (kf.crop_x + kf.crop_w) > 1.0001:
                raise ValidationError(
                    f"RenderPlan '{plan.plan_id}' keyframe {idx} crop_x ({kf.crop_x}) extends out of canvas bounds."
                )

        if not plan.caption_segments:
            raise ValidationError(f"RenderPlan '{plan.plan_id}' contains no caption segments.")

        for idx, seg in enumerate(plan.caption_segments):
            if seg.end_ms <= seg.start_ms:
                raise ValidationError(
                    f"RenderPlan '{plan.plan_id}' caption segment {idx} has invalid bounds ({seg.start_ms} to {seg.end_ms}ms)."
                )
            for line in seg.lines:
                if len(line) > 50:  # Hard limit check
                    raise ValidationError(
                        f"RenderPlan '{plan.plan_id}' caption line exceeds max character limit: '{line[:40]}...'"
                    )
