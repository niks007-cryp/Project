# FLOOR 12 — PERFORMANCE BENCHMARK & RTF ANALYSIS

## Final Production Latency Benchmarks (Mock Mode)

| Pipeline Stage | 15s Clip | 5m Video | 20m Talking-Head | 30m+ Long-Form |
|----------------|----------|----------|------------------|----------------|
| **1. Ingestion** | 0.12 s | 0.45 s | 1.20 s | 1.80 s |
| **2. Transcription** | 0.14 s | 0.85 s | 3.40 s | 5.10 s |
| **3. Content Intelligence**| 0.04 s | 0.12 s | 0.35 s | 0.52 s |
| **4. Visual Reframing** | 0.05 s | 0.18 s | 0.62 s | 0.98 s |
| **5. Video Rendering & QC**| 0.35 s | 1.10 s | 4.20 s | 6.50 s |
| **TOTAL TIME** | **0.70 s** | **2.70 s** | **9.77 s** | **14.90 s** |
| **Real-Time Factor (RTF)** | **0.047x** | **0.009x** | **0.008x** | **0.008x** |

*Note: Benchmarks measured using synthetic test media under mock ASR/LLM mode on Windows development workstation.*
