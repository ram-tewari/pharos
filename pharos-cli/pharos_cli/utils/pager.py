"""Pager utilities for Pharos CLI.

Provides automatic paging for long output, supporting less, more, and bat.
"""

import os
import sys
import shutil
import subprocess
from enum import Enum
from typing import Optional, Callable, Any
from contextlib import contextmanager


class PagerMode(Enum):
    """Pager mode options."""
    AUTO = "auto"  # Use pager if available and output is a TTY
    ALWAYS = "always"  # Always use pager
    NEVER = "never"  # Never use pager


class PagerNotAvailableError(Exception):
    """Raised when no pager is available."""
    pass


def get_pager_executable() -> Optional[str]:
    """Find an available pager executable.
    
    Searches for available pagers in order of preference:
    1. BAT_PAGER environment variable
    2. PAGER environment variable
    3. less (with --quit-if-one-screen option)
    4. more
    5. bat (with --paging=always)
    
    Returns:
        Path to pager executable or None if not found
    """
    # Check BAT_PAGER first (bat uses this)
    bat_pager = os.environ.get("BAT_PAGER")
    if bat_pager and shutil.which(bat_pager.split()[0]):
        return bat_pager
    
    # Check PAGER environment variable
    pager = os.environ.get("PAGER")
    if pager:
        pager_name = pager.split()[0]
        if shutil.which(pager_name):
            return pager
    
    # Check for less with quit-if-one-screen option (preferred on Unix)
    if shutil.which("less"):
        # Use --quit-if-one-screen to exit if content fits on one screen
        # Use --no-init to avoid clearing screen on exit
        # Use --RAW-CONTROL-CHARS to preserve colors
        return "less --quit-if-one-screen --no-init --raw-control-chars"
    
    # Check for more (Windows/DOS fallback)
    if shutil.which("more"):
        return "more"
    
    # Check for bat with paging
    if shutil.which("bat"):
        # bat with explicit paging
        return "bat --paging=always --style=plain"
    
    return None


def is_pager_available() -> bool:
    """Check if any pager is available.
    
    Returns:
        True if a pager executable is available
    """
    return get_pager_executable() is not None


def should_use_pager(mode: PagerMode = PagerMode.AUTO) -> bool:
    """Determine if pager should be used based on mode and environment.
    
    Args:
        mode: Pager mode to use
        
    Returns:
        True if pager should be used
    """
    if mode == PagerMode.NEVER:
        return False
    
    if mode == PagerMode.ALWAYS:
        return is_pager_available()
    
    # AUTO mode: use pager only if:
    # 1. A pager is available
    # 2. Output is to a TTY
    # 3. Not in CI environment
    if not is_pager_available():
        return False
    
    # Check if stdout is a TTY
    try:
        if not sys.stdout.isatty():
            return False
    except (AttributeError, OSError):
        return False
    
    # Don't use pager in CI environments
    ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
    for var in ci_vars:
        if os.environ.get(var):
            return False
    
    return True


def get_pager_mode_from_string(mode_str: str) -> PagerMode:
    """Convert string to PagerMode enum.
    
    Args:
        mode_str: Mode string (auto, always, never)
        
    Returns:
        PagerMode enum value
        
    Raises:
        ValueError: If mode_str is invalid
    """
    mode_str = mode_str.lower().strip()
    if mode_str in ("auto", "a"):
        return PagerMode.AUTO
    elif mode_str in ("always", "always"):
        return PagerMode.ALWAYS
    elif mode_str in ("never", "n", "no"):
        return PagerMode.NEVER
    else:
        raise ValueError(f"Invalid pager mode: {mode_str}. Valid options: auto, always, never")


