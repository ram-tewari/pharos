"""Shell completion scripts for Pharos CLI."""

from .bash import get_bash_completion_script
from .zsh import get_zsh_completion_script
from .fish import get_fish_completion_script

__all__ = [
    "get_bash_completion_script",
    "get_zsh_completion_script",
    "get_fish_completion_script",
]