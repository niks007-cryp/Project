# BUILD CONTRACT — LOCAL AI CLIPPER

## 1. Engineering Governance Rules
1. **FLOOR GATE CERTIFICATION:** Progression from Floor N to Floor N+1 strictly requires automated verification via `clipper verify-floor N`.
2. **ZERO APPLICATION CODE IN FLOOR 0:** Floor 0 is reserved strictly for architectural design, governance, data models, technology evaluations, and specifications.
3. **AI DECISION BOUNDARY:** Enforce strict architectural principle: **AI PROPOSES -> SYSTEM VALIDATES -> SYSTEM DECIDES**. LLMs shall never execute commands or control file operations directly.
4. **STRICT PROVIDER ABSTRACTIONS:** AI capabilities (ASR, LLM, Computer Vision) must interact with core business logic exclusively through provider interface abstractions (`ASRProvider`, `AIProvider`, `VisionProvider`).
5. **HUMAN REVIEW REPRODUCIBILITY:** Human overrides are stored as immutable `HumanReview` overlays without mutating raw AI baseline artifacts.
6. **NO RAW SHELL EXECUTION:** Subprocess management must use explicit array parameters (`shell=False`).
7. **AUTOMATED QC GATEWAY:** No output video clip shall be marked published without passing 100% of automated QC assertions.
8. **DATABASE INDEPENDENCE PRINCIPLE:** The core local-first application MUST NOT require an external database (PostgreSQL, MySQL, Redis, ORMs). Job state, pipeline state, provenance, artifact metadata, and processing state operate using the filesystem-based architecture (atomic JSON manifests, typed Pydantic models, state machine, SHA-256 provenance). A database may only be evaluated if an explicit scalability/concurrency requirement demonstrates filesystem insufficiency.
9. **BYOK / USER-CONTROLLED PROVIDER POLICY:** API credentials must be provided by the user through application settings. No API key, bearer token, or secret may be hardcoded in backend code, test fixtures, logs, or manifests.

## 2. Definition of Done (DoD)
A feature or floor is certified "Done" ONLY when:
- Functionally implemented according to specifications.
- Unit and integration tests written and passing.
- Security and threat mitigations verified.
- Performance limits benchmarked.
- Architecture and schema documentation updated.
- Floor verifier script certifies execution with 0 defects.
