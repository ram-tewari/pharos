"""Tests for configuration module."""

import pytest
import tempfile
import os
from pathlib import Path
from typer.testing import CliRunner

from pharos_cli.config.settings import (
    Config,
    Profile,
    OutputConfig,
    BehaviorConfig,
    load_config,
    save_config,
    get_config_dir,
    get_config_path,
)
from pharos_cli.cli import app as pharos_app
from pharos_cli.commands.config import config_app


class TestProfile:
    """Tests for Profile model."""

    def test_default_profile(self):
        """Test default profile values."""
        profile = Profile()
        assert profile.api_url == "http://localhost:8000"
        assert profile.api_key is None
        assert profile.timeout == 30
        assert profile.verify_ssl is True

    def test_custom_profile(self):
        """Test custom profile values."""
        profile = Profile(
            api_url="https://api.example.com",
            api_key="test-key",
            timeout=60,
            verify_ssl=False,
        )
        assert profile.api_url == "https://api.example.com"
        assert profile.api_key == "test-key"
        assert profile.timeout == 60
        assert profile.verify_ssl is False


class TestOutputConfig:
    """Tests for OutputConfig model."""

    def test_default_output_config(self):
        """Test default output config values."""
        config = OutputConfig()
        assert config.format == "table"
        assert config.color == "auto"
        assert config.pager == "auto"

    def test_custom_output_config(self):
        """Test custom output config values."""
        config = OutputConfig(format="json", color="always", pager="never")
        assert config.format == "json"
        assert config.color == "always"
        assert config.pager == "never"


class TestBehaviorConfig:
    """Tests for BehaviorConfig model."""

    def test_default_behavior_config(self):
        """Test default behavior config values."""
        config = BehaviorConfig()
        assert config.confirm_destructive is True
        assert config.show_progress is True
        assert config.parallel_batch is True
        assert config.max_workers == 4


class TestConfig:
    """Tests for Config model."""

    def test_default_config(self):
        """Test default config values."""
        config = Config()
        assert config.active_profile == "default"
        assert "default" in config.profiles
        assert config.output.format == "table"
        assert config.behavior.confirm_destructive is True

    def test_get_active_profile(self):
        """Test getting active profile."""
        config = Config()
        profile = config.get_active_profile()
        assert profile.api_url == "http://localhost:8000"

    def test_get_profile(self):
        """Test getting profile by name."""
        config = Config(profiles={"test": Profile(api_url="http://test.com")})
        profile = config.get_profile("test")
        assert profile is not None
        assert profile.api_url == "http://test.com"

    def test_get_nonexistent_profile(self):
        """Test getting nonexistent profile returns None."""
        config = Config()
        profile = config.get_profile("nonexistent")
        assert profile is None

    def test_add_profile(self):
        """Test adding a profile."""
        config = Config()
        config.add_profile("production", Profile(api_url="https://prod.com"))
        assert "production" in config.profiles
        assert config.profiles["production"].api_url == "https://prod.com"

    def test_set_active_profile(self):
        """Test setting active profile."""
        config = Config(profiles={"dev": Profile(), "prod": Profile()})
        result = config.set_active_profile("prod")
        assert result is True
        assert config.active_profile == "prod"

    def test_set_active_profile_nonexistent(self):
        """Test setting active profile to nonexistent returns False."""
        config = Config()
        result = config.set_active_profile("nonexistent")
        assert result is False
        assert config.active_profile == "default"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = Config(active_profile="test")
        data = config.to_dict()
        assert data["active_profile"] == "test"
        assert "profiles" in data
        assert "output" in data
        assert "behavior" in data


class TestConfigFileOperations:
    """Tests for config file operations."""

    def test_save_and_load_config(self):
        """Test saving and loading config."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"

            original_path = get_config_path()
            try:
                # Override config path
                import pharos_cli.config.settings as settings
                original_get_config_path = settings.get_config_path

                settings.get_config_path = lambda: config_path

                # Create and save config
                config = Config(
                    active_profile="test",
                    profiles={"test": Profile(api_url="http://test.com")},
                )
                save_config(config)

                # Load config
                loaded_config = load_config(config_path)

                assert loaded_config.active_profile == "test"
                assert loaded_config.get_profile("test") is not None
                assert loaded_config.get_profile("test").api_url == "http://test.com"
            finally:
                settings.get_config_path = original_get_config_path

    def test_load_nonexistent_config(self):
        """Test loading nonexistent config returns default."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "nonexistent.yaml"

            import pharos_cli.config.settings as settings
            original_get_config_path = settings.get_config_path

            settings.get_config_path = lambda: config_path

            try:
                config = load_config(config_path)
                assert config.active_profile == "default"
            finally:
                settings.get_config_path = original_get_config_path


