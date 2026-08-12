# FLOOR 12 — TASKS.md

## Task List

- [x] Create Floor 12 loop artifacts (`FLOOR_12_LOOP.md`, `FLOOR_12_TASKS.md`, `FLOOR_12_DONE_WHEN.md`, etc.)
- [x] Full Source Audit (Verify dead code, shell=False enforcement, no hardcoded secrets/paths)
- [x] Security Audit (Scan secret patterns in tree & git history, path traversal containment)
- [x] BYOK Final Audit (Verify save, mask `****...XXXX`, connection test, switch, delete, zero leakage)
- [x] Data Privacy & Content Rights Audit (Verify minimal metadata, source file immutability, `CONTENT_RIGHTS_POLICY.md`)
- [x] License & Dependency Audit (Generate `FLOOR_12_LICENSE_AUDIT.md` covering PyPI packages, FFmpeg, MediaPipe, models)
- [x] Reproducibility & Provenance Audit (Verify source hash immutability SHA-256 and manifest provenance tags)
- [x] Failure Taxonomy & Recovery Audit (Verify typed errors: InputError, ValidationError, ResourceError, SystemError)
- [x] Performance Benchmarking (Generate `FLOOR_12_PERFORMANCE.md` with latency breakdowns and RTF metrics)
- [x] Governance & Human Review Audit (Verify AI proposes -> system decides -> human review immutability)
- [x] Create `FLOOR_12_RELEASE_CHECKLIST.md`
- [x] Create `FLOOR_12_DEPLOYMENT_READINESS.md`
- [x] Create `FLOOR_12_INCIDENT_TESTS.md`
- [x] Create `FLOOR_12_FINAL_CERTIFICATION.md`
- [x] Create `FLOOR_12_RELEASE_MANIFEST.md`
- [x] Create `CHANGELOG.md`
- [x] Implement `scripts/verify_floor_12.py` and register `clipper verify-floor 12`
- [x] Execute `clipper verify-floor 12`
- [x] Write `FLOOR_12_WALKTHROUGH.md`
- [x] Read `FLOOR_12_WALKTHROUGH.md` and print it in the final response
