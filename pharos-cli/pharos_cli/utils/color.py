"""Color and theme utilities for Pharos CLI."""

import os
import sys
from enum import Enum
from typing import Optional

# Valid color options
class ColorMode(str, Enum):
    """Color mode enumeration."""
    AUTO = "auto"
    ALWAYS = "always"
    NEVER = "never"


def is_tty() -> bool:
    """Check if stdout is a TTY (terminal).
    
    Returns:
        True if stdout is a terminal, False otherwise.
    """
    try:
        return sys.stdout.isatty()
    except Exception:
        return False


def is_ci_environment() -> bool:
    """Check if running in a CI environment.
    
    Returns:
        True if running in a known CI environment, False otherwise.
    """
    # Check for common CI environment variables
    ci_vars = [
        "CI",
        "GITHUB_ACTIONS",
        "GITLAB_CI",
        "TRAVIS",
        "CIRCLECI",
        "JENKINS",
        "BUILD_ID",
        "TEAMCITY_VERSION",
    ]
    
    return any(os.environ.get(var) for var in ci_vars)


def supports_color() -> bool:
    """Check if the terminal supports color output.
    
    This checks:
    1. If stdout is a TTY
    2. If NO_COLOR environment variable is set
    3. If we're in a CI environment (many CI terminals don't support color)
    
    Returns:
        True if color output is supported, False otherwise.
    """
    # Check NO_COLOR first (standard: https://no-color.org/)
    if "NO_COLOR" in os.environ:
        return False
    
    # Check if stdout is a TTY
    if not is_tty():
        return False
    
    # Check for CI environment (often don't support true color)
    if is_ci_environment():
        return False
    
    # Check for terminal type
    term = os.environ.get("TERM", "").lower()
    if term in ["dumb", ""]:
        return False
    
    return True


def get_color_system(force_color: Optional[ColorMode] = None) -> Optional[str]:
    """Get the appropriate color system for the terminal.
    
    Args:
        force_color: Optional color mode to force (overrides auto-detection)
    
    Returns:
        Color system string: "standard", "256", "truecolor", or None for no color
    """
    # If force_color is provided, use it directly
    if force_color is not None:
        if force_color == ColorMode.ALWAYS:
            return "standard"
        elif force_color == ColorMode.NEVER:
            return None
        else:  # AUTO
            pass  # Fall through to auto-detection
    
    # Auto-detect based on terminal capabilities
    if supports_color():
        # Use standard 16-color mode for best compatibility
        # Can be upgraded to "256" or "truecolor" if needed
        return "standard"
    
    return None


def should_use_color(color_option: Optional[ColorMode] = None) -> bool:
    """Determine if color output should be used.
    
    This is the main function to check whether to use colors.
    It respects:
    1. Explicit color option (--color flag)
    2. NO_COLOR environment variable
    3. TTY detection
    4. CI environment detection
    
    Args:
        color_option: Explicit color mode from CLI flag
    
    Returns:
        True if color should be used, False otherwise
    """
    # Check NO_COLOR first (standard environment variable)
    if "NO_COLOR" in os.environ:
        return False
    
    # If explicit option is provided, use it
    if color_option is not None:
        if color_option == ColorMode.ALWAYS:
            return True
        elif color_option == ColorMode.NEVER:
            return False
        else:  # AUTO
            pass  # Fall through to auto-detection
    
    # Auto-detect
    return supports_color()


def get_terminal_info() -> dict:
    """Get information about the terminal environment.
    
    Returns:
        Dictionary with terminal information
    """
    return {
        "is_tty": is_tty(),
        "is_ci": is_ci_environment(),
        "supports_color": supports_color(),
        "term": os.environ.get("TERM", ""),
        "no_color": "NO_COLOR" in os.environ,
    }