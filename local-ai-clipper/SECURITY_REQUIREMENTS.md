# SECURITY REQUIREMENTS — LOCAL AI CLIPPER

## 1. Process Execution Security
- **SEC-01 Direct Array Subprocess Invocations:** All process calls (`ffmpeg`, `ffprobe`, `git`) MUST be executed by passing explicit string lists (e.g. `subprocess.run(["ffmpeg", "-i", input_path, ...])`). The use of `shell=True` or string concatenation is strictly prohibited.
- **SEC-02 Argument Sanitization:** Input file paths MUST be validated using standard filesystem paths. Arguments containing unprintable characters or control bytes MUST be rejected.

## 2. Secrets & Credential Management
- **SEC-03 Zero Hardcoded Secrets:** No API keys, passwords, or tokens shall be hardcoded in source code, configuration templates, or test suites.
- **SEC-04 Log Masking:** All loggers MUST automatically redact patterns matching known API key patterns (`AIzaSy...`, `sk-...`, `Bearer ...`).

## 3. Storage & Workspace Isolation
- **SEC-05 Path Traversal Containment:** Every job operation MUST ensure that target output paths reside strictly within the designated job directory (`N:/local-ai-clipper/jobs/<JOB_ID>/`).
- **SEC-06 Secure File Deletion:** Temporary file cleanup MUST execute safely without wildcards (`rm -rf *` prohibited).

## 4. Input Validation & Media Integrity
- **SEC-07 Header & Format Verification:** Input files MUST be probed for valid container magic bytes before spawning decoder pipelines.
- **SEC-08 Execution Timeouts:** All external process invocations MUST enforce hard wall-clock timeouts (e.g., maximum 30 minutes for media render).
