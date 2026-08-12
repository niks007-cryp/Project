"""
LLM Provider Abstraction for Content Intelligence Engine.
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    provider_name: str = "mock"  # mock, local_ollama, gemini, openai
    model_name: str = "mock-v1"
    temperature: float = 0.2
    max_tokens: int = 1000
    timeout_seconds: int = 30
    api_key_masked: Optional[str] = None


class LLMEvaluationResult(BaseModel):
    candidate_id: str
    hook_score: float
    curiosity_score: float
    value_score: float
    emotion_score: float
    story_score: float
    hook_summary: str
    reasoning: str
    confidence: float = 0.90
    raw_response_text: Optional[str] = None


class LLMProvider(ABC):
    """Abstract Base Class for LLM Provider implementations."""

    @abstractmethod
    def evaluate_candidate(
        self,
        candidate_id: str,
        candidate_text: str,
        context_text: str,
        config: LLMConfig,
    ) -> LLMEvaluationResult:
        """Evaluates clip candidate using structured LLM analysis."""
        pass
