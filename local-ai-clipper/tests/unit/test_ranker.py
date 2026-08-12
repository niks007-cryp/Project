"""
Unit Tests for Candidate Ranker.
"""

from clipper.core.intelligence.ranker import CandidateRanker
from clipper.domain.models import ClipCandidate, ClipScore, CandidateProvenance, CandidateStatus


def test_candidate_ranker_top_k():
    prov = CandidateProvenance(transcript_id="tx_1")
    candidates = [
        ClipCandidate(candidate_id=f"c_{i}", transcript_id="tx_1", start_ms=i*30000, end_ms=(i+1)*30000, duration_seconds=30.0, text=f"Text {i}", score=ClipScore(composite_score=float(i*10)), provenance=prov)
        for i in range(1, 10)
    ]

    ranked = CandidateRanker.rank_candidates(candidates, top_k=3)
    selected = [c for c in ranked if c.is_selected]

    assert len(selected) == 3
    assert selected[0].candidate_id == "c_9"
    assert selected[0].status == CandidateStatus.SELECTED
