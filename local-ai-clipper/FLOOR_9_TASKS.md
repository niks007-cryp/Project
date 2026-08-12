# FLOOR 9 — TASKS.md

## Status Legend
- `[ ]` Not started
- `[/]` In progress
- `[x]` Complete

---

## Phase 1: Audit & Inspection
- [x] Read project structure
- [x] Scan for hardcoded paths (N:\, C:\, D:\, 127.0.0.1, localhost)
- [x] Check for existing .gitignore, .env, .env.example, LICENSE, SECURITY.md, .github
- [x] Read pyproject.toml, web stack
- [x] Identify what belongs on Vercel vs local worker

## Phase 2: Git Repository Hygiene
- [ ] Create .gitignore (comprehensive)
- [ ] Create .env.example (placeholders only, no secrets)
- [ ] Create LICENSE (MIT or appropriate)
- [ ] Verify README.md is production-ready
- [ ] Create CONTRIBUTING.md
- [ ] Create SECURITY.md
- [ ] Run git status audit

## Phase 3: CI/CD — GitHub Actions
- [ ] Create .github/workflows/ci.yml (Python tests, lint, security, build)
- [ ] Create .github/workflows/deployment-check.yml (vercel build validation)
- [ ] Create .github/PULL_REQUEST_TEMPLATE.md
- [ ] Add floor regression gates (verify-floor 1-8, CI-safe mode)

## Phase 4: Vercel Deployment Architecture
- [ ] Determine what deploys to Vercel (Web Control Panel + thin API)
- [ ] Create vercel.json if needed
- [ ] Create web/app deployment target (Next.js thin frontend OR static + serverless functions)
- [ ] Create /api/health endpoint (deployment-safe)
- [ ] Create /api/ready endpoint (web vs worker distinction)
- [ ] Create /api/version endpoint
- [ ] Create /api/worker/capabilities endpoint
- [ ] Remove localhost assumptions from deployment-facing code
- [ ] Verify no Windows paths in deployment code
- [ ] Test production build locally

## Phase 5: Environment Configuration
- [ ] Create deployment environment configuration (dev/preview/production)
- [ ] Create DEPLOYMENT_ENVIRONMENT_MATRIX.md
- [ ] Verify BYOK never enters client bundle
- [ ] Verify no NEXT_PUBLIC_*_KEY patterns for secrets

## Phase 6: Worker Boundary
- [ ] Define worker contract interface
- [ ] Document media upload architecture (not through Vercel functions)
- [ ] Document worker capabilities schema

## Phase 7: Security
- [ ] Secret scanning check (grep for common key patterns)
- [ ] Dependency audit (pip audit or safety)
- [ ] Security headers documented for Vercel deployment
- [ ] Error sanitization verified
- [ ] Verify no API keys tracked

## Phase 8: Documentation
- [ ] Create DEPLOYMENT.md (local, GitHub, Vercel)
- [ ] Create RELEASE_PROCESS.md
- [ ] Create DEPLOYMENT_READINESS.md (matrix)
- [ ] Update README.md with deployment section

## Phase 9: Verification
- [ ] Create scripts/verify_floor_9.py
- [ ] Register verify-floor 9 in CLI
- [ ] Run verify_floor_9.py
- [ ] Run Floors 1-8 regression

## Phase 10: Walkthrough
- [ ] Write FLOOR_9_WALKTHROUGH.md
- [ ] Print walkthrough in final response
- [ ] STOP
