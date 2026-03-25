"""Tests for CLI --version and --help flags."""

from __future__ import annotations

import subprocess
import sys


def test_server_version_flag():
    """server.py --version prints version and exits 0."""
    result = subprocess.run(
        [sys.executable, "server.py", "--version"],
        capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert "claude-collaborate" in result.stdout
    # Should contain a semver-like version
    assert "1." in result.stdout


def test_server_version_short_flag():
    """server.py -V prints version and exits 0."""
    result = subprocess.run(
        [sys.executable, "server.py", "-V"],
        capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert "claude-collaborate" in result.stdout


def test_server_help_flag():
    """server.py --help prints usage and exits 0."""
    result = subprocess.run(
        [sys.executable, "server.py", "--help"],
        capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert "Usage" in result.stdout
    assert "--version" in result.stdout


def test_server_help_short_flag():
    """server.py -h prints usage and exits 0."""
    result = subprocess.run(
        [sys.executable, "server.py", "-h"],
        capture_output=True, text=True, timeout=5
    )
    assert result.returncode == 0
    assert "Usage" in result.stdout
