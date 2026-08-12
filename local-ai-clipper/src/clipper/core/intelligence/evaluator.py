"""
Candidate Ranking Evaluator (Precision@K & NDCG@K) for Local AI Clipper.
"""

import math
from typing import List, Dict, Any
from clipper.domain.models import ClipCandidate


class RankingEvaluator:
    """Calculates Precision@K and NDCG@K ranking evaluation metrics against ground truth."""

    @classmethod
    def calculate_precision_at_k(
        cls, ranked_candidates: List[ClipCandidate], ground_truth_relevance: Dict[str, float], k: int = 3, threshold: float = 2.0
    ) -> float:
        top_k = ranked_candidates[:k]
        if not top_k:
            return 0.0

        relevant_count = 0
        for cand in top_k:
            rel = ground_truth_relevance.get(cand.candidate_id, 0.0)
            if rel >= threshold:
                relevant_count += 1

        return round(relevant_count / len(top_k), 4)

    @classmethod
    def calculate_ndcg_at_k(
        cls, ranked_candidates: List[ClipCandidate], ground_truth_relevance: Dict[str, float], k: int = 3
    ) -> float:
        top_k = ranked_candidates[:k]
        if not top_k:
            return 0.0

        # DCG@K
        dcg = 0.0
        for idx, cand in enumerate(top_k):
            rel = ground_truth_relevance.get(cand.candidate_id, 0.0)
            rank = idx + 1
            dcg += (math.pow(2, rel) - 1.0) / math.log2(rank + 1)

        # Ideal DCG@K (IDCG)
        sorted_ideal = sorted(ground_truth_relevance.values(), reverse=True)[:k]
        idcg = 0.0
        for idx, rel in enumerate(sorted_ideal):
            rank = idx + 1
            idcg += (math.pow(2, rel) - 1.0) / math.log2(rank + 1)

        if idcg == 0.0:
            return 1.0 if dcg == 0.0 else 0.0

        return round(dcg / idcg, 4)

    @classmethod
    def evaluate_ranking(
        cls, ranked_candidates: List[ClipCandidate], ground_truth_relevance: Dict[str, float], k: int = 3
    ) -> Dict[str, Any]:
        p_k = cls.calculate_precision_at_k(ranked_candidates, ground_truth_relevance, k=k)
        ndcg_k = cls.calculate_ndcg_at_k(ranked_candidates, ground_truth_relevance, k=k)

        return {
            "precision_at_k": p_k,
            "ndcg_at_k": ndcg_k,
            "top_k": k,
            "candidate_count": len(ranked_candidates),
        }
