# FLOOR 5 EVALUATION & BENCHMARKING SPECIFICATION

## Metrics Measured
1. **Subject Visibility Rate (%):** Percentage of video duration where primary subject is within 9:16 crop boundaries.
2. **Caption Collision Rate (%):** Percentage of subtitle frames overlapping primary subject bounding box.
3. **Caption Overflow Rate (%):** Percentage of captions exceeding 35 characters or 2 lines.
4. **Crop Boundary Violation Count:** Number of crop keyframes extending outside original video resolution.
5. **Tracking Jump Rate (%):** Percentage of consecutive keyframes with erratic position jumps (> 15% frame width per frame).
6. **RenderPlan Schema Validation Rate (%):** Percentage of generated RenderPlans passing Pydantic validation.
