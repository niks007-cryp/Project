"""
Unit Tests for Subprocess Safety & Security Isolation.
"""

import pytest
from pathlib import Path
from clipper.infrastructure.security import (
    SafeSubprocess,
    validate_path_containment,
    SafeTempDir,
)
from clipper.core.errors import SecurityError


def test_safe_subprocess_prohibits_non_list_cmd():
    with pytest.raises(SecurityError):
        SafeSubprocess.run("echo hello")  # String instead of list prohibited


def test_safe_subprocess_successful_execution():
    res = SafeSubprocess.run(["python", "-c", "print('hello_security')"])
    assert res.returncode == 0
    assert "hello_security" in res.stdout


def test_path_traversal_prevention(temp_job_dir):
    allowed_parent = temp_job_dir
    valid_sub_path = allowed_parent / "subfolder" / "file.txt"
    
    # Valid child path passes
    resolved = validate_path_containment(valid_sub_path, allowed_parent)
    assert resolved is not None

    # Path traversal outside allowed parent raises SecurityError
    traversal_path = allowed_parent / ".." / ".." / "system.txt"
    with pytest.raises(SecurityError):
        validate_path_containment(traversal_path, allowed_parent)


def test_safe_temp_dir_cleanup(temp_job_dir):
    with SafeTempDir(parent_dir=temp_job_dir) as tmp_path:
        assert tmp_path.exists()
        test_file = tmp_path / "test.txt"
        test_file.write_text("sample")
        assert test_file.exists()

    # Directory automatically removed on exit
    assert not tmp_path.exists()
