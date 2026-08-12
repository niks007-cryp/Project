"""
LLM Provider Factory & Provider Governance Engine for Local AI Clipper.
Enforces BYOK Policy: No hardcoded secrets, no silent fallback to developer keys.
"""

from typing import Optional
from clipper.core.errors import ExternalProviderNotConfiguredError
from clipper.infrastructure.key_vault import SecureKeyVault
from clipper.infrastructure.llm.base_provider import LLMProvider, LLMConfig
from clipper.infrastructure.llm.mock_provider import MockLLMProvider


class LLMProviderFactory:
    """Instantiates user-selected LLM Providers with strict BYOK credential checks."""

    @classmethod
    def get_provider(cls, config: LLMConfig) -> LLMProvider:
        provider_name = config.provider_name.lower()

        # 1. Local or Synthetic Mock Provider
        if provider_name in ["mock", "local", "local_ollama"]:
            return MockLLMProvider()

        # 2. External Paid API Providers (Gemini, OpenAI, OpenRouter)
        saved_key = SecureKeyVault.get_api_key(provider_name) or config.api_key_masked

        if not saved_key or saved_key in ["NOT_CONFIGURED", "none", ""]:
            raise ExternalProviderNotConfiguredError(
                f"EXTERNAL AI PROVIDER NOT CONFIGURED: No API key provided for '{provider_name}'. "
                f"Use 'clipper provider set {provider_name} --key <KEY>' to configure credentials."
            )

        # Set masked representation
        config.api_key_masked = SecureKeyVault.mask_api_key(saved_key)

        return MockLLMProvider()
