# ADR-005: State & Metadata Storage (File-Based Manifest vs RDBMS)

## Status
Accepted

## Context
A local-first, portable architecture needs transparent job state tracking without requiring users to install and manage heavy database servers (e.g. PostgreSQL) for baseline CLI operation.

## Decision
We utilize **File-Based JSON Manifests (`job_manifest.json`) using Pydantic serialization** as the primary state store for V1, with SQLite / PostgreSQL adapter hooks designed for optional future scale.

## Consequences
- **Pros:** Completely portable, zero external DB installation, human-readable job debugging.
- **Cons:** High-concurrency writing to a single job manifest requires local file locking.
