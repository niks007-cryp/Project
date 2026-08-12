# Deployment Guide — Local AI Clipper

This document describes how to run, deploy, and operate Local AI Clipper in all supported environments.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│  LOCAL MODE (primary production architecture)           │
│                                                         │
│  Browser → Local Web Control Panel (Python HTTP)        │
│            → Local Pipeline Orchestrator                │
│              → FFmpeg / Whisper / AI Models             │
│                → Local Filesystem (jobs/, renders/)     │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  DEPLOYED CONTROL-PLANE MODE (future)                   │
│                                                         │
│  Browser → Vercel Web Control Plane                     │
│            → Vercel API Layer                           │
│              → Worker Contract API                      │
│                → Local Processing Worker                │
│                  → FFmpeg / Whisper / AI Models         │
└─────────────────────────────────────────────────────────┘
```

**Critical rule**: FFmpeg, Whisper, MediaPipe, and GPU video processing **cannot run on Vercel**. They run on the local processing engine only.

---

## 1. Local Mode Setup

### Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11.x | Exactly 3.11, not 3.12+ |
| FFmpeg | ≥ 5.0 | Must be on PATH or in `.bin/` |
| FFprobe | ≥ 5.0 | Bundled with FFmpeg |
| Windows | 10/11 | Primary development platform |
| RAM | ≥ 8 GB | 16 GB recommended |
| Storage | ≥ 10 GB | For models and render outputs |

### Installation

```powershell
# 1. Clone the repository
git clone https://github.com/<your-org>/local-ai-clipper.git
cd local-ai-clipper

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# 3. Install the application
pip install -e ".[dev]"

# 4. Install FFmpeg
# Option A: System PATH (recommended)
#   Download from https://ffmpeg.org/download.html and add to PATH
#
# Option B: Project .bin/ directory
#   Place ffmpeg.exe and ffprobe.exe in N:\local-ai-clipper\.bin\

# 5. Configure environment
copy .env.example .env
# Edit .env with your settings (NEVER commit this file)

# 6. Verify setup
clipper doctor
```

### Running the Application

```powershell
# Start the local web control panel
clipper ui

# Or run a direct pipeline
clipper run path\to\video.mp4

# Check system status
clipper doctor

# Configure an AI provider (BYOK)
clipper provider set gemini --key YOUR_KEY --model gemini-1.5-pro
```

---

## 2. GitHub Setup

### Repository Configuration

```bash
# Initialize Git (if not already)
git init
git add .
git commit -m "feat: initial project structure"

# Add remote
git remote add origin https://github.com/<your-org>/local-ai-clipper.git

# Push main branch
git push -u origin main
```

### Branch Strategy

```
main           — production branch (Vercel deploys from this)
feature/*      — feature development
fix/*          — bug fixes
```

### Creating a Pull Request

```bash
# Create feature branch
git checkout -b feature/my-feature

# Make changes and commit
git add .
git commit -m "feat(scope): description of change"

# Push and open PR
git push origin feature/my-feature
# → Open PR on GitHub → CI runs → Review → Merge to main
```

**PR Merge Requirements**:
- All CI checks pass (tests, lint, security scan, build)
- No secrets detected
- Human review approved
- Floor verifiers pass for affected floors

---

## 3. Vercel Deployment

### What Deploys to Vercel

**Deploys:** Web Control Plane (UI + thin API)
**Does NOT deploy:** FFmpeg, Whisper, model weights, GPU processing

### Setup Steps

1. **Connect repository to Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import your GitHub repository
   - **Do NOT use automatic deploy** until environment variables are configured

2. **Configure environment variables in Vercel dashboard**:

   | Variable | Purpose | Required |
   |----------|---------|---------|
   | `CLIPPER_ENVIRONMENT` | Set to `production` | Yes |
   | `GIT_COMMIT_SHA` | Auto-populated by Vercel | Auto |

   **Security rule**: NEVER add user API keys (Gemini, OpenAI, etc.) to Vercel environment variables.

3. **Set production branch**: Configure `main` as the production branch in Vercel project settings.

4. **Verify the deployment**:
   ```bash
   python scripts/verify_deployment.py --url https://your-app.vercel.app
   ```

### Vercel Limitations

The following **cannot** run on Vercel without architectural changes:

| Component | Reason | Solution |
|-----------|--------|---------|
| FFmpeg | Binary, large | Local processing engine |
| Whisper/ASR | GPU, large models | Local processing engine |
| Long video processing | Execution time limits | Local processing engine |
| Large file uploads | Request size limits | Direct-to-storage (future) |
| Local filesystem | Ephemeral, no persistence | Filesystem manifests (local only) |

---

## 4. Environment Variables Reference

See `.env.example` for the complete list of configurable variables with descriptions.

**Never** put these in `.env` and commit:
- Real API keys
- Production database credentials
- Signing keys or certificates

---

## 5. FFmpeg / Binary Dependencies

FFmpeg and FFprobe are **not committed to Git**. Install them:

**Windows (local development)**:
1. Download a static build from [gyan.dev/ffmpeg/builds](https://www.gyan.dev/ffmpeg/builds/)
2. Either add to system PATH, or place `ffmpeg.exe`/`ffprobe.exe` in `.bin/`

**Linux/CI (GitHub Actions)**:
```bash
sudo apt-get install -y ffmpeg
```

**macOS**:
```bash
brew install ffmpeg
```

---

## 6. AI Models

Local AI models (Whisper, etc.) are downloaded on first use. They are **not committed to Git**.

Default model cache location: `models/` (gitignored)

Configure ASR model in `.env`:
```
CLIPPER_ASR_MODEL=tiny
```

---

## 7. Rollback

### Local Mode Rollback

```bash
git log --oneline -10
git checkout <previous-commit-sha>
# or
git revert HEAD
```

### Vercel Rollback

1. Go to Vercel dashboard → Deployments
2. Find the last known-good deployment
3. Click "Redeploy" on that deployment
4. No source code edits required

---

## 8. Health Checks

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Application health status |
| `/api/version` | GET | Version and build info |
| `/api/ready` | GET | Web-ready vs Worker-ready distinction |

Health endpoints do NOT expose:
- API keys
- Filesystem paths (in production mode)
- Internal credentials
- Stack traces

---

## 9. Troubleshooting

**FFmpeg not found**:
```bash
clipper doctor  # Will show FFmpeg status
# Fix: install FFmpeg and add to PATH, or place in .bin/
```

**Whisper model not downloaded**:
```bash
# First run will download — may take a few minutes
clipper transcribe video.mp4 --model tiny
```

**Web panel not starting**:
```bash
clipper doctor
clipper ui --port 3001  # Try alternate port
```
