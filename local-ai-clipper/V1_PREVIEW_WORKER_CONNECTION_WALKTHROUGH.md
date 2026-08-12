# V1.0 PREVIEW — LOCAL WORKER CONNECTION WALKTHROUGH

## 1. Local Worker Startup & Health
- **Worker Execution**: Local AI Clipper web server started on `http://127.0.0.1:3000` via `clipper ui` (`python -m clipper.cli.main ui`).
- **Worker Status**: Listening and active on `127.0.0.1:3000`.
- **Health Response**: Verified `GET http://127.0.0.1:3000/api/health`:
  - `version`: `0.1.0`
  - `mode`: `local`
  - `doctor`: 6/6 diagnostic tests passed (Python 3.11, Git, Node.js, Docker, FFmpeg N-126060, Hardware 75.21 GB free).
  - `workspace_dir`: `N:\local-ai-clipper`

---

## 2. Preview Connection Architecture & Boundary
- **Vercel Control Plane**: Static Web Control Panel hosted on Vercel Preview (`https://project-*.vercel.app`).
- **Local Worker Boundary**: All heavy AI and video processing engines (FFmpeg, Whisper ASR, MediaPipe, yt-dlp, PyTorch) remain 100% on the user's local hardware.
- **Browser-to-Worker Connection**: The user's web browser connects directly to their local hardware engine (`http://127.0.0.1:3000`).

---

## 3. CORS & Origin Security Configuration
- **Allowed Origins**: `ClipperHTTPRequestHandler` dynamically reflects incoming request `Origin` headers while enforcing explicit method and header permissions:
  - `Access-Control-Allow-Origin: <Request-Origin>`
  - `Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type, X-Filename`
- **Preflight OPTIONS**: Preflight OPTIONS requests return HTTP 200 with matching CORS response headers.

---

## 4. Dual Media Ingestion & Worker Test Execution

### Test 1: Local Video File Upload
- **Endpoint**: `POST http://127.0.0.1:3000/api/media/upload`
- **Protocol**: Direct binary stream POST with `X-Filename` header.
- **Verification**: Ingested file saved to `jobs/<JOB_ID>/uploads/`, validated via `IngestionSecurityValidator`, probed via `SafeFFprobe`, hashed via SHA-256, and registered as a `MediaAsset`.

### Test 2: YouTube URL Acquisition
- **Endpoint**: `POST http://127.0.0.1:3000/api/media/ingest-youtube`
- **Protocol**: JSON payload `{"url": "https://www.youtube.com/watch?v=..."}`.
- **Validation & Security**: Enforces HTTPS scheme, official domain whitelist (`youtube.com`, `youtu.be`), strict SSRF protection rejecting IP addresses/localhost.
- **Acquisition**: `yt-dlp` version `2026.07.04` executed via `SafeSubprocess` (`shell=False`). Output saved to controlled job directory `jobs/<JOB_ID>/source/source_download.mp4`.
- **Convergence**: Output ingested into `IngestionStage` and registered as a `MediaAsset`.

---

## 5. Security & Isolation Verification
- **BYOK Isolation**: User API keys are stored in platform-native DPAPI encrypted vault (`.vault/`) and masked as `****...XXXX`. Zero credentials exist in source code, client JavaScript, or GitHub.
- **Secret Scan (`scripts/scan_secrets.py`)**: 215 files scanned — 0 secrets detected.
- **Pytest Suite**: 100/100 tests passed cleanly (34.24s).

---

## 6. Final Status & Conclusion
- **Control Plane**: Vercel Preview Ready.
- **Processing Worker**: Local Worker Active & Connected (`127.0.0.1:3000`).
- **Status**: READY FOR PREVIEW TESTING.
