"""
RenderPlan Pre-Render Quality Validator for Local AI Clipper.
Verifies source media asset, crop bounds, caption timing, and output paths prior to rendering.
"""

from pathlib import Path
from clipper.core.errors import ValidationError, InputError
from clipper.domain.models import RenderPlan, MediaAsset


class RenderPlanPreValidator:
    """Pre-rendering validator ensuring source assets and RenderPlans are safe for FFmpeg."""

    @classmethod
    def validate_for_rendering(cls, plan: RenderPlan, media_asset: MediaAsset) -> None:
        if not plan:
            raise ValidationError("RenderPlan object is missing.")

        if not media_asset:
            raise InputError("Source MediaAsset object is missing.")

        source_file = Path(media_asset.file_path).resolve()
        if not source_file.exists():
            raise InputError(f"Source media file for rendering does not exist: {source_file}")

        if plan.duration_seconds <= 0:
            raise ValidationError(f"RenderPlan duration ({plan.duration_seconds}s) is invalid.")

        if not plan.crop_keyframes:
            raise ValidationError("RenderPlan contains zero crop keyframes.")

        for idx, kf in enumerate(plan.crop_keyframes):
            if kf.crop_x < 0.0 or (kf.crop_x + kf.crop_w) > 1.0001:
                raise ValidationError(
                    f"RenderPlan keyframe {idx} crop_x ({kf.crop_x}) extends outside source bounds."
                )

        if not plan.caption_segments:
            raise ValidationError("RenderPlan contains zero caption segments.")
