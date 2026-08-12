# OBSERVABILITY & LOGGING — LOCAL AI CLIPPER

## 1. Structured JSON Logging Format
All system events MUST output structured JSON logs to stdout and job log files (`N:/local-ai-clipper/jobs/<JOB_ID>/logs/pipeline.log`).

```json
{
  "timestamp": "2026-08-11T22:36:12.401Z",
  "level": "INFO",
  "job_id": "job_20260811_98412a",
  "stage": "transcription",
  "component": "ASREngine",
  "event": "transcription_segment_completed",
  "metrics": {
    "segment_index": 14,
    "start_ms": 120000,
    "end_ms": 135000,
    "processing_duration_ms": 420
  },
  "context": {
    "model": "whisper-large-v3",
    "device": "cuda"
  }
}
```

## 2. Core Metrics & Telemetry

| Metric Name | Type | Description |
|-------------|------|-------------|
| `clipper_job_duration_seconds` | Histogram | Overall job execution time broken down by stage. |
| `clipper_asr_realtime_factor` | Gauge | Ratio of audio processing time to audio duration. |
| `clipper_llm_tokens_total` | Counter | Total prompt & completion tokens consumed per provider. |
| `clipper_render_fps` | Gauge | FFmpeg frame encoding throughput. |
| `clipper_qc_failures_total` | Counter | Count of QC check rejections by failure mode. |
