# THIRD-PARTY SOFTWARE LICENSE INVENTORY — LOCAL AI CLIPPER

## 1. Core Python Dependencies

| Package | Version | License | Usage Role | Compliance Notes |
|---------|---------|---------|------------|------------------|
| `pydantic` | 2.13.4 | MIT | Schema Validation & Data Models | Commercial use permitted |
| `pydantic-settings` | 2.15.0 | MIT | Configuration Governance | Commercial use permitted |
| `faster-whisper` | 1.2.1 | MIT | CTranslate2 Local ASR Engine | Commercial use permitted |
| `ctranslate2` | 4.8.1 | MIT | Fast Inference Engine for Whisper | Commercial use permitted |
| `editdistance` | 0.8.1 | MIT | Fast Levenshtein Distance / WER Evaluation | Commercial use permitted |
| `huggingface-hub` | 1.27.0 | Apache 2.0 | Model Artifact Downloads | Commercial use permitted |
| `onnxruntime` | 1.28.0 | MIT | Neural Network Execution Runtime | Commercial use permitted |
| `psutil` | 7.0.0 | BSD-3-Clause | System Hardware Diagnostics | Commercial use permitted |
| `pyyaml` | 6.0.3 | MIT | Config Serialization | Commercial use permitted |
| `colorama` | 0.4.6 | BSD-3-Clause | Console Terminal Styling | Commercial use permitted |

## 2. Binary Toolchain Dependencies

| Binary Tool | License | Usage Role | Distribution Policy |
|-------------|---------|------------|---------------------|
| `ffmpeg.exe` | GPL v3.0 | Video / Audio Encoding & Normalization | Dynamically invoked sub-process |
| `ffprobe.exe` | GPL v3.0 | Media Metadata Inspection | Dynamically invoked sub-process |
