# Release Process — Local AI Clipper

## Overview

```
Developer
   ↓
feature/* branch
   ↓
commit (conventional commits)
   ↓
git push origin feature/my-feature
   ↓
Pull Request → main
   ↓
GitHub CI (tests, lint, security, build, floor regression)
   ↓
Vercel Preview Deployment (automatic)
   ↓
Human Code Review
   ↓
PR Approved + CI Green → Merge to main
   ↓
Vercel Production Deployment (automatic from main)
   ↓
Post-deployment smoke test
   ↓
Monitor (logs, health endpoints)
```

---

## 1. Feature Development

```bash
# Checkout from latest main
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/my-feature-name

# Develop with conventional commits
git commit -m "feat(scope): description"
git commit -m "test(scope): add test coverage"
git commit -m "docs: update relevant documentation"
```

---

## 2. Pre-PR Checks (Run Locally)

Before opening a PR, verify:

```bash
# 1. Run full test suite
pytest

# 2. Run floor verifiers for affected floors
clipper verify-floor 8   # (or whichever floors you changed)

# 3. Run secret scanner
python scripts/scan_secrets.py

# 4. Run path scanner
python scripts/scan_windows_paths.py

# 5. Run deployment verification
python scripts/verify_deployment.py --local-only
```

All must pass before the PR is opened.

---

## 3. Pull Request

- Open PR from `feature/*` → `main`
- Fill in the PR template completely
- Assign at least one reviewer
- CI will automatically:
  - Run pytest suite
  - Run floor regression (Floors 1-8)
  - Run secret scan
  - Run dependency audit
  - Validate build
  - Check deployment configuration

---

## 4. CI Gate

PR is **not merge-ready** until:

| Check | Requirement |
|-------|------------|
| Tests | All 97+ tests pass |
| Floor Regression | Floors 1-8 all PASS |
| Secret Scan | 0 secrets detected |
| Dependency Audit | No critical vulnerabilities |
| Build | Package builds successfully |
| Deployment Config | All required files present |

---

## 5. Preview Deployment

Every PR automatically receives a Vercel Preview URL (once Vercel is connected to GitHub).

**Preview rules**:
- Preview uses `preview` environment variables in Vercel
- Preview must NOT share production credentials
- Preview is for review only — not for real user data

---

## 6. Merge to Production

After CI passes and review is approved:

```bash
# Merge via GitHub UI (squash merge recommended for clean history)
# OR merge commit for traceability

# After merge, Vercel automatically deploys the production branch (main)
```

---

## 7. Post-Deployment Verification

After production deployment:

```bash
# Run deployment smoke test
python scripts/verify_deployment.py --url https://your-app.vercel.app

# Verify health endpoint
curl https://your-app.vercel.app/api/health
```

---

## 8. Rollback

### Rollback Vercel Production

1. Go to Vercel dashboard → Project → Deployments
2. Find the last known-good deployment (before the issue)
3. Click the `···` menu → **Redeploy**
4. Vercel redeploys the previous build without code changes

### Rollback Local Installation

```bash
# Find previous working commit
git log --oneline -20

# Checkout previous version
git checkout v0.1.0   # or specific commit SHA

# Re-install
pip install -e ".[dev]"
```

### Emergency Rollback Protocol

If a security-sensitive bug is deployed:
1. Immediately roll back on Vercel (takes ~1 minute)
2. Revoke any affected credentials through the respective provider dashboard
3. Document the incident in `INCIDENT_RESPONSE.md`
4. Fix the issue in a `fix/security-*` branch
5. Fast-track through CI and redeploy

---

## 9. Versioning

Version is set in `src/clipper/__init__.py` and `pyproject.toml`.

Versioning follows [Semantic Versioning](https://semver.org/):

```
MAJOR.MINOR.PATCH

0.1.0 — Initial production release
0.1.1 — Bug fix
0.2.0 — New feature (backwards compatible)
1.0.0 — Production-stable, public API commitment
```

To bump version:
1. Update `__version__` in `src/clipper/__init__.py`
2. Update `version` in `pyproject.toml`
3. Update `FLOOR_PLAN.md` if a new floor is complete
4. Tag the release: `git tag v0.1.1`

---

## 10. Blocked Releases

A release is **blocked** if any of the following are true:

- Any pytest test is failing
- Any floor verifier fails
- A secret has been detected in the repository
- A critical security vulnerability is present in dependencies
- The deployment configuration is invalid
- The deployment smoke test fails

Do NOT deploy broken builds merely because Vercel can build them.
