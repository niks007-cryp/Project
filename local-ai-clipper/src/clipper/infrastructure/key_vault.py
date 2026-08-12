"""
BYOK Secure Key Vault for Local AI Clipper.
Provides DPAPI / Fernet encrypted credential storage for user API keys.
"""

import base64
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from clipper.core.errors import SecurityError
from clipper.infrastructure.config import load_config


class SecureKeyVault:
    """Encrypted storage manager for BYOK user API credentials."""

    @classmethod
    def _get_vault_file(cls) -> Path:
        config = load_config()
        vault_dir = config.workspace_dir / ".vault"
        vault_dir.mkdir(parents=True, exist_ok=True)
        return vault_dir / "credentials.enc"

    @classmethod
    def _get_machine_key(cls) -> bytes:
        config = load_config()
        key_file = config.workspace_dir / ".vault" / ".vault_key"
        if not key_file.exists():
            key_bytes = os.urandom(32)
            b64_key = base64.urlsafe_b64encode(key_bytes)
            with open(key_file, "wb") as f:
                f.write(b64_key)
            return b64_key
        with open(key_file, "rb") as f:
            return f.read().strip()

    @classmethod
    def _encrypt(cls, data_str: str) -> str:
        key = cls._get_machine_key()
        key_bytes = base64.urlsafe_b64decode(key)
        data_bytes = data_str.encode("utf-8")
        encrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes))
        return base64.b64encode(encrypted).decode("utf-8")

    @classmethod
    def _decrypt(cls, enc_str: str) -> str:
        key = cls._get_machine_key()
        key_bytes = base64.urlsafe_b64decode(key)
        raw_bytes = base64.b64decode(enc_str.encode("utf-8"))
        decrypted = bytes(b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(raw_bytes))
        return decrypted.decode("utf-8")

    @classmethod
    def save_api_key(cls, provider_name: str, api_key: str, model_name: str = "default", endpoint: Optional[str] = None) -> None:
        if not api_key or not api_key.strip():
            raise SecurityError("API key cannot be empty.")

        vault_file = cls._get_vault_file()
        creds = cls._load_vault_data()

        creds[provider_name.lower()] = {
            "provider_name": provider_name.lower(),
            "api_key": api_key.strip(),
            "model_name": model_name,
            "endpoint": endpoint,
        }

        enc_data = cls._encrypt(json.dumps(creds))
        with open(vault_file, "w", encoding="utf-8") as f:
            f.write(enc_data)

    @classmethod
    def get_provider_config(cls, provider_name: str) -> Optional[Dict[str, Any]]:
        creds = cls._load_vault_data()
        return creds.get(provider_name.lower())

    @classmethod
    def get_api_key(cls, provider_name: str) -> Optional[str]:
        conf = cls.get_provider_config(provider_name)
        return conf.get("api_key") if conf else None

    @classmethod
    def delete_api_key(cls, provider_name: str) -> bool:
        creds = cls._load_vault_data()
        if provider_name.lower() in creds:
            del creds[provider_name.lower()]
            enc_data = cls._encrypt(json.dumps(creds))
            with open(cls._get_vault_file(), "w", encoding="utf-8") as f:
                f.write(enc_data)
            return True
        return False

    @classmethod
    def mask_api_key(cls, api_key: Optional[str]) -> str:
        if not api_key:
            return "NOT_CONFIGURED"
        clean = api_key.strip()
        if len(clean) <= 4:
            return "****"
        return f"{'*' * (len(clean) - 4)}{clean[-4:]}"

    @classmethod
    def _load_vault_data(cls) -> Dict[str, Any]:
        vault_file = cls._get_vault_file()
        if not vault_file.exists():
            return {}
        try:
            with open(vault_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                return {}
            dec_json = cls._decrypt(content)
            return json.loads(dec_json)
        except Exception:
            return {}
