# FLOOR 9 — DONE_WHEN.md

Floor 9 is complete ONLY when ALL of the following are TRUE:

## Git Repository
- [ ] .gitignore is comprehensive and secure
- [ ] .env.example exists with placeholders only
- [ ] No secrets tracked in Git
- [ ] No large media tracked
- [ ] LICENSE exists
- [ ] CONTRIBUTING.md exists
- [ ] SECURITY.md exists
- [ ] README.md is production-ready

## CI/CD
- [ ] .github/workflows/ci.yml created and valid YAML
- [ ] Tests run in CI
- [ ] Lint/type check runs in CI
- [ ] Security scan runs in CI
- [ ] Floor regression verification runs in CI (CPU-safe mode)
- [ ] Build validation runs in CI

## Vercel Deployment
- [ ] vercel.json validated (or documented as not needed)
- [ ] Production build works locally
- [ ] No localhost assumptions in deployment code
- [ ] No Windows paths in deployment code
- [ ] Health endpoint (/api/health) responds correctly
- [ ] Version endpoint (/api/version) works
- [ ] No secrets exposed to client JavaScript
- [ ] BYOK remains user-controlled (not in deployment config)
- [ ] Deployment environment variables documented

## Worker Boundary
- [ ] Worker contract interface defined
- [ ] Local processing engine continues to work (clipper run, clipper doctor)
- [ ] Deployment code does not assume N:\ exists
- [ ] Web vs Worker readiness distinguished

## Security
- [ ] Secret scanning completed — 0 secrets in tracked files
- [ ] Dependency audit run
- [ ] Error sanitization verified for production endpoints
- [ ] Security headers documented

## Documentation
- [ ] DEPLOYMENT.md created
- [ ] RELEASE_PROCESS.md created
- [ ] DEPLOYMENT_READINESS.md created
- [ ] DEPLOYMENT_ENVIRONMENT_MATRIX.md created

## Regression
- [ ] Floor 1: PASS
- [ ] Floor 2: PASS
- [ ] Floor 3: PASS
- [ ] Floor 4: PASS
- [ ] Floor 5: PASS
- [ ] Floor 6: PASS
- [ ] Floor 7: PASS
- [ ] Floor 8: PASS

## Final
- [ ] verify_floor_9.py PASS
- [ ] Full pytest suite PASS
- [ ] FLOOR_9_WALKTHROUGH.md written and printed
- [ ] No fabricated deployment results
- [ ] STOP — Human review gate enforced
