# ADR-007: Python Runtime Strategy & Virtual Environment Isolation

## Status
Accepted

## Context
Host system runs Python 3.14.1, which lacks precompiled binary wheels for PyTorch, CTranslate2, and MediaPipe. Python 3.11 is available on the system at `C:\Users\nits4\AppData\Local\Programs\Python\Python311\python.exe`.

## Decision
Standardize on **Python 3.11** as the project target runtime, isolated in a dedicated project virtual environment (`.venv`) managed by `uv` or `venv`.

## Consequences
- **Pros:** Full binary wheel compatibility for PyTorch CUDA, CTranslate2, MediaPipe, and OpenCV; zero disruption to host Python.
- **Cons:** Virtual environment creation mandated in Floor 1.
