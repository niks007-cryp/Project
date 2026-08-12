# OPERATIONS MANUAL — LOCAL AI CLIPPER

## 1. CLI Commands & Operability Matrix

```bash
# Initialize project workspace
clipper init

# Ingest and validate a source video
clipper ingest --input N:/media/video.mp4

# Run local ASR transcription
clipper transcribe --job <JOB_ID> --model whisper-large-v3

# Execute clip intelligence scoring
clipper analyze --job <JOB_ID> --provider local-ollama

# Execute batch processing end-to-end
clipper process --input N:/media/video.mp4 --output-dir N:/local-ai-clipper/renders/

# Verify floor gate certification
clipper verify-floor <FLOOR_NUM>
```

## 2. Resource Management Guidelines
- **VRAM Control:** Set `CLIPPER_MAX_VRAM_GB=8` in environment to enforce explicit CUDA memory allocation safety bounds.
- **Disk Management:** Keep minimum 20GB free space on `N:` drive during multi-video batch rendering.
