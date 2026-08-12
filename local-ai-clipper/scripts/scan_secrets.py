"""
Secret Scanner — CI Security Check for Local AI Clipper.
Scans source files for common secret patterns.
Fails with exit code 1 if any secrets are detected.
Does NOT print the detected secret value.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

# Directories and files to skip
SKIP_DIRS = {
    ".venv", ".git", "__pycache__", ".pytest_cache",
    ".bin", "node_modules", "dist", "build", "models",
    ".vault", "jobs", "renders",
    "tests",  # Test fixtures use synthetic/fake keys intentionally
}
SKIP_FILES = {
    ".env.example",  # Placeholders only — safe to scan but no real values
    "scan_secrets.py",  # This file itself
    "SECURITY.md",  # Security documentation
}
SKIP_EXTENSIONS = {".pyc", ".pyd", ".so", ".exe", ".dll", ".zip", ".tar"}

# Patterns that indicate a likely hardcoded secret
# Using named groups so we can report the pattern name without the value
SECRET_PATTERNS = [
    # Generic high-entropy API key patterns
    (r'(?i)(api[_\-]?key|apikey)\s*[=:]\s*["\']([A-Za-z0-9+/\-_]{20,})["\']', "api_key"),
    # Gemini / Google AI API keys
    (r'AIza[0-9A-Za-z\-_]{35}', "google_api_key"),
    # OpenAI API keys
    (r'sk-[A-Za-z0-9]{48}', "openai_api_key"),
    # Generic bearer tokens
    (r'(?i)bearer\s+[A-Za-z0-9+/\-_\.]{20,}', "bearer_token"),
    # Hardcoded passwords
    (r'(?i)(password|passwd|secret)\s*[=:]\s*["\'][^"\']{8,}["\']', "hardcoded_password"),
    # Private key header
    (r'-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----', "private_key"),
    # AWS credentials
    (r'AKIA[0-9A-Z]{16}', "aws_access_key"),
    # GitHub tokens
    (r'ghp_[A-Za-z0-9]{36}', "github_token"),
    (r'github_pat_[A-Za-z0-9_]{82}', "github_pat"),
]

# Compile patterns
compiled = [(re.compile(p), name) for p, name in SECRET_PATTERNS]


def should_skip(path: Path) -> bool:
    for part in path.parts:
        if part in SKIP_DIRS:
            return True
    if path.name in SKIP_FILES:
        return True
    if path.suffix in SKIP_EXTENSIONS:
        return True
    return False


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Returns list of (line_number, pattern_name) for hits."""
    hits = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, name in compiled:
                if pattern.search(line):
                    hits.append((lineno, name))
    except Exception:
        pass
    return hits


def main():
    print("=== Secret Scanner ===")
    print(f"Scanning: {project_root}")
    total_hits = 0
    scanned = 0

    for path in project_root.rglob("*"):
        if not path.is_file():
            continue
        if should_skip(path):
            continue
        scanned += 1
        hits = scan_file(path)
        for lineno, name in hits:
            rel = path.relative_to(project_root)
            print(f"  [SECRET DETECTED] {rel}:{lineno} — pattern: {name}")
            total_hits += 1

    print(f"\nScanned {scanned} files.")
    if total_hits == 0:
        print("Secret scan PASSED — 0 secrets detected.")
        sys.exit(0)
    else:
        print(f"Secret scan FAILED — {total_hits} potential secret(s) found.")
        print("Review the files above. Do NOT commit real credentials.")
        sys.exit(1)


if __name__ == "__main__":
    main()
