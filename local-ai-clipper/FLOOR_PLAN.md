# FLOOR PLAN & STAGED IMPLEMENTATION ROADMAP — LOCAL AI CLIPPER

## Floor 0: Specification + Architecture (CURRENT FLOOR)
- **Goal:** Define system architecture, data models, threat model, governance policies, and design system contracts.
- **Verification:** 100% documentation completion in `N:\local-ai-clipper`; explicit user approval before unlocking Floor 1.

## Floor 1: Engineering Foundation
- **Goal:** Establish directory layout, CLI harness, logging framework, Pydantic schemas, and `clipper verify-floor` verifier.
- **Verification:** Unit tests pass; `clipper verify-floor 1` certification.

## Floor 2: Video Ingestion & Media Validation
- **Goal:** Build FFmpeg probe wrapper, media integrity validation, audio extraction service (PCM WAV 16kHz).
- **Verification:** Media validation integration tests pass; `clipper verify-floor 2` certification.

## Floor 3: Local Transcription Engine
- **Goal:** Integrate local ASR (`faster-whisper`), implement word-level timestamp normalization.
- **Verification:** ASR accuracy and schema verification tests pass; `clipper verify-floor 3` certification.

## Floor 4: Content Intelligence Engine
- **Goal:** Implement candidate boundary detection, prompt scoring contracts, candidate ranking, and deduplication logic.
- **Verification:** Synthetic candidate selection tests pass; `clipper verify-floor 4` certification.

## Floor 5: Captions & Auto Reframing Engine
- **Goal:** Implement computer vision face tracking, 9:16 dynamic crop trajectory math, and ASS animated subtitle generator.
- **Verification:** Vision trajectory math and ASS style generator tests pass; `clipper verify-floor 5` certification.

## Floor 6: Rendering Engine
- **Goal:** Construct FFmpeg filtergraph rendering pipeline with HW/SW encoding support.
- **Verification:** 9:16 video render integration tests pass; `clipper verify-floor 6` certification.

## Floor 7: Quality Control Engine
- **Goal:** Build automated QC checker verifying playability, audio/video sync, frame freezing, and safe zone compliance.
- **Verification:** Automated QC verification tests pass; `clipper verify-floor 7` certification.

## Floor 8: AI Evaluation & Regression System
- **Goal:** Build quantitative evaluation benchmarks for WER, hook scoring precision, and subject framing stability.
- **Verification:** Evaluation benchmark suite passes; `clipper verify-floor 8` certification.

## Floor 9: Governance & Security Audit
- **Goal:** Enforce audit log manifests, provenance recording, secret redaction, and threat mitigations.
- **Verification:** Security audit and threat scenario tests pass; `clipper verify-floor 9` certification.

## Floor 10: Production Operations
- **Goal:** Implement batch orchestration CLI, persistent state engine, system metrics, and operational health checks.
- **Verification:** Full multi-video batch E2E test suite passes; `clipper verify-floor 10` certification.
