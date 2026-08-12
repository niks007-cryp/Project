# FLOOR 12 — LICENSE & MODEL AUDIT

## 1. Software Dependency Licenses

| Component | Version | License | Commercial Usage | Notes |
|-----------|---------|---------|------------------|-------|
| **Python** | 3.11.x | PSF License | Permitted | Core runtime environment |
| **Pydantic** | 2.13.4 | MIT | Permitted | Schema and validation framework |
| **faster-whisper** | 1.2.1 | MIT | Permitted | Local ASR binding engine |
| **CTranslate2** | 4.8.1 | MIT | Permitted | High-performance inference engine for Whisper |
| **PyTorch** | 2.13.0+cpu | BSD-3-Clause | Permitted | Tensor compute runtime |
| **FFmpeg / FFprobe** | 7.x GPL | GPL v3 | Permitted (Local binary wrapper) | Called via isolated subprocess CLI (`shell=False`) |
| **psutil** | 7.2.2 | BSD-3-Clause | Permitted | Process & hardware resource monitoring |
| **colorama** | 0.4.6 | BSD-3-Clause | Permitted | Console output formatting |
| **PyYAML** | 6.0.3 | MIT | Permitted | Configuration file parser |

---

## 2. AI Model Licenses & Provenance

| Model Identity | Role / Task | Source Repository | License | Commercial Status |
|----------------|-------------|-------------------|---------|-------------------|
| **Whisper Tiny / Small** | Audio Transcription | OpenAI / HuggingFace (`systran/faster-whisper-tiny`) | MIT License | Permitted |
| **MediaPipe Face Detector** | Visual Subject Tracking | Google MediaPipe | Apache 2.0 | Permitted |
| **Mock LLM Provider** | Candidate Scoring | Internal Synthetic Provider | Proprietary / Built-in | Permitted |
