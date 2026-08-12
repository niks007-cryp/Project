# SYSTEM REQUIREMENTS — LOCAL AI CLIPPER

## 1. Functional Requirements (FR)
- **FR-01 Media Ingestion:** The system MUST accept video files in MP4, MOV, MKV, WEBM, and M4V formats with resolutions up to 4K (3840x2160) at 23.976, 24, 25, 29.97, 30, 59.94, and 60 FPS.
- **FR-02 Pre-processing & Validation:** The system MUST inspect input files via `ffprobe` to verify media stream presence, container integrity, and extract duration, codec, and aspect ratio metrics before queuing.
- **FR-03 Local Transcription:** The system MUST extract mono audio (16kHz 16-bit PCM WAV) and execute local ASR to produce word-level timestamps (start time, end time, confidence score).
- **FR-04 Candidate Boundary Generation:** The system MUST generate clip candidates based on semantic completeness (target duration 15s - 90s), preventing truncated sentences or abrupt word cuts.
- **FR-05 Candidate Ranking & Scoring:** The system MUST evaluate clip candidates on hook strength, story arc completeness, curiosity, and emotional resonance, returning structured evaluation metadata.
- **FR-06 Deduplication:** The system MUST eliminate clip candidates that have >40% temporal overlap or >70% semantic similarity.
- **FR-07 Subject-Aware Reframing:** The system MUST analyze video frames using computer vision to detect speaker faces and dynamic main subjects, outputting a smooth 9:16 vertical crop trajectory without dynamic jitter.
- **FR-08 Caption Styling:** The system MUST burn in timed subtitles using template-based ASS styles with enforced safe zones (top 15%, bottom 20% clear of UI overlay).
- **FR-09 Automated QC:** The system MUST run automated verification on generated clips, failing any clip with frozen frames, silent audio, out-of-sync audio/video (>100ms drift), or ASS syntax errors.

## 2. Non-Functional Requirements (NFR)
- **NFR-01 Local-First Privacy:** No raw video frames or full audio binaries shall be transmitted to external services. Only text transcripts and structural metadata may be passed to external APIs when configured.
- **NFR-02 Deterministic Checkpointing:** Every job stage MUST persist state so that pipeline execution can resume from the last successful stage following a crash or cancellation.
- **NFR-03 Process Isolation:** FFmpeg process invocations MUST be launched using explicit array syntax with strict timeout limits and resource quotas.
- **NFR-04 Performance Target:** Real-time processing ratio MUST be <= 0.5x source duration on standard GPU-accelerated hardware (e.g., a 60-minute video fully processed in under 30 minutes).

## 3. System Constraints
- **OS:** Windows 11 64-bit / Linux x86_64.
- **Runtime:** Python 3.11 isolated `.venv`.
- **Dependencies:** FFmpeg binaries must be installed and accessible.
