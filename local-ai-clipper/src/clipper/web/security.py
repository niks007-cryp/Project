"""
API Security & Input Containment Validator for Floor 7 Local Web Control Panel.
"""

from pathlib import Path
from clipper.core.errors import SecurityError


class APIBoundarySecurityValidator:
    """Validates local API inputs, paths, and commands."""

    @classmethod
    def validate_input_path(cls, path_str: str, allowed_root: Path) -> Path:
        if not path_str:
            raise SecurityError("Input path cannot be empty.")
        path = Path(path_str).resolve()
        if not path.exists():
            raise SecurityError(f"Target path does not exist: {path}")
        return path

    @classmethod
    def validate_job_id(cls, job_id: str):
        if not job_id or not job_id.replace("_", "").replace("-", "").isalnum():
            raise SecurityError("Invalid job_id. Job IDs must contain alphanumeric characters, hyphens, or underscores only.")

    @classmethod
    def validate_provider_name(cls, provider_name: str):
        allowed = ["gemini", "openai", "openrouter", "mock"]
        if provider_name.lower() not in allowed:
            raise SecurityError(f"Provider '{provider_name}' is not in allowed provider list: {allowed}")
