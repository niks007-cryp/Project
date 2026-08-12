"""
Unit Tests for JavaScript Runtime Resolver (yt-dlp challenge solver).
Verifies runtime discovery, version validation, path resolution, arg generation,
missing runtime handling, and YouTube readiness.
"""

import sys
import pytest
from unittest.mock import patch, MagicMock


def test_resolve_node_returns_path_and_version():
    from clipper.infrastructure.js_runtime import resolve_node
    result = resolve_node()
    assert result is not None, "Node.js must be resolvable in this test environment"
    path, version = result
    assert path is not None
    assert "v22" in version or "v20" in version or "v18" in version or version.startswith("v")


def test_resolve_js_runtime_returns_node_tuple():
    from clipper.infrastructure.js_runtime import resolve_js_runtime
    result = resolve_js_runtime()
    assert result is not None, "A JS runtime must be resolvable"
    name, path, version = result
    assert name in ("node", "deno")
    assert path
    assert version


def test_build_ytdlp_runtime_args_non_empty():
    from clipper.infrastructure.js_runtime import build_ytdlp_runtime_args
    args = build_ytdlp_runtime_args()
    assert args, "Runtime args must be non-empty when a runtime is available"
    assert "--js-runtimes" in args
    assert "--remote-components" in args
    assert "ejs:github" in args


def test_build_ytdlp_runtime_args_contains_node_path():
    from clipper.infrastructure.js_runtime import build_ytdlp_runtime_args
    args = build_ytdlp_runtime_args()
    runtime_spec_idx = args.index("--js-runtimes") + 1
    runtime_spec = args[runtime_spec_idx]
    assert ":" in runtime_spec, "Runtime spec must include path separator"
    runtime_name, runtime_path = runtime_spec.split(":", 1)
    assert runtime_name in ("node", "deno")
    assert runtime_path  # Must have a non-empty path


def test_check_youtube_readiness_passes():
    from clipper.infrastructure.js_runtime import check_youtube_readiness
    result = check_youtube_readiness()
    assert result["passed"] is True
    assert result["runtime"] in ("node", "deno")
    assert result["runtime_version"]
    assert result["runtime_path"]


def test_check_youtube_readiness_missing_runtime():
    from clipper.infrastructure.js_runtime import check_youtube_readiness
    # Simulate missing runtime
    with patch("clipper.infrastructure.js_runtime.resolve_js_runtime", return_value=None):
        result = check_youtube_readiness()
    assert result["passed"] is False
    assert "No supported JavaScript runtime" in result["message"]


def test_build_ytdlp_runtime_args_missing_runtime_returns_empty():
    from clipper.infrastructure.js_runtime import build_ytdlp_runtime_args
    with patch("clipper.infrastructure.js_runtime.resolve_js_runtime", return_value=None):
        args = build_ytdlp_runtime_args()
    assert args == []


def test_env_override_takes_priority(tmp_path):
    from clipper.infrastructure import js_runtime
    import os

    fake_node_path = str(tmp_path / "node.exe")

    # Simulate: env override is set AND probe succeeds for this path
    with patch.dict(os.environ, {"CLIPPER_YTDLP_JS_RUNTIME_PATH": fake_node_path}):
        with patch("clipper.infrastructure.js_runtime._probe_executable", return_value="v99.0.0") as mock_probe:
            with patch("os.path.isfile", return_value=True):
                result = js_runtime.resolve_node()

    assert result is not None
    path, version = result
    assert path == fake_node_path
    assert version == "v99.0.0"


def test_50gb_size_policy_preserved():
    """Regression: Ensure the 50 GB YouTube size policy was not removed by JS runtime fix."""
    from clipper.core.ingestion.youtube import download_youtube_video
    import inspect
    sig = inspect.signature(download_youtube_video)
    default_max = sig.parameters["max_size_bytes"].default
    assert default_max == 50 * 1024 * 1024 * 1024


def test_doctor_youtube_js_runtime_check():
    from clipper.infrastructure.doctor import SystemDoctor
    result = SystemDoctor.check_youtube_js_runtime()
    assert result["passed"] is True
    assert result["runtime"] in ("node", "deno")
    assert result["version"]
