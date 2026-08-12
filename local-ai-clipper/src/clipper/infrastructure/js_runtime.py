"""
JavaScript Runtime Resolver for yt-dlp YouTube challenge solving.

Resolves Node.js or Deno executable for use with yt-dlp --js-runtimes.
Uses a priority-ordered search strategy with no hardcoded user paths.

Resolution order:
  1. CLIPPER_YTDLP_JS_RUNTIME_PATH env variable (explicit override)
  2. 'node' / 'deno' via shutil.which (PATH lookup at call time)
  3. Common stable system install directories
  4. Failure with diagnostic message

NEVER logs API keys. Never uses shell=True.
"""

import os
import shutil
import subprocess
from typing import Optional, Tuple
from clipper.infrastructure.logger import get_logger

logger = get_logger("js_runtime")

# Stable system install directories to probe (no user-specific paths)
_NODE_SYSTEM_CANDIDATES = [
    r"C:\Program Files\nodejs\node.exe",
    r"C:\Program Files (x86)\nodejs\node.exe",
    "/usr/local/bin/node",
    "/usr/bin/node",
    "/opt/homebrew/bin/node",
]

_DENO_SYSTEM_CANDIDATES = [
    "/usr/local/bin/deno",
    "/usr/bin/deno",
    "/opt/homebrew/bin/deno",
]


def _probe_executable(exe_path: str, version_flag: str = "--version") -> Optional[str]:
    """Returns the version string if executable runs successfully, else None."""
    try:
        r = subprocess.run(
            [exe_path, version_flag],
            capture_output=True,
            text=True,
            timeout=8,
        )
        if r.returncode == 0:
            return r.stdout.strip().splitlines()[0]
    except (FileNotFoundError, subprocess.TimeoutExpired, PermissionError):
        pass
    return None


def resolve_node() -> Optional[Tuple[str, str]]:
    """
    Finds a working Node.js executable.
    Returns (absolute_path, version_string) or None.
    Priority order:
      1. CLIPPER_YTDLP_JS_RUNTIME_PATH env variable (explicit override)
      2. Stable system install directories (not session-scoped)
      3. PATH lookup via shutil.which (may be session-scoped in some shells)
    """
    # 1. Explicit override
    override = os.environ.get("CLIPPER_YTDLP_JS_RUNTIME_PATH")
    if override and os.path.isfile(override):
        ver = _probe_executable(override)
        if ver:
            logger.info(f"JS runtime (node) resolved from env override: {override} ({ver})")
            return override, ver

    # 2. Stable system install directories (not session-scoped, safe across restarts)
    for candidate in _NODE_SYSTEM_CANDIDATES:
        if os.path.isfile(candidate):
            ver = _probe_executable(candidate)
            if ver:
                logger.info(f"JS runtime (node) resolved from system dir: {candidate} ({ver})")
                return candidate, ver

    # 3. PATH lookup via shutil.which (may be session-scoped in fnm/nvm shells)
    which_node = shutil.which("node")
    if which_node:
        ver = _probe_executable(which_node)
        if ver:
            logger.info(f"JS runtime (node) resolved via PATH: {which_node} ({ver})")
            return which_node, ver

    logger.warning("JS runtime (node) not found. YouTube extraction may fail.")
    return None


def resolve_deno() -> Optional[Tuple[str, str]]:
    """
    Finds a working Deno executable.
    Returns (absolute_path, version_string) or None.
    """
    override = os.environ.get("CLIPPER_YTDLP_JS_RUNTIME_PATH")
    if override and "deno" in override.lower() and os.path.isfile(override):
        ver = _probe_executable(override)
        if ver:
            return override, ver

    which_deno = shutil.which("deno")
    if which_deno:
        ver = _probe_executable(which_deno)
        if ver:
            logger.info(f"JS runtime (deno) resolved via PATH: {which_deno} ({ver})")
            return which_deno, ver

    for candidate in _DENO_SYSTEM_CANDIDATES:
        if os.path.isfile(candidate):
            ver = _probe_executable(candidate)
            if ver:
                logger.info(f"JS runtime (deno) resolved from system dir: {candidate} ({ver})")
                return candidate, ver

    return None


def resolve_js_runtime() -> Optional[Tuple[str, str, str]]:
    """
    Resolves the best available JS runtime for yt-dlp.
    Prefers Deno, falls back to Node.
    Returns (runtime_name, absolute_path, version_string) or None.
    """
    deno = resolve_deno()
    if deno:
        return ("deno", deno[0], deno[1])

    node = resolve_node()
    if node:
        return ("node", node[0], node[1])

    return None


def build_ytdlp_runtime_args() -> list:
    """
    Returns the yt-dlp argument list fragment for the JS runtime and EJS component.
    E.g.: ['--js-runtimes', 'node:/path/to/node.exe', '--remote-components', 'ejs:github']

    Returns empty list if no runtime is found (caller decides how to handle).
    """
    runtime = resolve_js_runtime()
    if not runtime:
        return []

    name, path, version = runtime
    runtime_spec = f"{name}:{path}"
    args = ["--js-runtimes", runtime_spec, "--remote-components", "ejs:github"]
    logger.info(f"yt-dlp JS runtime args: {args[:2]} (version: {version})")
    return args


def check_youtube_readiness() -> dict:
    """
    Full diagnostic check for YouTube acquisition readiness.
    Returns a dict with passed/failed keys suitable for SystemDoctor.
    """
    result = {
        "passed": False,
        "runtime": None,
        "runtime_version": None,
        "runtime_path": None,
        "message": "No supported JavaScript runtime detected.",
    }

    runtime = resolve_js_runtime()
    if runtime:
        name, path, version = runtime
        result["passed"] = True
        result["runtime"] = name
        result["runtime_version"] = version
        result["runtime_path"] = path
        result["message"] = f"JavaScript runtime ready: {name} {version}"

    return result
