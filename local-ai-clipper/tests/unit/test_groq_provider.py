"""
Unit Tests for Groq BYOK LLM Provider Integration.
"""

import pytest
from clipper.core.errors import ExternalServiceError, ExternalProviderNotConfiguredError
from clipper.infrastructure.key_vault import SecureKeyVault
from clipper.infrastructure.llm.base_provider import LLMConfig
from clipper.infrastructure.llm.groq_provider import GroqProvider
from clipper.infrastructure.llm.factory import LLMProviderFactory


def test_groq_provider_initialization():
    provider = GroqProvider(api_key="gsk_test_1234567890abcdef")
    assert provider.BASE_URL == "https://api.groq.com/openai/v1"
    assert provider.raw_api_key == "gsk_test_1234567890abcdef"


def test_groq_default_models():
    models = GroqProvider.DEFAULT_MODELS
    assert "llama-3.1-8b-instant" in models
    assert "llama-3.3-70b-versatile" in models


def test_groq_factory_unconfigured_throws():
    SecureKeyVault.delete_api_key("groq")
    config = LLMConfig(provider_name="groq", model_name="llama-3.1-8b-instant")
    with pytest.raises(ExternalProviderNotConfiguredError):
        LLMProviderFactory.get_provider(config)


def test_groq_factory_configured():
    SecureKeyVault.save_api_key("groq", "gsk_test_sample_key_9999", model_name="llama-3.1-8b-instant")
    config = LLMConfig(provider_name="groq", model_name="llama-3.1-8b-instant")
    provider = LLMProviderFactory.get_provider(config)
    assert isinstance(provider, GroqProvider)
    assert config.api_key_masked is not None
    assert "9999" in config.api_key_masked


def test_groq_evaluation_structure():
    SecureKeyVault.save_api_key("groq", "gsk_test_sample_key_9999", model_name="llama-3.1-8b-instant")
    config = LLMConfig(provider_name="groq", model_name="llama-3.1-8b-instant")
    provider = GroqProvider(api_key="gsk_test_sample_key_9999")

    # Synthetic key throws ExternalProviderNotConfiguredError on live Groq endpoint HTTP 401
    with pytest.raises((ExternalProviderNotConfiguredError, ExternalServiceError)):
        provider.evaluate_candidate(
            candidate_id="cand_001",
            candidate_text="This is a test transcript for viral scoring.",
            context_text="Video context about AI technology.",
            config=config
        )
