"""
Subject Tracker & Trajectory Generator for Content Intelligence Engine.
Computes smooth horizontal center motion path for 9:16 vertical crop.
"""

from typing import Dict, List
from clipper.domain.models import BoundingBox, CropKeyframe


class SubjectTracker:
    """Computes smooth 9:16 crop trajectories centered on detected subjects."""

    @classmethod
    def generate_trajectory(
        cls,
        boxes: Dict[int, BoundingBox],
        start_ms: int,
        end_ms: int,
        sample_interval_ms: int = 500,
        smoothing_alpha: float = 0.3,
        crop_w_ratio: float = 0.5625,  # 9:16 ratio on 16:9 canvas
    ) -> List[CropKeyframe]:
        keyframes: List[CropKeyframe] = []

        timestamps = sorted([ts for ts in boxes.keys() if start_ms <= ts <= end_ms])
        if not timestamps:
            # Fallback to single center keyframe
            keyframes.append(
                CropKeyframe(
                    timestamp_ms=start_ms,
                    crop_x=round((1.0 - crop_w_ratio) / 2.0, 4),
                    crop_y=0.0,
                    crop_w=crop_w_ratio,
                    crop_h=1.0,
                    target_aspect_ratio="9:16",
                )
            )
            return keyframes

        prev_crop_x: float = (1.0 - crop_w_ratio) / 2.0

        for idx, ts in enumerate(timestamps):
            box = boxes[ts]
            subject_cx = box.xmin + (box.width / 2.0)

            # Target crop xmin centered on subject_cx
            target_crop_x = subject_cx - (crop_w_ratio / 2.0)

            # Clamp crop within canvas bounds [0.0, 1.0 - crop_w_ratio]
            clamped_crop_x = max(0.0, min(1.0 - crop_w_ratio, target_crop_x))

            # Apply Exponential Moving Average (EMA) smoothing
            if idx == 0:
                smoothed_crop_x = clamped_crop_x
            else:
                smoothed_crop_x = (smoothing_alpha * clamped_crop_x) + ((1.0 - smoothing_alpha) * prev_crop_x)

            prev_crop_x = smoothed_crop_x

            keyframes.append(
                CropKeyframe(
                    timestamp_ms=ts,
                    crop_x=round(smoothed_crop_x, 4),
                    crop_y=0.0,
                    crop_w=round(crop_w_ratio, 4),
                    crop_h=1.0,
                    target_aspect_ratio="9:16",
                    is_interpolated=False,
                )
            )

        return keyframes
