"""
Safe-Zone 9:16 Crop Planner for Local AI Clipper.
"""

from typing import List
from clipper.core.errors import ValidationError
from clipper.domain.models import CropKeyframe


class CropPlanner:
    """Validates and enforces safe-zone crop boundaries and trajectory smoothness."""

    @classmethod
    def validate_and_constrain_keyframes(
        cls, keyframes: List[CropKeyframe], max_jump_per_sec: float = 0.15
    ) -> List[CropKeyframe]:
        if not keyframes:
            raise ValidationError("Crop trajectory keyframes list is empty.")

        constrained: List[CropKeyframe] = []
        for idx, kf in enumerate(keyframes):
            # Clamp bounds
            x = max(0.0, min(1.0 - kf.crop_w, kf.crop_x))
            y = max(0.0, min(1.0 - kf.crop_h, kf.crop_y))

            if idx > 0:
                prev_x = constrained[-1].crop_x
                dt_sec = max(0.1, (kf.timestamp_ms - constrained[-1].timestamp_ms) / 1000.0)
                max_allowed_delta = max_jump_per_sec * dt_sec

                delta_x = x - prev_x
                if abs(delta_x) > max_allowed_delta:
                    x = prev_x + (max_allowed_delta if delta_x > 0 else -max_allowed_delta)

            constrained.append(
                CropKeyframe(
                    timestamp_ms=kf.timestamp_ms,
                    crop_x=round(x, 4),
                    crop_y=round(y, 4),
                    crop_w=kf.crop_w,
                    crop_h=kf.crop_h,
                    target_aspect_ratio=kf.target_aspect_ratio,
                    is_interpolated=kf.is_interpolated,
                )
            )

        return constrained
