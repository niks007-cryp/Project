# Deployment Environment Matrix — Local AI Clipper

## Runtime Comparison

| Component | Local Dev | GitHub CI | Vercel Preview | Vercel Production |
|-----------|-----------|-----------|----------------|-------------------|
| **Python Version** | 3.11.x | 3.11.x | N/A (thin API) | N/A (thin API) |
| **FFmpeg** | Required (local) | `apt-get install ffmpeg` | ❌ Not available | ❌ Not available |
| **Whisper/ASR** | Local models | Mock ASR only | ❌ Not available | ❌ Not available |
| **GPU/NVENC** | Optional (local) | ❌ Not available | ❌ Not available | ❌ Not available |
| **MediaPipe/CV** | Local | Skipped (CPU mock) | ❌ Not available | ❌ Not available |
| **Local Filesystem** | Full access | Temp only | ❌ Ephemeral | ❌ Ephemeral |
| **Web Server** | Python HTTP | Not started | Vercel runtime | Vercel runtime |
| **BYOK Vault** | DPAPI (Windows) | Not tested | Not applicable | Not applicable |

---

## Environment Variables

| Variable | Local Dev | GitHub CI | Vercel Preview | Vercel Production | Is Secret |
|----------|-----------|-----------|----------------|-------------------|-----------|
| `CLIPPER_ENVIRONMENT` | `development` | `ci` | `preview` | `production` | No |
| `CLIPPER_LOG_LEVEL` | `DEBUG` | `WARNING` | `INFO` | `INFO` | No |
| `GIT_COMMIT_SHA` | Set manually | Set by Actions | Set by Vercel | Set by Vercel | No |
| `CLIPPER_WORKSPACE_DIR` | Local path | Temp/repo dir | ❌ Not set | ❌ Not set | No |
| `CLIPPER_FFMPEG_PATH` | Auto-detect | System PATH | ❌ N/A | ❌ N/A | No |
| `WORKER_API_URL` | N/A (local) | N/A | Optional | Optional | No |
| `WORKER_API_TOKEN` | N/A | N/A | If configured | If configured | YES |

### User BYOK Credentials (NOT deployment secrets)

| Credential | Storage | Deployment |
|-----------|---------|------------|
| Gemini API Key | DPAPI vault (local) | Never in Vercel |
| OpenAI API Key | DPAPI vault (local) | Never in Vercel |
| OpenRouter Key | DPAPI vault (local) | Never in Vercel |

**Rule**: User API keys are entered through the application, stored encrypted locally, never in environment variables or Git.

---

## Processing Capability Matrix

| Capability | Local Mode | CI Mode | Vercel Mode |
|-----------|------------|---------|-------------|
| Video ingestion | ✅ Full | ✅ Mock/FFmpeg | ❌ Not available |
| Transcription (ASR) | ✅ Whisper | ✅ Mock | ❌ Not available |
| Content Intelligence | ✅ Full | ✅ Mock LLM | ❌ Not available |
| Visual Reframing | ✅ Full | ✅ Mock CV | ❌ Not available |
| Video Rendering | ✅ Full FFmpeg | ✅ Mock | ❌ Not available |
| Web Control Panel | ✅ Python HTTP | ✅ (test only) | ✅ Vercel |
| Job Management UI | ✅ Full | ✅ API tests | ✅ (no worker) |
| Provider Config UI | ✅ DPAPI vault | ✅ (tests) | ✅ (no vault) |
| BYOK credential entry | ✅ Full | ✅ (mocked) | ✅ (no vault) |

---

## Known Architecture Gaps

### Gap 1: Vercel ↔ Local Worker Communication
**Status**: Not implemented in Floor 9
**Description**: The Vercel control plane currently has no mechanism to communicate with a local processing worker. This is a future floor concern.
**Workaround**: Local mode is the production processing path.

### Gap 2: DPAPI Vault on Linux/Vercel
**Status**: DPAPI is Windows-only
**Description**: The BYOK credential vault uses Windows DPAPI. On Linux CI, credentials are mocked. On Vercel, there is no vault.
**Workaround**: In Vercel control-plane mode, BYOK configuration would need an alternative encrypted storage strategy (future).

### Gap 3: Large Media Upload Architecture
**Status**: Documented, not implemented
**Description**: Sending production videos through Vercel API routes is not appropriate due to size limits.
**Workaround**: Local mode processes media directly. Cloud upload path is a future floor deliverable.

---

## Floor-by-Floor Environment Compatibility

| Floor | Local | CI | Vercel |
|-------|-------|----|--------|
| 1 — Foundation | ✅ | ✅ | Partial |
| 2 — Media Ingestion | ✅ | ✅ | ❌ (no FFmpeg) |
| 3 — Transcription | ✅ | ✅ Mock | ❌ (no Whisper) |
| 4 — Intelligence | ✅ | ✅ Mock | ❌ (no LLM) |
| 5 — Reframing | ✅ | ✅ Mock | ❌ (no CV) |
| 6 — Rendering | ✅ | ✅ Mock | ❌ (no FFmpeg) |
| 7 — Web Panel | ✅ | ✅ | ✅ (control plane) |
| 8 — Orchestration | ✅ | ✅ Mock | ❌ (no worker) |
| 9 — Deployment | ✅ | ✅ | ✅ (config verified) |
