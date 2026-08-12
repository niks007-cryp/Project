# ADR-006: Subtitle ASS Format & Computer Vision Trajectory Math

## Status
Accepted

## Context
High-converting short-form videos require dynamic vertical reframing and word-level animated subtitles. Hardcoding crop offsets or subtitle strings inside rendering logic creates brittle, un-maintainable code.

## Decision
We decouple:
1. **Visual Reframing:** Computer vision algorithms output a normalized `CropTrajectory` curve (center X coordinate keyframes over time).
2. **Subtitle Generation:** Timed word events are rendered to standard **Advanced SubStation Alpha (`.ass`)** files with defined safe zone bounding boxes.

## Consequences
- **Pros:** Trajectories and subtitle styles can be previewed, edited, and validated independently prior to rendering.
- **Cons:** ASS syntax formatting requires precise styling template specs.
