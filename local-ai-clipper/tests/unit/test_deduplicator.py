"""
Unit Tests for Candidate Deduplicator.
"""

from clipper.core.intelligence.deduplicator import CandidateDeduplicator
from clipper.domain.models import ClipCandidate, ClipScore, CandidateProvenance, CandidateStatus


def test_deduplicator_temporal_and_semantic():
    prov = CandidateProvenance(transcript_id="tx_1")

    c1 = ClipCandidate(
        candidate_id="c1",
        transcript_id="tx_1",
        start_ms=1000,
        end_ms=30000,
        duration_seconds=29.0,
        text="Why is this secret method so effective? Discover the truth here.",
        score=ClipScore(composite_score=85.0),
        provenance=prov,
    )

    # Substantial temporal overlap with c1 (1000 to 28000)
    c2 = ClipCandidate(
        candidate_id="c2",
        transcript_id="tx_1",
        start_ms=1000,
        end_ms=28000,
        duration_seconds=27.0,
        text="Why is this secret method so effective? Discover the truth here.",
        score=ClipScore(composite_score=70.0),
        provenance=prov,
    )

    # Distinct timestamp (35000 to 60000)
    c3 = ClipCandidate(
        candidate_id="c3",
        transcript_id="tx_1",
        start_ms=35000,
        end_ms=60000,
        duration_seconds=25.0,
        text="Next topic discussion about productivity workflows.",
        score=ClipScore(composite_score=90.0),
        provenance=prov,
    )

    deduped = CandidateDeduplicator.deduplicate_candidates([c1, c2, c3])
    # c3 (90.0) and c1 (85.0) survive; c2 (70.0) marked duplicate
    assert len(deduped) == 2
    ids = [c.candidate_id for c in deduped]
    assert "c3" in ids
    assert "c1" in ids
    assert "c2" not in ids
