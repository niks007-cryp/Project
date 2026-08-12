# ADR-001: Local ASR Transcription Engine

## Status
Accepted

## Context
Video transcription is a core capability requiring word-level timestamps and speaker identification. Relying exclusively on external APIs (e.g. OpenAI Whisper API) introduces latency, recurring network costs, and privacy exposure of raw media.

## Decision
We select **local-first ASR via `faster-whisper` (CTranslate2 backend)** as the default transcription provider, wrapped behind an `ASRProvider` interface abstraction.

## Consequences
- **Pros:** Zero cloud API costs for ASR; complete privacy of audio data; high throughput using CUDA or quantized CPU execution.
- **Cons:** Host machine must meet RAM/VRAM requirements (4GB-8GB VRAM recommended for large-v3 models).
