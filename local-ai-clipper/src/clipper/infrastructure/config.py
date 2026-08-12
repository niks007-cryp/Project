"""
Typed Configuration System for Local AI Clipper.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AIProviderConfig(BaseSettings):
    provider_type: str = "ollama"  # ollama, gemini, openai, local_llm
    api_key: Optional[SecretStr] = None
    endpoint_url: Optional[str] = "http://localhost:11434"
    model_name: str = "qwen2.5:7b-instruct"
    temperature: float = 0.2
    max_tokens: int = 2048


class SystemConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CLIPPER_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    # Profile & Environment
    environment: str = Field(default="development")  # development, test, production
    debug: bool = Field(default=False)

    # Directories
    workspace_dir: Path = Field(default=Path("N:/local-ai-clipper"))
    jobs_dir: Path = Field(default=Path("N:/local-ai-clipper/jobs"))
    renders_dir: Path = Field(default=Path("N:/local-ai-clipper/renders"))
    models_dir: Path = Field(default=Path("N:/local-ai-clipper/models"))

    # Resource Limits
    max_vram_gb: float = Field(default=8.0)
    min_free_disk_gb: float = Field(default=15.0)
    process_timeout_seconds: int = Field(default=1800)

    # Logging
    log_level: str = Field(default="INFO")
    log_json: bool = Field(default=True)

    # AI Provider settings
    ai_provider: AIProviderConfig = Field(default_factory=AIProviderConfig)

    def get_masked_dict(self) -> Dict[str, Any]:
        """Returns a configuration dict with all SecretStr fields masked."""
        data = self.model_dump()
        if "ai_provider" in data and isinstance(data["ai_provider"], dict):
            if data["ai_provider"].get("api_key"):
                data["ai_provider"]["api_key"] = "********"
        return data


def load_config(env_profile: Optional[str] = None) -> SystemConfig:
    """Loads system configuration, optionally applying profile settings."""
    profile = env_profile or os.getenv("CLIPPER_ENVIRONMENT", "development")
    config = SystemConfig(environment=profile)
    
    # Ensure directories exist
    config.jobs_dir.mkdir(parents=True, exist_ok=True)
    config.renders_dir.mkdir(parents=True, exist_ok=True)
    config.models_dir.mkdir(parents=True, exist_ok=True)
    
    return config
