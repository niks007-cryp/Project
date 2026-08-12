## Pull Request Description

<!-- Describe your change clearly and concisely -->

## Type of Change

- [ ] Bug fix (non-breaking)
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Security fix
- [ ] CI/deployment change
- [ ] Refactor

## Floor(s) Affected

- [ ] Floor 1 — Foundation
- [ ] Floor 2 — Media Ingestion
- [ ] Floor 3 — Transcription
- [ ] Floor 4 — Content Intelligence
- [ ] Floor 5 — Visual Reframing
- [ ] Floor 6 — Video Rendering
- [ ] Floor 7 — Web Control Panel
- [ ] Floor 8 — Pipeline Orchestration
- [ ] Floor 9 — Deployment & CI/CD

## Checklist

### Code Quality
- [ ] Tests added or updated for all changes
- [ ] All existing tests pass (`pytest`)
- [ ] Affected floor verifiers pass (`clipper verify-floor N`)
- [ ] No debug code, print statements, or temporary files committed

### Security
- [ ] No API keys, tokens, or credentials committed
- [ ] No `.env` file committed (only `.env.example` with placeholders)
- [ ] No hardcoded Windows paths (`N:\`, `C:\`) in deployment-facing code
- [ ] No `NEXT_PUBLIC_*` variables used for secrets
- [ ] `shell=False` used for all subprocess calls

### Architecture
- [ ] No external database dependencies introduced
- [ ] Filesystem-only job manifest pattern preserved
- [ ] Local processing engine continues to work (`clipper doctor`, `clipper run`)
- [ ] BYOK policy maintained — user controls API keys

### Documentation
- [ ] Relevant documentation updated
- [ ] WALKTHROUGH or EVALUATION document updated if applicable

## Testing Notes

<!-- Describe how you tested this change -->

## Related Issues

<!-- Closes #N -->
