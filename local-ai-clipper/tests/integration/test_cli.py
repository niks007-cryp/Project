"""
Integration Tests for CLI Commands.
"""

import sys
from clipper.cli.main import build_parser, cmd_version, cmd_doctor, cmd_verify


def test_cli_parser_subcommands():
    parser = build_parser()
    
    args = parser.parse_args(["version"])
    assert args.command == "version"

    args = parser.parse_args(["doctor"])
    assert args.command == "doctor"

    args = parser.parse_args(["pipeline-status", "job_123"])
    assert args.command == "pipeline-status"
    assert args.job == "job_123"

    args = parser.parse_args(["verify-floor", "1"])
    assert args.command == "verify-floor"
    assert args.floor == 1


def test_cli_version_execution(capsys):
    try:
        cmd_version(None)
    except SystemExit as e:
        assert e.code == 0

    captured = capsys.readouterr()
    assert "Local AI Clipper v" in captured.out
