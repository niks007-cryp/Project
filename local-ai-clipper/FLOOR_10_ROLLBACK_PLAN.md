# FLOOR 10 — ROLLBACK PLAN & EMERGENCY PROTOCOL

## 1. Rollback Targets & Triggers

- **Triggers for Rollback**:
  - High error rates on health/readiness endpoints (`/api/health`).
  - Secret leakage or BYOK isolation breach.
  - Unexpected worker boundary failure or crash loop.

## 2. Vercel Control-Plane Rollback
1. Access Vercel Dashboard → Deployments.
2. Locate the previous known-good deployment (e.g., commit tagged `v0.1.0-certified`).
3. Click `···` → **Redeploy**.
4. Confirm health status via `curl https://<vercel-deployment-url>/api/health`.

## 3. Local Engine Rollback
```bash
# Revert working directory to last certified git tag/commit
git checkout main
git reset --hard HEAD~1

# Verify local engine integrity
clipper doctor
clipper verify-floor 9
```

## 4. Post-Rollback Verification Checklist
- [ ] `/api/health` returns `status: HEALTHY` / `WARNING` with no path leaks.
- [ ] Pytest suite passes (97/97 tests).
- [ ] Local pipeline execution (`clipper run`) functions cleanly.
