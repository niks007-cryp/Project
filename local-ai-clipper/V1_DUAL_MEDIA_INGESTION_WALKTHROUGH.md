# V1.0 DUAL MEDIA INGESTION & LOCAL WORKER CONNECTION WALKTHROUGH

## 1. Existing Architecture & Overview
This walkthrough documents the implementation of **Dual Media Ingestion** (Local File Upload + YouTube Video URL) and the **Environment-Aware Local Worker Connection Boundary** for **Local AI Clipper**.

All processing continues to follow the certified 100% database-free, local-first pipeline:
```text
  Local File Upload OR YouTube URL
                 ↓
      Local Worker Acquisition
                 ↓
       MediaAsset (Floor 2)
                 ↓
  Floor 3 (ASR) → Floor 4 (LLM) → Floor 5 (CV) → Floor 6 (Rendering & QC)
```

---

## 2. Problem Diagnosis & Localhost Fix

### Localhost Boundary Diagnosis
Previously, the Web Control Panel assumed that `localhost:3000` was hardcoded as both the UI domain and worker domain. When deployed to Vercel Preview/Production, attempting to fetch `/api/...` directly from Vercel caused routing failures because Vercel was not running the heavy local Python worker engine.

### Fix Implemented
- **Environment-Aware Worker URL**: The Web Control Panel UI now checks `localStorage.getItem('clipper_worker_url')` or `window.location.origin` (if running locally on localhost/127.0.0.1) and defaults to `http://127.0.0.1:3000`.
- **Dynamic Worker Health Badge**: Pings `${getWorkerUrl()}/api/health` live. Displays `Control Plane: Active | Worker: Connected (127.0.0.1:3000)` when healthy, or `Worker: Disconnected` when offline.
- **Worker Configuration in UI**: Added worker endpoint setting in Settings tab allowing users to pair any Vercel Preview UI instance with their local hardware worker engine.

---

## 3. Dual Media Ingestion Architecture

### Input Method 1: Local Video File Upload (`LOCAL_UPLOAD`)
- **UI Interface**: Native browser `<input type="file" accept=".mp4,.mov,.mkv,.webm,.m4v">`.
- **Worker Ingestion**: Direct stream POST to `/api/media/upload` with `X-Filename` header.
- **Processing**: Uploaded file saved to `jobs/<JOB_ID>/uploads/`, validated via `IngestionSecurityValidator`, probed via `SafeFFprobe`, hashed via SHA-256, and registered as a `MediaAsset`.

### Input Method 2: YouTube Video URL (`YOUTUBE_URL`)
- **UI Interface**: Text input field accepting `https://www.youtube.com/watch?v=...`, `https://youtu.be/...`, or `https://www.youtube.com/shorts/...`.
- **Compliance & Rights Notice**: "Only process content you have the necessary rights or permission to use."
- **URL Validation**: `validate_youtube_url()` verifies HTTPS scheme, host whitelist (`youtube.com`, `www.youtube.com`, `m.youtube.com`, `youtu.be`), and enforces strict SSRF protection rejecting IP addresses (`127.0.0.1`, `10.*`, `192.168.*`, `172.16.*`), localhost, file://, data:, etc.
- **yt-dlp Execution**: Executed via `SafeSubprocess` (`shell=False`, argument array, timeout = 300s). `yt-dlp` version verified (`2026.07.04` >= `2024.0.0`).
- **Controlled Output Path**: Output saved exclusively to controlled path `jobs/<JOB_ID>/source/source_download.mp4` (never untrusted video titles).
- **Error Taxonomy**: Handled `LOGIN_REQUIRED`, `PRIVATE`, `AGE_RESTRICTED`, `UNAVAILABLE`, `ACCESS_DENIED` with clear user-facing messages.

### Convergence into MediaAsset
Both local file uploads and YouTube URL acquisitions converge into `IngestionStage` and produce a standard `MediaAsset`. From `MediaAsset` onward, transcription, intelligence scoring, reframing, rendering, and quality control run through the **IDENTICAL PIPELINE**.

---

## 4. Verification & Testing

- **Secret Scan (`scripts/scan_secrets.py`)**: 215 files scanned — 0 secrets detected.
- **Pytest Suite**: 100/100 tests passed cleanly (36.60s), including 3 new unit tests in `test_youtube_ingestion.py`.
- **Git Commit & Push**: Commit `c0721ad` pushed to `https://github.com/niks007-cryp/Project.git` on branch `main`.

---

## 5. Summary of Files Created / Modified

- **Created**:
  - `src/clipper/core/ingestion/youtube.py`
  - `tests/unit/test_youtube_ingestion.py`
  - `V1_DUAL_MEDIA_INGESTION_WALKTHROUGH.md`
- **Modified**:
  - `src/clipper/domain/models.py`
  - `src/clipper/pipeline/ingestion_stage.py`
  - `src/clipper/web/api.py`
  - `src/clipper/web/server.py`
  - `src/clipper/web/static/index.html`
  - `pyproject.toml`
- **Pushed Commit**: `c0721ad` to `https://github.com/niks007-cryp/Project.git`
