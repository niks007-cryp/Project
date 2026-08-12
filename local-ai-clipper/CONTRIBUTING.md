# Contributing to Local AI Clipper

Thank you for your interest in contributing to Local AI Clipper.

---

## Development Setup

### Prerequisites

- Python 3.11 (exactly — see `PYTHON_RUNTIME_STRATEGY.md`)
- FFmpeg and FFprobe (see `DEPLOYMENT.md` for installation)
- Windows (primary development platform) or compatible Linux environment

### Local Setup

```bash
# Clone the repository
git clone https://github.com/<your-org>/local-ai-clipper.git
cd local-ai-clipper

# Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# or: source .venv/bin/activate  # Linux/Mac

# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Copy environment template (fill in your values — never commit .env)
copy .env.example .env

# Verify your setup
clipper doctor
```

---

## Branch Strategy

```
main           — production-ready, protected
feature/*      — individual features
fix/*          — bug fixes
docs/*         — documentation changes
```

### Creating a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/my-feature-name
```

---

## Pull Request Process

1. **Create a feature branch** from `main`
2. **Make your changes** with clear, focused commits
3. **Run the test suite** and ensure all tests pass:
   ```bash
   pytest
   ```
4. **Run the floor verifiers** relevant to your change:
   ```bash
   clipper verify-floor 1
   # ... through the highest floor your change affects
   ```
5. **Check for secrets** — ensure no credentials, API keys, or local paths are committed
6. **Open a Pull Request** against `main`
7. **CI must pass** before merge (tests, lint, security scan, build)
8. **Human review** is required before merge

---

## Commit Messages

Use conventional commit format:

```
type(scope): description

feat(ingestion): add support for MXF container format
fix(transcription): resolve checkpoint race condition on Windows
docs(deployment): add Vercel environment variable reference
test(rendering): add QC engine edge case for zero-duration clips
security(byok): enforce vault encryption for all external provider keys
ci: add dependency audit step to GitHub Actions
```

**Types**: `feat`, `fix`, `docs`, `test`, `refactor`, `perf`, `security`, `ci`, `chore`

---

## Security Rules

**These are non-negotiable:**

- **NEVER** commit API keys, tokens, or credentials
- **NEVER** commit `.env` (only `.env.example` with placeholders)
- **NEVER** add a `NEXT_PUBLIC_*` variable containing a secret
- **NEVER** expose raw API keys in API responses or logs
- **NEVER** commit media files (videos, audio)
- **NEVER** commit model weights

If you accidentally commit a secret, contact the maintainers immediately and follow the incident response procedure in `INCIDENT_RESPONSE.md`.

---

## Code Standards

- **Python 3.11** — do not use features only available in 3.12+
- **Pydantic v2** for all domain models
- **No shell=True** in subprocess calls (security requirement)
- **Structured JSON logging** via the project logger
- **No hardcoded paths** — use `load_config()` for all path resolution
- **No external databases** — filesystem-only, atomic manifests

---

## Testing

- All new features must include unit tests in `tests/unit/`
- Integration changes must include integration tests in `tests/integration/`
- Tests must be deterministic — no network calls, no GPU requirements
- Use `SyntheticMediaGenerator` for test media fixtures

---

## Floor Architecture

The project is organized into numbered Floors (architectural layers):

| Floor | Capability |
| ----- | ---------- |
| 1     | Project Foundation & Infrastructure |
| 2     | Media Ingestion & Validation |
| 3     | Local Transcription Engine |
| 4     | Content Intelligence Engine |
| 5     | Visual Reframing & RenderPlan |
| 6     | Video Rendering & Quality Control |
| 7     | Local Web Control Panel |
| 8     | End-to-End Pipeline Orchestration |
| 9     | Production Deployment & CI/CD |

Changes to a floor require the relevant `verify-floor N` to pass.

---

## Questions?

Open an issue tagged `question` or consult the project documentation in the root directory.
