"""Helper utilities for Pharos CLI."""

import math
from typing import Any


def format_number(n: int) -> str:
    """Format number with thousand separators."""
    return f"{n:,}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 0.001:
        return f"{seconds * 1000000:.0f}μs"
    elif seconds < 1:
        return f"{seconds * 1000:.0f}ms"
    elif seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m"


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to max length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_percentage(value: float, decimals: int = 1) -> str:
    """Format value as percentage."""
    return f"{value * 100:.{decimals}f}%"


def format_score(score: float) -> str:
    """Format quality score with color indicator."""
    if score >= 0.8:
        return f"[green]{score:.2f}[/green]"
    elif score >= 0.5:
        return f"[yellow]{score:.2f}[/yellow]"
    else:
        return f"[red]{score:.2f}[/red]"


def format_bytes(size: int) -> str:
    """Format bytes in human-readable format."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def format_count(count: int, singular: str, plural: str = None) -> str:
    """Format count with singular/plural."""
    if plural is None:
        plural = singular + "s"
    return f"{count} {singular if count == 1 else plural}"


def safe_get(data: dict, key: str, default: Any = None) -> Any:
    """Safely get nested value from dict."""
    keys = key.split(".")
    result = data
    for k in keys:
        if isinstance(result, dict):
            result = result.get(k)
        else:
            return default
        if result is None:
            return default
    return result


def chunk_list(items: list, chunk_size: int):
    """Split list into chunks."""
    for i in range(0, len(items), chunk_size):
        yield items[i:i + chunk_size]


def flatten_dict(d: dict, parent_key: str = "", sep: str = ".") -> dict:
    """Flatten nested dictionary."""
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(flatten_dict(v, new_key, sep))
        elif isinstance(v, list):
            for i, item in enumerate(v):
                if isinstance(item, dict):
                    items.update(flatten_dict(item, f"{new_key}[{i}]", sep))
                else:
                    items[f"{new_key}[{i}]"] = item
        else:
            items[new_key] = v
    return items