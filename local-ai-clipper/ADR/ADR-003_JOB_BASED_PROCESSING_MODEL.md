# ADR-003: Job-Based Processing Model & Checkpointing

## Status
Accepted

## Context
Long-form video processing is compute-intensive. Systems that process videos as monolithic, un-checkpointed operations lose all progress if a failure occurs at 90%.

## Decision
We implement a **Job-Based State Machine (`job_manifest.json`)** where every processing step is isolated, checkpointed, and idempotent.

## Consequences
- **Pros:** Crashed or interrupted jobs resume instantly from the last valid stage without repeating expensive operations (such as transcription).
- **Cons:** Storage overhead for manifest tracking and temporary stage files (mitigated via garbage collection).
