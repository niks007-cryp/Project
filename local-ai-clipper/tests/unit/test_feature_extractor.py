"""
Unit Tests for Feature Extractor.
"""

from clipper.core.intelligence.feature_extractor import FeatureExtractor
from clipper.domain.models import ClipCandidate, CandidateProvenance


def test_feature_extractor_hook_and_pacing():
    prov = CandidateProvenance(transcript_id="tx_1")
    cand = ClipCandidate(
        candidate_id="cand_test",
        transcript_id="tx_1",
        start_ms=0,
        end_ms=20000,  # 20 sec
        duration_seconds=20.0,
        text="Why is this the secret best method? Here is what you must know.",
        provenance=prov,
    )

    fv = FeatureExtractor.extract_features(cand)
    assert fv.hook_strength > 0.6
    assert fv.curiosity_gap > 0.4
    assert fv.repetition_penalty == 0.0
