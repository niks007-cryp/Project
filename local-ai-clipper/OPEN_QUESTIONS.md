# OPEN QUESTIONS & RESOLUTIONS — LOCAL AI CLIPPER

## 1. Resolved Floor 0 Technical Decisions

| ID | Title | Issue & Analysis | Final Decision & Resolution | Status |
|----|-------|------------------|-----------------------------|--------|
| **OQ-01** | Local ASR Package | Evaluated `faster-whisper` vs `WhisperX` vs `openai-whisper`. | **Resolved:** Selected `faster-whisper` (CTranslate2) as primary engine for 4x-8x throughput; `WhisperX` as optional diarization plugin. | **RESOLVED** |
| **OQ-02** | CV Tracking Engine | Evaluated MediaPipe vs YOLOv8/v11 vs OpenCV. | **Resolved:** Selected Google MediaPipe Tasks (Apache 2.0, zero AGPL restrictions) for face/pose tracking; OpenCV as fallback. | **RESOLVED** |
| **OQ-03** | UI Architecture | Evaluated CLI vs Local Web Panel vs Electron. | **Resolved:** Core CLI + Local Web Control Panel (served at `localhost:3000`). Decoupled architecture. | **RESOLVED** |
| **OQ-04** | Python Host Runtime | Host system reports Python 3.14.1 (lacks precompiled PyTorch/CTranslate2 binary wheels). | **Resolved:** Standardized on Python 3.11 isolated virtual environment (`.venv`) managed via `uv` or `venv`. | **RESOLVED** |
| **OQ-05** | Job State Storage | File-Based JSON manifest vs Database engine. | **Resolved:** Atomic File-Based JSON manifest (`job_manifest.json`) using Pydantic schemas. Zero external DB required. | **RESOLVED** |

---

## 2. Remaining Floor 1 Operational Questions

- **OQ-06 (FFmpeg PATH Bundling):** Standardize on system PATH detection vs auto-downloading static FFmpeg builds into project `.bin` directory during `clipper init`? (To be finalized during Floor 1 setup).
