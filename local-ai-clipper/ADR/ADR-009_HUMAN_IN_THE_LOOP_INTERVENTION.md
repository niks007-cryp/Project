# ADR-009: Human-in-the-Loop Interventions & Reproducibility Preservation

## Status
Accepted

## Context
Automated AI video clipping requires human review for edge cases (editing timestamp cuts, refining captions, overriding scores). Modifying pipeline outputs directly breaks reproducibility and invalidates audit manifests.

## Decision
All human interventions are captured as **Immutable HumanReview Overlays (`HumanReview`)**, stored separately from raw AI candidate outputs. Re-running the pipeline deterministically re-applies human review overlays.

## Consequences
- **Pros:** Preserves audit trail and 100% reproducibility; allows comparison between pure AI outputs and human-refined outputs.
- **Cons:** Pipeline execution engine must support applying human review overlay layers during rendering.
