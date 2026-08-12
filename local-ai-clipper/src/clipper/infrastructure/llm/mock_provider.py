"""
Mock LLM Provider for Testing Content Intelligence Engine.
"""

from clipper.infrastructure.llm.base_provider import LLMProvider, LLMConfig, LLMEvaluationResult


class MockLLMProvider(LLMProvider):
    """Synthetic LLM Provider for fast unit and integration testing."""

    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_text: str,
        context_text: str,
        config: LLMConfig,
    ) -> LLMEvaluationResult:
        # Synthetic deterministic scores based on candidate_text length & keywords
        text_lower = candidate_text.lower()
        has_q = "?" in candidate_text
        has_secret = "secret" in text_lower or "why" in text_lower

        hook = 85.0 if (has_q or has_secret) else 70.0
        curiosity = 80.0 if has_secret else 65.0
        value = 75.0
        emotion = 70.0
        story = 80.0

        return LLMEvaluationResult(
            candidate_id=candidate_id,
            hook_score=hook,
            curiosity_score=curiosity,
            value_score=value,
            emotion_score=emotion,
            story_score=story,
            hook_summary="Engaging opening question with key insights.",
            reasoning="Strong setup and clear payoff for social media clip.",
            confidence=0.92,
            raw_response_text='{"status": "success"}',
        )
