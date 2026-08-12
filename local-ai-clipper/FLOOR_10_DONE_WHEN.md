# FLOOR 10 — DONE_WHEN.md

Floor 10 is certified COMPLETE when:

1. [x] Secret Audit: Working tree and repository history pass secret scanning with 0 detected production credentials.
2. [x] Local Build & Bundle Audit: Local production build passes, client assets contain 0 exposed secrets or NEXT_PUBLIC_* credentials.
3. [x] Local Regressions: Pytest suite (97/97) passes and all floor verifiers (Floors 1-9) pass.
4. [x] Worker Boundary: Web Control Plane API endpoints (`/api/health`, `/api/version`, `/api/readiness`) remain decoupled from heavy local video processing.
5. [x] Deployment Documentation: `RELEASE_MANIFEST.md`, `FLOOR_10_DEPLOYMENT_LOG.md`, `FLOOR_10_ROLLBACK_PLAN.md`, `FLOOR_10_SECURITY.md`, and `FLOOR_10_EVALUATION.md` are created.
6. [x] Honest Status Reporting: Deployment statuses (Vercel Preview/Production) are reported as `NOT DEPLOYED` / `CONFIGURATION VERIFIED` without fabrication.
7. [x] Floor 10 Verifier: `clipper verify-floor 10` executes and passes cleanly.
8. [x] Walkthrough: `FLOOR_10_WALKTHROUGH.md` is written, read, and printed in the final response with the required status block.
