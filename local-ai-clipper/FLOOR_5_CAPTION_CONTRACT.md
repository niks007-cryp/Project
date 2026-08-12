# FLOOR 5 CAPTION & SUBTITLE CONTRACT — LOCAL AI CLIPPER

## 1. Subtitle Segmentation Rules
- Maximum Characters Per Line: 35 chars.
- Maximum Lines Per Segment: 2 lines.
- Reading Speed Limit: <= 25 characters per second (CPS).
- Timestamp Alignment: Subtitle segment bounds align strictly with word-level timestamps from Floor 3 ASR `Transcript`.

## 2. ASS Style Configuration
- Font Family: `Outfit` (fallback to Arial/sans-serif).
- Font Size: 24pt.
- Colors: Primary White (`&H00FFFFFF`), Outline Black (`&H00000000`), Background Semi-transparent (`&H80000000`).
- Collision Resolution: Automatically shifts subtitle position from bottom to top (`position_vertical="top"`) when subject-subtitle bounding box overlap exceeds 5%.
