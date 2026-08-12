# PYTHON RUNTIME STRATEGY & ISOLATION — LOCAL AI CLIPPER

## 1. Runtime Diagnostics & Problem Statement
- **Host Environment Check:** The system reports default Python `3.14.1` registered on the host system PATH.
- **ML Ecosystem Analysis:**
  - Standard machine learning libraries (PyTorch 2.x, CTranslate2, Google MediaPipe, OpenCV, ONNX Runtime) DO NOT yet offer precompiled binary wheels for Python 3.14 on Windows x86_64.
  - Attempting to run Floor 3 (ASR) or Floor 5 (Vision) on Python 3.14 would fail due to missing wheel dependencies or C extension compilation errors.
- **System Assets Found:** Python `3.11` is installed at `C:\Users\nits4\AppData\Local\Programs\Python\Python311\python.exe` and `uv` package manager is available.

---

## 2. Decision & Runtime Architecture

### Decision
We standardize **Python 3.11** as the official target runtime for Local AI Clipper, isolated completely inside a project virtual environment (`.venv`) managed via `uv` or standard Python `venv`.

```
System Host (Python 3.14)  -->  [ISOLATED BOUNDARY]  -->  N:\local-ai-clipper\.venv (Python 3.11)
                                                          ├── PyTorch 2.3+ (CUDA 12.1 / CPU)
                                                          ├── CTranslate2 / faster-whisper
                                                          ├── MediaPipe Tasks
                                                          └── OpenCV-Python
```

---

## 3. Implementation Contracts for Floor 1

1. **Virtual Environment Creation:**
   ```powershell
   # Created in N:\local-ai-clipper via Python 3.11 launcher or uv
   uv venv --python 3.11 N:\local-ai-clipper\.venv
   ```
2. **Environment Validation in Floor Verifier:**
   - `clipper verify-floor 1` checks `sys.version_info` and asserts `major == 3 and minor == 11`.
   - Rejects execution if launched directly under system Python 3.14.
3. **Reproducible Lockfile:**
   - All runtime dependencies locked in `requirements.lock` generated via `uv pip compile`.
