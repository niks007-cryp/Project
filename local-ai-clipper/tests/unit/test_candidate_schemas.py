"""
Unit Tests for ClipCandidate & ClipScore Schemas.
"""

import pytest
from clipper.domain.models import (
    ClipCandidate,
    ClipScore,
    CandidateFeatureVector,
    CandidateProvenance,
    CandidateStatus,
)


def test_clip_candidate_schema_initialization():
    prov = CandidateProvenance(transcript_id="tx_12345")
    candidate = ClipCandidate(
        candidate_id="cand_001",
        transcript_id="tx_12345",
        start_ms=1000,
        end_ms=31000,
        duration_seconds=30.0,
        text="This is a test clip candidate text.",
        provenance=prov,
    )

    assert candidate.candidate_id == "cand_001"
    assert candidate.status == CandidateStatus.PROPOSED
    assert candidate.score.composite_score == 0.0
    assert candidate.feature_vector.hook_strength == 0.5
