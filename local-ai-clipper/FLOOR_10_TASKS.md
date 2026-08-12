# FLOOR 10 — TASKS.md

## Task List

- [x] Create Floor 10 loop artifacts (`FLOOR_10_LOOP.md`, `FLOOR_10_TASKS.md`, `FLOOR_10_DONE_WHEN.md`, etc.)
- [x] Run mandatory secret audit on working tree and Git history
- [x] Audit environment configuration (.env.example, BYOK key masking)
- [x] Verify local production build and static assets
- [x] Audit client JS bundle for accidental secret exposure (NEXT_PUBLIC_*)
- [x] Run full pytest suite
- [x] Run floor regression suites (Floors 1 through 9)
- [x] Verify Vercel deployment configuration readiness
- [x] Document Vercel preview & production status (Report `NOT DEPLOYED` / `CONFIGURATION VERIFIED` honestly if accounts not connected)
- [x] Verify deployment-safe endpoints (`/api/health`, `/api/version`, `/api/readiness`)
- [x] Create `RELEASE_MANIFEST.md`
- [x] Create `FLOOR_10_DEPLOYMENT_LOG.md`
- [x] Create `FLOOR_10_ROLLBACK_PLAN.md`
- [x] Create `FLOOR_10_SECURITY.md`
- [x] Create `FLOOR_10_EVALUATION.md`
- [x] Implement `scripts/verify_floor_10.py` and register `clipper verify-floor 10`
- [x] Run `clipper verify-floor 10`
- [x] Write `FLOOR_10_WALKTHROUGH.md`
- [x] Read `FLOOR_10_WALKTHROUGH.md` and print it in the final response
