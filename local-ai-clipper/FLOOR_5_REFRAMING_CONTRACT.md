# FLOOR 5 AUTO-REFRAMING CONTRACT — LOCAL AI CLIPPER

## 1. Scope & Objective
Defines normalized 9:16 vertical crop trajectory generation from 16:9 or arbitrary aspect ratio input video.

## 2. Crop Bounds & Constraints
- Aspect Ratio: 9:16 target canvas.
- Crop Width Ratio (`crop_w`): `0.5625` (for 16:9 canvas where `crop_h = 1.0`).
- Canvas Containment: `0.0 <= crop_x <= 1.0 - crop_w` and `0.0 <= crop_y <= 1.0 - crop_h`.
- Trajectory Smoothing: Exponential Moving Average (EMA, `alpha=0.3`) smoothing applied across consecutive keyframes. Maximum horizontal jump rate capped at `< 15%` canvas width per second.