class TestConfigCommands:
    """Tests for config CLI commands."""

    runner = CliRunner()

    def test_config_path_command(self):
        """Test 'pharos config path' command."""
        result = self.runner.invoke(pharos_app, ["config", "path"])
        assert result.exit_code == 0
        assert ".pharos" in result.stdout or "config.yaml" in result.stdout

    def test_config_dir_command(self):
        """Test 'pharos config dir' command."""
        result = self.runner.invoke(pharos_app, ["config", "dir"])
        assert result.exit_code == 0
        assert ".pharos" in result.stdout or "pharos" in result.stdout

    def test_config_show_default(self):
        """Test 'pharos config show' command with defaults."""
        result = self.runner.invoke(pharos_app, ["config", "show"])
        assert result.exit_code == 0
        assert "API URL" in result.stdout or "api_url" in result.stdout.lower()
        assert "Output" in result.stdout or "output" in result.stdout.lower()

    def test_config_show_json_format(self):
        """Test 'pharos config show --format json' command."""
        result = self.runner.invoke(pharos_app, ["config", "show", "--format", "json"])
        assert result.exit_code == 0
        # JSON output should contain these keys
        assert "api_url" in result.stdout.lower() or "API URL" in result.stdout

    def test_config_show_yaml_format(self):
        """Test 'pharos config show --format yaml' command."""
        result = self.runner.invoke(pharos_app, ["config", "show", "--format", "yaml"])
        assert result.exit_code == 0
        # YAML output should contain these keys
        assert "api_url" in result.stdout.lower() or "API URL" in result.stdout

    def test_config_show_specific_profile(self):
        """Test 'pharos config show --profile' command."""
        result = self.runner.invoke(pharos_app, ["config", "show", "--profile", "default"])
        assert result.exit_code == 0
        assert "default" in result.stdout.lower()

    def test_config_show_nonexistent_profile(self):
        """Test 'pharos config show --profile' with nonexistent profile."""
        result = self.runner.invoke(pharos_app, ["config", "show", "--profile", "nonexistent"])
        assert result.exit_code != 0
        assert "not found" in result.stdout.lower() or "error" in result.stdout.lower()

    def test_init_command_non_interactive(self):
        """Test 'pharos config init --non-interactive' command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"

            # Override config path for testing
            import pharos_cli.config.settings as settings
            original_get_config_path = settings.get_config_path

            settings.get_config_path = lambda: config_path

            try:
                result = self.runner.invoke(
                    pharos_app,
                    ["config", "init", "--non-interactive", "--url", "http://test.com"]
                )
                assert result.exit_code == 0
                assert config_path.exists()

                # Verify config content
                config = load_config(config_path)
                assert config.get_active_profile().api_url == "http://test.com"
            finally:
                settings.get_config_path = original_get_config_path

    def test_init_command_with_api_key(self):
        """Test 'pharos config init --api-key' command."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"

            import pharos_cli.config.settings as settings
            original_get_config_path = settings.get_config_path

            settings.get_config_path = lambda: config_path

            try:
                result = self.runner.invoke(
                    pharos_app,
                    ["config", "init", "--non-interactive", "--url", "http://test.com", "--api-key", "test-key"]
                )
                assert result.exit_code == 0
                assert config_path.exists()

                # Verify config content
                config = load_config(config_path)
                assert config.get_active_profile().api_url == "http://test.com"
            finally:
                settings.get_config_path = original_get_config_path

    def test_init_command_already_exists(self):
        """Test 'pharos config init' when config already exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "config.yaml"
            config_path.write_text("active_profile: default\nprofiles: {}")

            # Patch at module level before importing
            import pharos_cli.commands.config as config_module
            original_get_config_path = config_module.get_config_path

            config_module.get_config_path = lambda: config_path

            try:
                result = self.runner.invoke(pharos_app, ["config", "init", "--non-interactive"])
                assert result.exit_code == 0
                assert "already exists" in result.stdout.lower()
            finally:
                config_module.get_config_path = original_get_config_path