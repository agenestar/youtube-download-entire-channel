"""Tests for cookie validation functionality."""

import pytest
from pathlib import Path
import tempfile

from youtube_channel_downloader.cookie_validator import (
    validate_cookie_file,
    CookieValidationError,
)


def test_validate_cookie_file_success():
    """Test successful cookie file validation."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# Netscape HTTP Cookie File\n")
        f.write(".youtube.com\tTRUE\t/\tTRUE\t0\tcookie_name\tcookie_value\n")
        cookie_path = f.name

    try:
        result = validate_cookie_file(cookie_path)
        assert isinstance(result, Path)
        assert result.exists()
    finally:
        Path(cookie_path).unlink()


def test_validate_cookie_file_not_found():
    """Test validation with non-existent file."""
    with pytest.raises(CookieValidationError, match="Cookie file not found"):
        validate_cookie_file("/nonexistent/path/cookies.txt")


def test_validate_cookie_file_is_directory():
    """Test validation when path is a directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with pytest.raises(CookieValidationError, match="not a file"):
            validate_cookie_file(tmpdir)


def test_validate_cookie_file_empty():
    """Test validation with empty file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        cookie_path = f.name

    try:
        with pytest.raises(CookieValidationError, match="Cookie file is empty"):
            validate_cookie_file(cookie_path)
    finally:
        Path(cookie_path).unlink()


def test_validate_cookie_file_wrong_format():
    """Test validation with non-Netscape format file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("This is not a Netscape cookie file\n")
        cookie_path = f.name

    try:
        with pytest.raises(CookieValidationError, match="not appear to be in Netscape format"):
            validate_cookie_file(cookie_path)
    finally:
        Path(cookie_path).unlink()


def test_validate_cookie_file_binary():
    """Test validation with binary file."""
    with tempfile.NamedTemporaryFile(mode="wb", suffix=".bin", delete=False) as f:
        f.write(b"\x00\x01\x02\x03\x04")
        cookie_path = f.name

    try:
        with pytest.raises(
            CookieValidationError,
            match="(not a valid text file|not appear to be in Netscape format)",
        ):
            validate_cookie_file(cookie_path)
    finally:
        Path(cookie_path).unlink()