@contextmanager
def pager_context(
    content: str,
    mode: PagerMode = PagerMode.AUTO,
    pager_executable: Optional[str] = None,
):
    """Context manager to display content through a pager.
    
    Args:
        content: Content to display
        mode: Pager mode to use
        pager_executable: Optional pager executable path
        
    Yields:
        None
        
    Raises:
        PagerNotAvailableError: If pager is not available and mode is ALWAYS
    """
    if not should_use_pager(mode):
        # Just print to stdout
        sys.stdout.write(content)
        sys.stdout.flush()
        yield
        return
    
    # Get pager executable
    if pager_executable is None:
        pager = get_pager_executable()
    else:
        pager = pager_executable
    
    if not pager:
        if mode == PagerMode.ALWAYS:
            raise PagerNotAvailableError("No pager available but mode is 'always'")
        # Fall back to direct output
        sys.stdout.write(content)
        sys.stdout.flush()
        yield
        return
    
    try:
        # Parse pager command safely without shell=True
        import shlex
        pager_args = shlex.split(pager)
        
        # Start pager process
        process = subprocess.Popen(
            pager_args,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        # Write content to pager
        process.communicate(input=content)
        
        # Check for errors
        if process.returncode != 0:
            # If pager failed, fall back to direct output
            sys.stdout.write(content)
            sys.stdout.flush()
    
    except (OSError, subprocess.SubprocessError, ValueError) as e:
        # If pager failed, fall back to direct output
        # ValueError can occur from shlex.split with empty strings or other issues
        sys.stdout.write(content)
        sys.stdout.flush()
    
    yield


def display_through_pager(
    content: str,
    mode: PagerMode = PagerMode.AUTO,
    pager_executable: Optional[str] = None,
) -> bool:
    """Display content through a pager.
    
    Args:
        content: Content to display
        mode: Pager mode to use
        pager_executable: Optional pager executable path
        
    Returns:
        True if pager was used, False if content was printed directly
    """
    if not should_use_pager(mode):
        sys.stdout.write(content)
        sys.stdout.flush()
        return False
    
    # Get pager executable
    if pager_executable is None:
        pager = get_pager_executable()
    else:
        pager = pager_executable
    
    if not pager:
        sys.stdout.write(content)
        sys.stdout.flush()
        return False
    
    try:
        # Parse pager command safely without shell=True
        import shlex
        pager_args = shlex.split(pager)
        
        process = subprocess.Popen(
            pager_args,
            stdin=subprocess.PIPE,
            stdout=sys.stdout,
            stderr=subprocess.PIPE,
            text=True,
        )
        
        process.communicate(input=content)
        
        if process.returncode != 0:
            sys.stdout.write(content)
            sys.stdout.flush()
    
    except (OSError, subprocess.SubprocessError, ValueError):
        # If pager failed, fall back to direct output
        # ValueError can occur from shlex.split with empty strings or other issues
        sys.stdout.write(content)
        sys.stdout.flush()
    
    return True


class PagerManager:
    """Manager for pager configuration and usage."""
    
    def __init__(self):
        self._mode: PagerMode = PagerMode.AUTO
        self._pager_executable: Optional[str] = None
    
    @property
    def mode(self) -> PagerMode:
        """Get current pager mode."""
        return self._mode
    
    @mode.setter
    def mode(self, value: PagerMode) -> None:
        """Set pager mode."""
        self._mode = value
    
    def set_mode_from_string(self, mode_str: str) -> None:
        """Set pager mode from string."""
        self._mode = get_pager_mode_from_string(mode_str)
    
    @property
    def pager_executable(self) -> Optional[str]:
        """Get pager executable path."""
        return self._pager_executable
    
    @pager_executable.setter
    def pager_executable(self, value: Optional[str]) -> None:
        """Set pager executable path."""
        self._pager_executable = value
    
    def should_use_pager(self) -> bool:
        """Check if pager should be used with current settings."""
        return should_use_pager(self._mode)
    
    def display(self, content: str) -> bool:
        """Display content through pager if configured."""
        return display_through_pager(content, self._mode, self._pager_executable)
    
    def get_pager_info(self) -> dict:
        """Get information about pager configuration.
        
        Returns:
            Dictionary with pager information
        """
        return {
            "mode": self._mode.value,
            "pager_available": is_pager_available(),
            "pager_executable": self._pager_executable or get_pager_executable(),
            "should_use_pager": self.should_use_pager(),
        }


# Global pager manager instance
_pager_manager: Optional[PagerManager] = None


def get_pager_manager() -> PagerManager:
    """Get the global pager manager instance."""
    global _pager_manager
    if _pager_manager is None:
        _pager_manager = PagerManager()
    return _pager_manager


def reset_pager_manager() -> None:
    """Reset the global pager manager (for testing)."""
    global _pager_manager
    _pager_manager = None