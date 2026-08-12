"""
Unit & Integration Tests for Floor 7 Local REST API & Web Server.
"""

import pytest
import json
import tempfile
from pathlib import Path
from clipper.web.api import LocalClipperAPI
from clipper.web.security import APIBoundarySecurityValidator
from clipper.core.errors import SecurityError


def test_api_health_status():
    api = LocalClipperAPI()
    health = api.get_health_status()
    assert health["status"] in ["HEALTHY", "WARNING"]
    assert "environment" in health
    assert "doctor" in health


def test_api_projects_list():
    api = LocalClipperAPI()
    projects = api.list_projects()
    assert isinstance(projects, list)


def test_api_byok_provider_workflow():
    api = LocalClipperAPI()
    save_res = api.set_provider_credential("gemini", "AIzaTestKey99998888", model_name="gemini-1.5-pro")
    assert save_res["status"] == "SUCCESS"
    assert save_res["api_key_masked"] == "••••••••••••"

    providers = api.list_providers()
    gemini_p = next(p for p in providers if p["provider_name"] == "gemini")
    assert gemini_p["is_configured"] is True
    assert gemini_p["api_key_masked"] != "AIzaTestKey99998888"

    ping_res = api.test_provider_connection("gemini")
    assert ping_res["status"] == "CONNECTED"


def test_api_security_input_validation():
    APIBoundarySecurityValidator.validate_job_id("valid_job_123")
    with pytest.raises(SecurityError):
        APIBoundarySecurityValidator.validate_job_id("../invalid/path;rm")

    with pytest.raises(SecurityError):
        APIBoundarySecurityValidator.validate_provider_name("unauthorized_provider")
