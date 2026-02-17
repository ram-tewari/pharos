"""Console utilities for Pharos CLI."""

import os
import sys
from typing import Optional

from rich.console import Console
from rich.theme import Theme

from pharos_cli.utils.color import ColorMode, get_color_system, should_use_color

# Custom theme for Pharos CLI
THEME = Theme(
    {
        "repr.str": "cyan",
        "repr.number": "green",
        "repr.bool": "green",
        "repr.none": "dim",
        "logging.level.info": "green",
        "logging.level.warning": "yellow",
        "logging.level.error": "red",
        "logging.level.debug": "dim",
    }
)

# Console singleton
_console: Optional[Console] = None
_color_mode: Optional[ColorMode] = None


def set_color_mode(mode: Optional[ColorMode]) -> None:
    """Set the color mode for the console.
    
    This should be called before get_console() is first called.
    
    Args:
        mode: Color mode to use (auto, always, never)
    """
    global _color_mode, _console
    _color_mode = mode
    # Reset console if it was already created
    if _console is not None:
        _console = None


def get_color_mode() -> Optional[ColorMode]:
    """Get the current color mode.
    
    Returns:
        Current color mode or None if not set
    """
    return _color_mode


def get_console() -> Console:
    """Get the Rich console singleton."""
    global _console

    if _console is None:
        # Determine color system based on color mode and environment
        color_system = get_color_system(_color_mode)

        _console = Console(
            theme=THEME,
            color_system=color_system,
            force_terminal=True,
            width=120,
            soft_wrap=False,
        )

    return _console


# Alias for convenience
console = get_console