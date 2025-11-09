"""Cookie validation utilities for YouTube Premium authentication."""

from pathlib import Path
from typing import Optional


class CookieValidationError(Exception):
    """Raised when cookie file validation fails."""

    pass


def validate_cookie_file(cookie_path: str) -> Path:
    """
    Validate that the cookie file exists and is readable.

    Args:
        cookie_path: Path to the Netscape format cookie file

    Returns:
        Path object to the validated cookie file

    Raises:
        CookieValidationError: If the cookie file is invalid or inaccessible
    """
    path = Path(cookie_path)

    if not path.exists():
        raise CookieValidationError(f"Cookie file not found: {cookie_path}")

    if not path.is_file():
        raise CookieValidationError(f"Cookie path is not a file: {cookie_path}")

    if not path.stat().st_size > 0:
        raise CookieValidationError(f"Cookie file is empty: {cookie_path}")

    # Check if file is readable
    try:
        with open(path, "r") as f:
            first_line = f.readline().strip()
            # Netscape cookie files should start with a comment
            if not first_line.startswith("#"):
                raise CookieValidationError(
                    f"Cookie file does not appear to be in Netscape format: {cookie_path}"
                )
    except PermissionError:
        raise CookieValidationError(f"Cookie file is not readable: {cookie_path}")
    except UnicodeDecodeError:
        raise CookieValidationError(f"Cookie file is not a valid text file: {cookie_path}")

    return path
