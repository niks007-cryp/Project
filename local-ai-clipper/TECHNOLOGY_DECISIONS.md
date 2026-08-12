# TECHNOLOGY DECISIONS & MATRIX — LOCAL AI CLIPPER

## 1. Automated Speech Recognition (ASR) Engine

| Candidate | Accuracy (WER) | Performance / Throughput | GPU VRAM | Windows Native Support | License | Ecosystem & Maintenance | Decision & Rationale |
|-----------|----------------|--------------------------|----------|------------------------|---------|-------------------------|----------------------|
| **faster-whisper** (CTranslate2) | High (equal to OpenAI Whisper) | 4x-8x faster than standard PyTorch Whisper | 2GB - 8GB (Int8 / FP16) | High (Prebuilt Windows CTranslate2 wheels) | MIT | Active, widely adopted in local media tools | **SELECTED (Primary):** Best throughput, low VRAM footprint, standalone C++ inference backend. |
| **WhisperX** | High + Forced Alignment | 3x-6x faster | 4GB - 10GB | Medium (Complex pyannote/torch audio C++ dependencies on Windows) | MIT / VAD restrictions | Active | **SELECTED (Secondary / Diarization Plugin):** Excellent for word alignment & multi-speaker diarization; optional module in Floor 3. |
| **openai-whisper** (Vanilla PyTorch) | High | Baseline (1x) | 4GB - 10GB | High | MIT | Core reference | **REJECTED as primary:** Slow inference speed compared to CTranslate2. |
| **vosk-api** | Moderate | Very High (CPU lightweight) | Low (CPU only) | High | Apache 2.0 | Stable | **REJECTED:** Lower transcript accuracy on unconstrained podcast/video audio. |

---

## 2. Computer Vision (CV) & Subject Tracking Engine

| Candidate | Subject Detection Accuracy | Framing Stability / Tracking | GPU / Hardware | Windows Support | License | Maintenance | Decision & Rationale |
|-----------|----------------------------|------------------------------|----------------|-----------------|---------|-------------|----------------------|
| **Google MediaPipe Tasks** | High (Face, Pose, Person Segmentation) | High (Landmark stabilization) | Lightweight CPU & GPU | High (Native Python / Windows wheels) | Apache 2.0 | Active (Google) | **SELECTED (Primary):** Fast, lightweight, zero license issues, built-in face landmarking ideal for 9:16 framing. |
| **YOLOv8 / YOLOv11** (Ultralytics) | Superior Person/Object detection | High | Requires CUDA GPU for high FPS | High | AGPL-3.0 (Commercial restrictions) | Active | **REJECTED as default:** AGPL-3.0 copyleft license imposes severe commercial/proprietary constraints. |
| **OpenCV (DNN / Haar Cascade)** | Moderate | Moderate (High jitter without Kalman filter) | CPU / CUDA | High | Apache 2.0 / BSD | Mature | **SELECTED (Fallback):** Native fallback for basic face box detection if MediaPipe unavailable. |

---

## 3. User Interface (UI) & Control Panel

| Option | Architecture Complexity | Performance / Responsiveness | Installation / Footprint | Windows UX Quality | Maintenance Cost | Decision & Rationale |
|--------|-------------------------|------------------------------|--------------------------|--------------------|------------------|----------------------|
| **CLI-Only Core + Local Web Control Panel** (FastAPI / Node + Vite/React) | Low / Modular | Very High (Decoupled background daemon) | Lightweight (Zero heavy bundler runtime) | High (Runs in local browser at `localhost:3000`) | Low | **SELECTED:** Perfect separation of pipeline core from UI. Runs headless or locally served. |
| **Electron App** | High | Medium (Chromium overhead) | Heavy (>200MB installer + Node/Python binary orchestration) | High | High | **REJECTED for V1:** Adds unnecessary IPC packaging complexity over simple local web server. |
| **Streamlit / Gradio** | Very Low | Low (Full page re-renders) | Low | Moderate | Low | **REJECTED for Production:** Poor fine-grained custom UI styling for 9:16 video timelines and custom canvas safe-zone previews. |

---

## 4. Job Queue & Orchestration Engine

| Candidate | Architecture | Dependency Footprint | Persistence & Checkpointing | Windows Compatibility | Decision & Rationale |
|-----------|--------------|----------------------|-----------------------------|-----------------------|----------------------|
| **File-Based State Machine + Async Queue** | Embedded Python (`asyncio` + JSON Manifest) | Zero external dependencies | Atomic JSON file checkpoints (`job_manifest.json`) | 100% Native | **SELECTED:** Zero database service setup required. Completely portable, deterministic, and crash-resilient. |
| **Celery + Redis** | Distributed Task Queue | Heavy (Requires Redis service running on Windows) | In-memory + Redis store | Complex on Windows native | **REJECTED for V1:** Violates zero-dependency local-first simplicity. |
| **SQLite + APScheduler** | Embedded SQL Database | Zero external services | Relational table checkpoints | 100% Native | **SELECTED (V2 Path):** Database adapter interface hook for multi-job concurrent queuing. |
