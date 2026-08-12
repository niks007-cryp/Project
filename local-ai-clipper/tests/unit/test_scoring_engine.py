"""
Unit Tests for Scoring Engine.
"""

from clipper.core.intelligence.feature_extractor import FeatureExtractor
from clipper.core.intelligence.scoring_engine import ScoringEngine, ScoringWeights
from clipper.domain.models import ClipCandidate, CandidateProvenance


def test_scoring_engine_computation():
    prov = CandidateProvenance(transcript_id="tx_1")
    cand = ClipCandidate(
        candidate_id="cand_score",
        transcript_id="tx_1",
        start_ms=0,
        end_ms=25000,
        duration_seconds=25.0,
        text="Why is this secret method so effective? Discover the truth here.",
        provenance=prov,
    )
    cand.feature_vector = FeatureExtractor.extract_features(cand)

    score = ScoringEngine.calculate_score(cand)
    assert 0.0 <= score.composite_score <= 100.0
    assert score.hook_score > 0.0
    assert score.curiosity_score > 0.0
