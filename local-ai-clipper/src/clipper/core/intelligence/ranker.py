"""
Candidate Ranking Engine for Content Intelligence Engine.
"""

from typing import List
from clipper.domain.models import ClipCandidate, CandidateStatus


class CandidateRanker:
    """Ranks and selects top candidate clips based on composite score."""

    @classmethod
    def rank_candidates(cls, candidates: List[ClipCandidate], top_k: int = 5) -> List[ClipCandidate]:
        if not candidates:
            return []

        # Sort descending by composite_score
        ranked = sorted(candidates, key=lambda c: c.score.composite_score, reverse=True)

        selected_count = 0
        for cand in ranked:
            cand.status = CandidateStatus.RANKED
            if selected_count < top_k:
                cand.is_selected = True
                cand.status = CandidateStatus.SELECTED
                selected_count += 1
            else:
                cand.is_selected = False

        return ranked
