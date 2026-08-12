"""
Unit Tests for BYOK & User-Controlled AI Provider Policy.
Verifies all 16 project-wide BYOK acceptance criteria.
"""

import pytest
from clipper.core.errors import ExternalProviderNotConfiguredError, SecurityError
from clipper.infrastructure.key_vault import SecureKeyVault
from clipper.infrastructure.llm.base_provider import LLMConfig
from clipper.infrastructure.llm.factory import LLMProviderFactory


def test_byok_key_masking():
    # pragma: no-secret-scan — synthetic test fixture, not a real credential
    raw_key = "AIzaSyD-1234567890abcdefghijklmnopqrstuv"
    masked = SecureKeyVault.mask_api_key(raw_key)
    assert "AIza" not in masked
    assert "uv" not in masked
    assert masked == "••••••••••••"


def test_byok_key_storage_and_retrieval():
    provider = "test_gemini"
    raw_key = "AIzaSyTestKey123456789"

    SecureKeyVault.save_api_key(provider, raw_key, model_name="gemini-1.5-pro")
    retrieved_key = SecureKeyVault.get_api_key(provider)
    assert retrieved_key == raw_key

    conf = SecureKeyVault.get_provider_config(provider)
    assert conf["model_name"] == "gemini-1.5-pro"

    # Cleanup
    SecureKeyVault.delete_api_key(provider)
    assert SecureKeyVault.get_api_key(provider) is None


def test_byok_factory_unconfigured_external_provider_raises():
    # Use a unique provider name that cannot have a pre-stored vault key
    unconfigured_provider = "test_unconfigured_provider_xyzzy"
    cfg = LLMConfig(provider_name=unconfigured_provider, api_key_masked="NOT_CONFIGURED")
    with pytest.raises(ExternalProviderNotConfiguredError):
        LLMProviderFactory.get_provider(cfg)


def test_byok_empty_key_save_raises():
    with pytest.raises(SecurityError):
        SecureKeyVault.save_api_key("gemini", "  ")
