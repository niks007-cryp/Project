"""
Unit Tests for Ranking Evaluator (Precision@K & NDCG@K).
"""

from clipper.core.intelligence.evaluator import RankingEvaluator
from clipper.domain.models import ClipCandidate, CandidateProvenance


def test_ranking_evaluator_precision_and_ndcg():
    prov = CandidateProvenance(transcript_id="tx_1")
    c1 = ClipCandidate(candidate_id="c1", transcript_id="tx_1", start_ms=0, end_ms=20000, duration_seconds=20.0, text="C1", provenance=prov)
    c2 = ClipCandidate(candidate_id="c2", transcript_id="tx_1", start_ms=20000, end_ms=40000, duration_seconds=20.0, text="C2", provenance=prov)

    gt_relevance = {"c1": 3.0, "c2": 1.0}
    res = RankingEvaluator.evaluate_ranking([c1, c2], gt_relevance, k=2)

    assert res["precision_at_k"] >= 0.5
    assert res["ndcg_at_k"] > 0.8
