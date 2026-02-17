"""Validation utilities for Pharos CLI."""

import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from pharos_cli.client.exceptions import ValidationError


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_file_path(path: str) -> Path:
    """Validate and return file path."""
    file_path = Path(path)

    if not file_path.exists():
        raise ValidationError(f"File not found: {path}")

    if not file_path.is_file():
        raise ValidationError(f"Path is not a file: {path}")

    return file_path


def validate_directory_path(path: str) -> Path:
    """Validate and return directory path."""
    dir_path = Path(path)

    if not dir_path.exists():
        raise ValidationError(f"Directory not found: {path}")

    if not dir_path.is_dir():
        raise ValidationError(f"Path is not a directory: {path}")

    return dir_path


def validate_api_key(api_key: str) -> bool:
    """Validate API key format."""
    # Basic validation - API keys are typically long random strings
    if len(api_key) < 8:
        return False

    # Check for obvious invalid patterns
    if api_key.startswith(" ") or api_key.endswith(" "):
        return False

    return True


def validate_language(language: str) -> bool:
    """Validate programming language."""
    valid_languages = {
        "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
        "go", "rust", "ruby", "php", "swift", "kotlin", "scala", "r",
        "julia", "matlab", "perl", "shell", "html", "css", "sql",
        "yaml", "json", "xml", "markdown", "text",
    }
    return language.lower() in valid_languages


def validate_resource_type(resource_type: str) -> bool:
    """Validate resource type."""
    valid_types = {
        "code", "paper", "documentation", "article", "book", "video",
        "audio", "image", "archive", "other",
    }
    return resource_type.lower() in valid_types


def validate_output_format(format_str: str) -> bool:
    """Validate output format."""
    valid_formats = {"json", "table", "tree", "csv", "quiet"}
    return format_str.lower() in valid_formats


def validate_color_option(color_str: str) -> bool:
    """Validate color option."""
    valid_options = {"auto", "always", "never"}
    return color_str.lower() in valid_options


def validate_page(page: int) -> int:
    """Validate page number."""
    if page < 1:
        raise ValidationError(f"Page must be >= 1, got {page}")
    return page


def validate_per_page(per_page: int) -> int:
    """Validate items per page."""
    if per_page < 1 or per_page > 100:
        raise ValidationError("Items per page must be between 1 and 100")
    return per_page


def validate_limit(limit: int, max_limit: int = 1000) -> int:
    """Validate limit value."""
    if limit < 1:
        raise ValidationError(f"Limit must be >= 1, got {limit}")
    if limit > max_limit:
        raise ValidationError(f"Limit must be <= {max_limit}, got {limit}")
    return limit


def validate_weight(weight: float) -> float:
    """Validate weight value (0.0 to 1.0)."""
    if not 0.0 <= weight <= 1.0:
        raise ValidationError(f"Weight must be between 0.0 and 1.0, got {weight}")
    return weight


def validate_quality_score(score: float) -> float:
    """Validate quality score (0.0 to 1.0)."""
    if not 0.0 <= score <= 1.0:
        raise ValidationError(f"Quality score must be between 0.0 and 1.0, got {score}")
    return score