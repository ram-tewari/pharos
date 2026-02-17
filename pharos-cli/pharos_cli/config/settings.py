"""Configuration management for Pharos CLI."""

import os
from pathlib import Path
from typing import Dict, Optional, Any
from functools import lru_cache

import yaml
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """Profile configuration for Pharos CLI."""

    api_url: str = "http://localhost:8000"
    api_key: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[int] = None  # Unix timestamp
    timeout: int = 30
    verify_ssl: bool = True


class OutputConfig(BaseModel):
    """Output formatting configuration."""

    format: str = "table"
    color: str = "auto"
    pager: str = "auto"


class BehaviorConfig(BaseModel):
    """Behavior configuration for Pharos CLI."""

    confirm_destructive: bool = True
    show_progress: bool = True
    parallel_batch: bool = True
    max_workers: int = 4


class Config(BaseModel):
    """Main configuration for Pharos CLI."""

    active_profile: str = "default"
    profiles: Dict[str, Profile] = Field(default_factory=lambda: {"default": Profile()})
    output: OutputConfig = Field(default_factory=OutputConfig)
    behavior: BehaviorConfig = Field(default_factory=BehaviorConfig)

    def get_active_profile(self) -> Profile:
        """Get the active profile."""
        return self.profiles.get(self.active_profile, Profile())

    def get_profile(self, name: str) -> Optional[Profile]:
        """Get a profile by name."""
        return self.profiles.get(name)

    def add_profile(self, name: str, profile: Profile) -> None:
        """Add or update a profile."""
        self.profiles[name] = profile

    def set_active_profile(self, name: str) -> bool:
        """Set the active profile."""
        if name in self.profiles:
            self.active_profile = name
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return self.model_dump()


def get_config_dir() -> Path:
    """Get the configuration directory."""
    # Check for platform-specific config locations
    if os.name == "nt":  # Windows
        config_dir = Path(os.environ.get("APPDATA", ""))
        config_dir = config_dir / "pharos"
    else:  # Linux/macOS
        config_dir = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        config_dir = config_dir / "pharos"

    # Also check for legacy location
    legacy_config = Path.home() / ".pharos"
    if legacy_config.exists():
        config_dir = legacy_config

    return config_dir


def get_config_path() -> Path:
    """Get the configuration file path."""
    config_dir = get_config_dir()
    return config_dir / "config.yaml"


@lru_cache(maxsize=1)
def load_config(config_path: Optional[Path] = None) -> Config:
    """Load configuration from file."""
    if config_path is None:
        config_path = get_config_path()

    if not config_path.exists():
        return Config()

    try:
        with open(config_path, "r") as f:
            data = yaml.safe_load(f) or {}
        return Config(**data)
    except (yaml.YAMLError, OSError) as e:
        console = get_console()
        console.print(f"[yellow]Warning:[/yellow] Could not load config: {e}")
        return Config()


def save_config(config: Config, config_path: Optional[Path] = None) -> None:
    """Save configuration to file."""
    if config_path is None:
        config_path = get_config_path()

    config_dir = config_path.parent
    config_dir.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w") as f:
        yaml.dump(config.to_dict(), f, default_flow_style=False, sort_keys=False)


def apply_env_overrides(config: Config) -> Config:
    """Apply environment variable overrides to config."""
    # Override from environment variables
    if os.environ.get("PHAROS_API_URL"):
        profile = config.get_active_profile()
        profile.api_url = os.environ["PHAROS_API_URL"]

    if os.environ.get("PHAROS_API_KEY"):
        profile = config.get_active_profile()
        profile.api_key = os.environ["PHAROS_API_KEY"]

    if os.environ.get("PHAROS_PROFILE"):
        config.set_active_profile(os.environ["PHAROS_PROFILE"])

    if os.environ.get("PHAROS_OUTPUT_FORMAT"):
        config.output.format = os.environ["PHAROS_OUTPUT_FORMAT"]

    if os.environ.get("PHAROS_NO_COLOR"):
        config.output.color = "never"

    if os.environ.get("PHAROS_VERIFY_SSL") == "0":
        profile = config.get_active_profile()
        profile.verify_ssl = False

    return config


# Import get_console at the end to avoid circular imports
from pharos_cli.utils.console import get_console