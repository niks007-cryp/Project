# Local AI Clipper

Local AI Clipper is a production-ready, local-first automated AI video clipping platform engineered to convert long-form videos into high-value vertical short-form content.

## Architectural Highlights
- **Local-First Processing:** Compute-heavy tasks (audio extraction, ASR transcription, CV reframing, rendering) run entirely locally.
- **Provider Abstraction:** AI capabilities (ASR, LLM, Computer Vision) are decoupled behind interface abstractions.
- **AI Decision Boundary:** Strict enforcement of `AI PROPOSES -> SYSTEM VALIDATES -> SYSTEM DECIDES`.
- **Reproducibility & Provenance:** 100% output traceability to source hash, model version, prompt version, and config version.
- **Floor-Gated Development:** Strict certification gates (`clipper verify-floor <N>`) enforce quality, testing, security, and governance before proceeding to higher development floors.

## Current State: Floor 0 (Specification & Architecture)
Application implementation HAS NOT BEGUN. Floor 0 establishes the engineering contracts, data schemas, security threat models, and architectural specifications located in this repository:

### Core Architecture & Strategy Documents
- [PROJECT_SCOPE.md](PROJECT_SCOPE.md)
- [REQUIREMENTS.md](REQUIREMENTS.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [SYSTEM_FLOWS.md](SYSTEM_FLOWS.md)
- [TECHNOLOGY_DECISIONS.md](TECHNOLOGY_DECISIONS.md)
- [DATA_MODEL.md](DATA_MODEL.md)
- [DATA_FLOW.md](DATA_FLOW.md)
- [PIPELINE_CONTRACTS.md](PIPELINE_CONTRACTS.md)
- [HUMAN_REVIEW.md](HUMAN_REVIEW.md)
- [FEEDBACK_ARCHITECTURE.md](FEEDBACK_ARCHITECTURE.md)
- [THREAT_MODEL.md](THREAT_MODEL.md)
- [SECURITY_REQUIREMENTS.md](SECURITY_REQUIREMENTS.md)
- [GOVERNANCE.md](GOVERNANCE.md)
- [CONTENT_RIGHTS_POLICY.md](CONTENT_RIGHTS_POLICY.md)
- [DATA_POLICY.md](DATA_POLICY.md)
- [MODEL_INVENTORY.md](MODEL_INVENTORY.md)
- [LICENSE_INVENTORY.md](LICENSE_INVENTORY.md)
- [DESIGN_SYSTEM.md](DESIGN_SYSTEM.md)
- [TESTING_STRATEGY.md](TESTING_STRATEGY.md)
- [EVALUATION_STRATEGY.md](EVALUATION_STRATEGY.md)
- [PYTHON_RUNTIME_STRATEGY.md](PYTHON_RUNTIME_STRATEGY.md)
- [REPRODUCIBILITY.md](REPRODUCIBILITY.md)
- [OBSERVABILITY.md](OBSERVABILITY.md)
- [OPERATIONS.md](OPERATIONS.md)
- [INCIDENT_RESPONSE.md](INCIDENT_RESPONSE.md)
- [BUILD_CONTRACT.md](BUILD_CONTRACT.md)
- [FLOOR_PLAN.md](FLOOR_PLAN.md)
- [OPEN_QUESTIONS.md](OPEN_QUESTIONS.md)
- [ADR/](ADR/) (Architecture Decision Records 001 - 009)
