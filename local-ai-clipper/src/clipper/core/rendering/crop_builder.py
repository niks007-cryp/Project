"""
Crop Trajectory Filter Builder for Local AI Clipper.
Translates normalized 9:16 crop keyframes into FFmpeg crop expressions.
"""

from typing import List
from clipper.domain.models import CropKeyframe


class CropExpressionBuilder:
    """Constructs FFmpeg video filter crop strings from crop keyframe trajectories."""

    @classmethod
    def build_crop_filter(
        cls,
        keyframes: List[CropKeyframe],
        source_width: int = 1920,
        source_height: int = 1080,
        target_width: int = 1080,
        target_height: int = 1920,
    ) -> str:
        if not keyframes:
            # Fallback center crop filter
            cw = int(round(source_height * (9.0 / 16.0)))
            ch = source_height
            cx = (source_width - cw) // 2
            return f"crop={cw}:{ch}:{cx}:0,scale={target_width}:{target_height}"

        # Average crop_x from keyframes for smooth centered crop
        avg_crop_x = sum(kf.crop_x for kf in keyframes) / len(keyframes)
        cw = int(round(source_width * keyframes[0].crop_w))
        ch = int(round(source_height * keyframes[0].crop_h))
        cx = int(round(source_width * avg_crop_x))

        # Clamp cx bounds
        cx = max(0, min(source_width - cw, cx))

        return f"crop={cw}:{ch}:{cx}:0,scale={target_width}:{target_height}"
