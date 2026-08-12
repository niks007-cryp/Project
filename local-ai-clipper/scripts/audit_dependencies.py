"""
Dependency Audit & Governance Script for Local AI Clipper.
"""

import sys
import importlib.metadata
from typing import Dict, List


APPROVED_LICENSES = ["MIT", "Apache-2.0", "BSD", "BSD-3-Clause", "PSF", "LGPL-2.1-or-later"]


def audit_installed_packages() -> Dict[str, str]:
    installed = {}
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        if name:
            installed[name.lower()] = dist.version
    return installed


def main():
    print("=== Local AI Clipper Dependency Governance Audit ===")
    packages = audit_installed_packages()
    print(f"Total installed packages in environment: {len(packages)}")
    
    key_deps = ["pydantic", "pydantic-settings", "pytest", "psutil", "colorama", "pyyaml"]
    missing = []
    for dep in key_deps:
        if dep.lower() in packages:
            print(f" [PASS] Dependency '{dep}': v{packages[dep.lower()]}")
        else:
            print(f" [FAIL] Mandatory dependency '{dep}' missing")
            missing.append(dep)

    if missing:
        print(f"\nAudit failed: Missing mandatory dependencies {missing}")
        sys.exit(1)
    
    print("\nDependency Governance Audit: PASSED")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
