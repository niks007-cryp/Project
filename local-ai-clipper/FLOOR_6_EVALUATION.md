# FLOOR 6 EVALUATION & BENCHMARKING SPECIFICATION

## Metrics Measured
1. **Rendering Pass Rate (%):** Percentage of RenderPlans successfully rendered into MP4 video artifacts.
2. **Quality Control (QC) Pass Rate (%):** Percentage of rendered MP4 files passing visual, audio, and A/V sync checks.
3. **A/V Sync Drift (seconds):** Difference between video stream duration and audio stream duration (tolerance <= 0.2s).
4. **Real-Time Factor (RTF):** `render_duration_sec / source_clip_duration_sec`.
5. **CPU / GPU Utilization (%):** Hardware resource consumption during encoding.
