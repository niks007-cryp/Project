# ADR-004: Provider Interface Abstraction

## Status
Accepted

## Context
Tightly coupling business logic to a single AI vendor (e.g. OpenAI or Gemini) creates vendor lock-in and risks breakage if pricing or APIs change.

## Decision
We enforce strict **Provider Abstraction Interfaces (`AIProvider`, `ASRProvider`, `VisionProvider`)**.

## Consequences
- **Pros:** Switching between local Ollama, cloud Gemini, OpenAI, or mock test providers requires zero changes to core pipeline logic.
- **Cons:** Standardizing output formats requires strict schema normalization across diverse provider payloads.
