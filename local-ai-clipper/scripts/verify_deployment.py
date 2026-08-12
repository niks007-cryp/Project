"""
Deployment Verification Script for Local AI Clipper.
Verifies that the local deployment configuration is correct.
Can be run locally (--local-only) or against a deployed URL.

Usage:
    python scripts/verify_deployment.py --local-only
    python scripts/verify_deployment.py --url https://your-app.vercel.app
"""

import sys
import json
import argparse
import subprocess
import time
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def check_env_example():
    """Verify .env.example exists with placeholders only."""
    path = project_root / ".env.example"
    if not path.exists():
        return False, ".env.example not found"
    content = path.read_text(encoding="utf-8")
    # Ensure no real-looking keys are present
    import re
    if re.search(r'AIza[0-9A-Za-z\-_]{35}', content):
        return False, ".env.example contains what looks like a real Google API key"
    if re.search(r'sk-[A-Za-z0-9]{48}', content):
        return False, ".env.example contains what looks like a real OpenAI key"
    return True, f".env.example exists ({len(content)} bytes)"


def check_gitignore():
    """Verify .gitignore exists and covers critical patterns."""
    path = project_root / ".gitignore"
    if not path.exists():
        return False, ".gitignore not found"
    content = path.read_text(encoding="utf-8")
    required = [".venv/", ".env", ".vault/", "*.log", "jobs/", "models/"]
    missing = [r for r in required if r not in content]
    if missing:
        return False, f".gitignore missing: {missing}"
    return True, f".gitignore covers {len(required)} required patterns"


def check_no_env_file():
    """Verify .env is not present (should not be committed)."""
    env_path = project_root / ".env"
    if env_path.exists():
        return None, ".env exists locally (expected for development — ensure it is gitignored)"
    return True, ".env not present in repository root"


def check_deployment_docs():
    """Verify required deployment documentation exists."""
    required_docs = [
        "DEPLOYMENT.md",
        "SECURITY.md",
        "RELEASE_PROCESS.md",
        "CONTRIBUTING.md",
        "LICENSE",
        ".env.example",
        ".gitignore",
    ]
    missing = [d for d in required_docs if not (project_root / d).exists()]
    if missing:
        return False, f"Missing deployment documents: {missing}"
    return True, f"All {len(required_docs)} deployment documents present"


def check_github_actions():
    """Verify GitHub Actions CI configuration exists."""
    ci_path = project_root / ".github" / "workflows" / "ci.yml"
    if not ci_path.exists():
        return False, ".github/workflows/ci.yml not found"

    # Basic YAML syntax check
    try:
        import yaml
        with open(ci_path) as f:
            yaml.safe_load(f)
        return True, "CI workflow YAML is valid"
    except ImportError:
        return True, "CI workflow exists (yaml not installed for full validation)"
    except Exception as e:
        return False, f"CI workflow YAML parse error: {e}"


def check_secret_scan():
    """Run secret scan."""
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "scan_secrets.py")],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    if result.returncode == 0:
        return True, "Secret scan passed — 0 secrets detected"
    return False, f"Secret scan failed:\n{result.stdout[-500:]}"


def check_windows_path_scan():
    """Run Windows path scan."""
    result = subprocess.run(
        [sys.executable, str(project_root / "scripts" / "scan_windows_paths.py")],
        capture_output=True,
        text=True,
        cwd=str(project_root),
    )
    if result.returncode == 0:
        return True, "Windows path scan passed"
    return False, f"Windows path scan issues:\n{result.stdout[-500:]}"


def check_local_api_health():
    """Check the local API health endpoint by importing directly."""
    try:
        sys.path.insert(0, str(project_root / "src"))
        from clipper.web.api import LocalClipperAPI
        api = LocalClipperAPI()
        health = api.get_health_status()
        status = health.get("status", "UNKNOWN")
        version = health.get("version", "unknown")
        env = health.get("environment", "unknown")
        return True, f"Health endpoint: status={status}, env={env}, version={version}"
    except Exception as e:
        return False, f"Health endpoint error: {e}"


def check_version_endpoint():
    """Verify the version/build info endpoint."""
    try:
        from clipper import __version__
        from clipper.web.api import LocalClipperAPI
        api = LocalClipperAPI()
        version_info = api.get_version_info()
        return True, f"Version: {version_info.get('version', __version__)}"
    except Exception as e:
        return False, f"Version endpoint error: {e}"


def check_remote_health(url: str):
    """Check remote deployment health endpoint."""
    try:
        import urllib.request
        import urllib.error
        health_url = f"{url.rstrip('/')}/api/health"
        req = urllib.request.Request(health_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            return True, f"Remote health: {data.get('status')} (env={data.get('environment')})"
    except Exception as e:
        return False, f"Remote health check failed: {e}"


def run_local_verification():
    checks = [
        ("Git Ignore",             check_gitignore),
        ("Env Example",            check_env_example),
        ("Deployment Docs",        check_deployment_docs),
        ("GitHub Actions CI",      check_github_actions),
        ("Secret Scan",            check_secret_scan),
        ("Windows Path Scan",      check_windows_path_scan),
        ("Local API Health",       check_local_api_health),
    ]

    print("=" * 58)
    print("      LOCAL AI CLIPPER — DEPLOYMENT VERIFICATION       ")
    print("=" * 58)
    print(f" Mode: LOCAL-ONLY\n")

    all_pass = True
    for name, fn in checks:
        try:
            result, msg = fn()
        except Exception as e:
            result, msg = False, f"Check error: {e}"

        if result is True:
            print(f" [PASS] {name}: {msg}")
        elif result is None:
            print(f" [INFO] {name}: {msg}")
        else:
            print(f" [FAIL] {name}: {msg}")
            all_pass = False

    print()
    if all_pass:
        print(">>> DEPLOYMENT VERIFICATION PASSED <<<")
        print("Configuration is correct for deployment.")
        print("NOTE: Actual Vercel deployment requires user authorization.")
    else:
        print(">>> DEPLOYMENT VERIFICATION FAILED <<<")
        print("Fix the issues above before deploying.")

    return all_pass


def main():
    parser = argparse.ArgumentParser(description="Local AI Clipper Deployment Verifier")
    parser.add_argument("--local-only", action="store_true", help="Run local config checks only")
    parser.add_argument("--url", help="Remote deployment URL to verify")
    args = parser.parse_args()

    if args.url:
        ok = run_local_verification()
        print(f"\nChecking remote: {args.url}")
        remote_ok, msg = check_remote_health(args.url)
        print(f" [{'PASS' if remote_ok else 'FAIL'}] Remote Health: {msg}")
        sys.exit(0 if (ok and remote_ok) else 1)
    else:
        ok = run_local_verification()
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
