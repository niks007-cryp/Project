# ADR-008: AI Decision Boundary (AI Proposes -> System Validates -> System Decides)

## Status
Accepted

## Context
AI models (LLMs, ASR, Vision) are inherently probabilistic and subject to hallucinations or malformed output formats. Direct trust in AI outputs leads to system failures, illegal command execution, or broken media rendering.

## Decision
Enforce the strict Architectural Boundary: **AI PROPOSES -> SYSTEM VALIDATES -> SYSTEM DECIDES**. LLMs must never directly execute commands or manage files. All model outputs must be validated by Pydantic schemas and bounded by deterministic rules.

## Consequences
- **Pros:** Total system safety and stability; failure of AI model results in deterministic fallback rather than pipeline crash.
- **Cons:** Requires explicit schema validators and fallback handlers for every AI stage.
