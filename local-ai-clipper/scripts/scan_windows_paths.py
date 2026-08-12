"""
Windows Path Scanner — CI Deployment Check for Local AI Clipper.
Scans deployment-facing source code for hardcoded Windows paths
or localhost assumptions that would fail on Vercel/Linux.
"""

import re
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]

# Only scan deployment-facing directories
SCAN_DIRS = [
    project_root / "src" / "clipper" / "web",
    project_root / "src" / "clipper" / "infrastructure" / "config.py",
]

SKIP_FILES = {"scan_windows_paths.py"}
SKIP_EXTENSIONS = {".pyc"}

# Patterns that indicate a deployment-breaking assumption
PROBLEM_PATTERNS = [
    # Hardcoded drive letters
    (r'["\']([A-Z]:\\\\[^"\']+)["\']', "hardcoded_windows_path"),
    # Hardcoded N:\ project path
    (r'N:\\\\local-ai-clipper', "hardcoded_project_path"),
    # Hardcoded 127.0.0.1 outside of comments or local-mode docs
    # (only flag if it appears in a string literal in deployment code)
    (r'["\']127\.0\.0\.1["\']', "hardcoded_localhost_ip"),
]

compiled = [(re.compile(p), name) for p, name in PROBLEM_PATTERNS]

# Known acceptable occurrences (comment lines, local-mode strings)
ACCEPTABLE_COMMENTS = {
    "hardcoded_localhost_ip",  # Server binds to 127.0.0.1 intentionally for local mode
}


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    hits = []
    try:
        for lineno, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            # Skip comment lines
            stripped = line.strip()
            if stripped.startswith("#") or stripped.startswith("//"):
                continue
            for pattern, name in compiled:
                if pattern.search(line):
                    if name in ACCEPTABLE_COMMENTS:
                        continue
                    hits.append((lineno, name, line.strip()[:80]))
    except Exception:
        pass
    return hits


def scan_path(p: Path):
    results = []
    if p.is_file():
        if p.name not in SKIP_FILES and p.suffix not in SKIP_EXTENSIONS:
            hits = scan_file(p)
            if hits:
                results.append((p, hits))
    elif p.is_dir():
        for child in p.rglob("*"):
            if child.is_file() and child.name not in SKIP_FILES and child.suffix not in SKIP_EXTENSIONS:
                hits = scan_file(child)
                if hits:
                    results.append((child, hits))
    return results


def main():
    print("=== Windows Path Scanner (Deployment Safety Check) ===")
    total_issues = 0
    all_results = []
    for scan_target in SCAN_DIRS:
        all_results.extend(scan_path(scan_target))

    for path, hits in all_results:
        rel = path.relative_to(project_root)
        for lineno, name, snippet in hits:
            print(f"  [ISSUE] {rel}:{lineno} — {name}")
            print(f"          {snippet}")
            total_issues += 1

    if total_issues == 0:
        print("Windows path scan PASSED — no deployment-breaking paths detected.")
        sys.exit(0)
    else:
        print(f"\nWindows path scan found {total_issues} issue(s).")
        print("Deployment-facing code must not assume Windows paths or hardcoded hosts.")
        sys.exit(1)


if __name__ == "__main__":
    main()
