"""
Scoring Engine for Content Intelligence Engine.
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field
from clipper.domain.models import ClipCandidate, ClipScore, CandidateFeatureVector


class ScoringWeights(BaseModel):
    hook_weight: float = 0.20
    curiosity_weight: float = 0.15
    story_weight: float = 0.15
    value_weight: float = 0.15
    emotion_weight: float = 0.10
    pacing_weight: float = 0.10
    context_weight: float = 0.10
    novelty_weight: float = 0.05


class ScoringEngine:
    """Calculates weighted composite score for ClipCandidates."""

    @classmethod
    def calculate_score(
        cls,
        candidate: ClipCandidate,
        weights: Optional[ScoringWeights] = None,
        ai_score_override: Optional[ClipScore] = None,
    ) -> ClipScore:
        w = weights or ScoringWeights()
        fv = candidate.feature_vector

        # Component scores scaled 0-100
        hook_score = round(fv.hook_strength * 100, 2)
        curiosity_score = round(fv.curiosity_gap * 100, 2)
        story_score = round(fv.story_completeness * 100, 2)
        value_score = round(fv.information_value * 100, 2)
        emotion_score = round(fv.emotional_intensity * 100, 2)
        pacing_score = round(fv.pacing_quality * 100, 2)
        context_score = round(fv.context_independence * 100, 2)
        novelty_score = round(fv.novelty * 100, 2)

        # Layered fusion if AI score provided
        if ai_score_override:
            hook_score = round(0.5 * hook_score + 0.5 * ai_score_override.hook_score, 2)
            curiosity_score = round(0.5 * curiosity_score + 0.5 * ai_score_override.curiosity_score, 2)
            story_score = round(0.5 * story_score + 0.5 * ai_score_override.story_score, 2)
            value_score = round(0.5 * value_score + 0.5 * ai_score_override.value_score, 2)
            emotion_score = round(0.5 * emotion_score + 0.5 * ai_score_override.emotion_score, 2)

        weighted_sum = (
            (hook_score * w.hook_weight)
            + (curiosity_score * w.curiosity_weight)
            + (story_score * w.story_weight)
            + (value_score * w.value_weight)
            + (emotion_score * w.emotion_weight)
            + (pacing_score * w.pacing_weight)
            + (context_score * w.context_weight)
            + (novelty_score * w.novelty_weight)
        )

        penalty = round(fv.repetition_penalty * 25.0, 2)
        composite = max(0.0, round(weighted_sum - penalty, 2))

        return ClipScore(
            composite_score=composite,
            hook_score=hook_score,
            story_score=story_score,
            curiosity_score=curiosity_score,
            value_score=value_score,
            emotion_score=emotion_score,
            pacing_score=pacing_score,
            context_score=context_score,
            novelty_score=novelty_score,
            repetition_penalty=penalty,
            ai_confidence=ai_score_override.ai_confidence if ai_score_override else 1.0,
        )
