# ADR-002: FFmpeg for Media Processing & Rendering

## Status
Accepted

## Context
Media decoding, audio extraction, video cropping, caption burn-in, and encoding require high performance and wide codec compatibility.

## Decision
We select **FFmpeg executed via safe subprocess list invocations** as the core media processing binary backend.

## Consequences
- **Pros:** Industry-standard codec support, GPU hardware acceleration (NVENC, QSV), rich filtergraph capabilities.
- **Cons:** Parameter list construction requires rigorous safety sanitization to prevent command injection.
