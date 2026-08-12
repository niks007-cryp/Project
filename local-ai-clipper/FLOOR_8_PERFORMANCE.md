# FLOOR 8 PERFORMANCE BENCHMARKS — PIPELINE ORCHESTRATION

## Benchmark Targets (15s Test Media Input)

- **End-to-End Execution Time:** ~2.5s to 3.5s total pipeline duration.
- **Real-Time Factor (RTF):** ~4.5x to 6.0x faster than real-time video playback.
- **Stage Latency Breakdown:**
  - Ingestion: ~0.15s
  - Transcription: ~0.20s (Mock ASR)
  - Intelligence: ~0.08s
  - Reframing: ~0.08s
  - Rendering: ~1.20s (Software CPU preview)
  - Quality Control: ~0.15s
- **Peak Resource Footprint:** RAM < 200 MB, CPU ~45% utilization, Disk ~120 KB per preview clip.
