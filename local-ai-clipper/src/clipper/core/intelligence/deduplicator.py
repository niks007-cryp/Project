"""
Deduplication & Overlap Management Engine for Content Intelligence Engine.
"""

import editdistance
import re
from typing import List, Tuple
from clipper.domain.models import ClipCandidate, CandidateStatus


class CandidateDeduplicator:
    """Performs temporal and semantic deduplication on ClipCandidates."""

    @classmethod
    def calculate_temporal_overlap(cls, cand_a: ClipCandidate, cand_b: ClipCandidate) -> float:
        """Calculates temporal Intersection-over-Union (IoU) ratio between two candidates."""
        start_a, end_a = cand_a.start_ms, cand_a.end_ms
        start_b, end_b = cand_b.start_ms, cand_b.end_ms

        intersection = max(0, min(end_a, end_b) - max(start_a, start_b))
        if intersection == 0:
            return 0.0

        union = (end_a - start_a) + (end_b - start_b) - intersection
        return round(intersection / union, 4)

    @classmethod
    def calculate_text_similarity(cls, text_a: str, text_b: str) -> float:
        """Calculates token-based Jaccard similarity between candidate text strings."""
        tokens_a = set(re.findall(r"\w+", text_a.lower()))
        tokens_b = set(re.findall(r"\w+", text_b.lower()))

        if not tokens_a or not tokens_b:
            return 0.0

        intersection = len(tokens_a.intersection(tokens_b))
        union = len(tokens_a.union(tokens_b))
        return round(intersection / union, 4)

    @classmethod
    def deduplicate_candidates(
        cls,
        candidates: List[ClipCandidate],
        max_temporal_overlap: float = 0.40,
        max_semantic_similarity: float = 0.70,
    ) -> List[ClipCandidate]:
        if not candidates:
            return []

        # Sort candidates descending by composite score
        sorted_cands = sorted(candidates, key=lambda c: c.score.composite_score, reverse=True)
        active_candidates: List[ClipCandidate] = []

        for cand in sorted_cands:
            is_dup = False
            for active in active_candidates:
                temp_overlap = cls.calculate_temporal_overlap(cand, active)
                sem_sim = cls.calculate_text_similarity(cand.text, active.text)

                if temp_overlap > max_temporal_overlap or sem_sim > max_semantic_similarity:
                    cand.status = CandidateStatus.DUPLICATE
                    is_dup = True
                    break

            if not is_dup:
                active_candidates.append(cand)

        return active_candidates
