"""
Unit Tests for Configuration System.
"""

import os
import pytest
from pydantic import SecretStr
from clipper.infrastructure.config import load_config, SystemConfig


def test_default_config_loading():
    config = load_config("development")
    assert config.environment == "development"
    assert config.workspace_dir.as_posix().startswith("N:")
    assert config.max_vram_gb == 8.0


def test_env_var_override(monkeypatch):
    monkeypatch.setenv("CLIPPER_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("CLIPPER_MAX_VRAM_GB", "12.5")
    
    config = SystemConfig()
    assert config.log_level == "DEBUG"
    assert config.max_vram_gb == 12.5


def test_secret_masking():
    config = SystemConfig()
    config.ai_provider.api_key = SecretStr("sk-secret-key-123456789")
    
    masked = config.get_masked_dict()
    assert masked["ai_provider"]["api_key"] == "********"
