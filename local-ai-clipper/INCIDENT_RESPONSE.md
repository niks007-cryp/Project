# INCIDENT RESPONSE & TROUBLESHOOTING — LOCAL AI CLIPPER

## 1. Failure Taxonomy & Remediation

| Error Code | Failure Class | Severity | Immediate Remediation |
|------------|---------------|----------|-----------------------|
| `ERR_FFMPEG_SUBPROCESS` | Pipeline Hardware / Process Error | HIGH | Check FFmpeg path installation; inspect raw FFmpeg filtergraph log in `jobs/<JOB_ID>/logs/render.log`. |
| `ERR_ASR_OOM` | CUDA VRAM Exhaustion | HIGH | Automatically fall back to CPU execution or quantized model (`whisper-medium` int8). |
| `ERR_LLM_SCHEMA_INVALID` | Model Schema Failure | MEDIUM | Retry prompt invocation (max 3 retries); fall back to local rule-based candidate boundaries. |
| `ERR_QC_AUDIO_SYNC` | Quality Check Rejection | MEDIUM | Re-extract audio stream; check source video variable frame rate (VFR) and convert to constant frame rate (CFR). |

## 2. Emergency Recovery Runbook
1. Inspect active job status: `clipper status --job <JOB_ID>`.
2. Inspect last stage log: `view_file N:/local-ai-clipper/jobs/<JOB_ID>/logs/pipeline.log`.
3. Clear locks and resume execution from last checkpoint: `clipper retry --job <JOB_ID>`.
