# Changelog — Local AI Clipper

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0-rc.1] - 2026-08-12

### Added
- Floor 12 Final Production Hardening and Certification suite (`scripts/verify_floor_12.py`).
- Comprehensive licensing audit (`FLOOR_12_LICENSE_AUDIT.md`) and model governance documentation.
- Production release manifest and release candidate configuration.

### Security
- Secret scanner automated check ensuring 0 credentials committed across codebase and Git history.
- BYOK masking and DPAPI vault verification.
- Path traversal and subprocess list argument safety audits.

### Fixed
- Pydantic schema alignment across orchestrator and manifest managers.
- Idempotency status updates on pipeline stage checkpoint resume.
