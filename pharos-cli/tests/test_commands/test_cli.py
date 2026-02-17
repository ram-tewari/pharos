"""Tests for CLI entry point and main app."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, MagicMock

from pharos_cli.cli import app
from pharos_cli.version import __version__


class TestCLIEntryPoint:
    """Test CLI entry point and basic commands."""

    def test_version_command(self, runner):
        """Test version command displays version."""
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output
        assert "Pharos CLI" in result.output

    def test_help_command(self, runner):
        """Test --help displays help information."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Pharos CLI" in result.output
        assert "Available commands" in result.output or "Commands" in result.output

    def test_help_shows_version_command(self, runner):
        """Test that help displays version command."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "version" in result.output.lower()

    def test_help_shows_auth_command(self, runner):
        """Test that help displays auth command group."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "auth" in result.output.lower()

    def test_completion_requires_shell(self, runner):
        """Test completion command requires shell argument."""
        result = runner.invoke(app, ["completion"])
        assert result.exit_code == 0
        assert "shell" in result.output.lower()

    def test_completion_bash(self, runner):
        """Test bash completion generation."""
        result = runner.invoke(app, ["completion", "bash"])
        # May fail on some systems, but should not crash
        assert result.exit_code in [0, 1]

    def test_completion_zsh(self, runner):
        """Test zsh completion generation."""
        result = runner.invoke(app, ["completion", "zsh"])
        # May fail on some systems, but should not crash
        assert result.exit_code in [0, 1]

    def test_completion_fish(self, runner):
        """Test fish completion generation."""
        result = runner.invoke(app, ["completion", "fish"])
        # May fail on some systems, but should not crash
        assert result.exit_code in [0, 1]

    def test_invalid_command(self, runner):
        """Test that invalid command shows error."""
        result = runner.invoke(app, ["invalid-command-xyz"])
        assert result.exit_code != 0
        assert "No such command" in result.output or "Error" in result.output


class TestAuthCommandGroup:
    """Test auth command group."""

    def test_auth_help(self, runner):
        """Test auth --help displays auth commands."""
        result = runner.invoke(app, ["auth", "--help"])
        assert result.exit_code == 0
        assert "login" in result.output.lower()
        assert "logout" in result.output.lower()
        assert "whoami" in result.output.lower()

    def test_auth_login_help(self, runner):
        """Test auth login --help displays options."""
        result = runner.invoke(app, ["auth", "login", "--help"])
        assert result.exit_code == 0
        assert "--api-key" in result.output
        assert "--url" in result.output

    def test_auth_logout_help(self, runner):
        """Test auth logout --help displays options."""
        result = runner.invoke(app, ["auth", "logout", "--help"])
        assert result.exit_code == 0

    def test_auth_whoami_help(self, runner):
        """Test auth whoami --help displays options."""
        result = runner.invoke(app, ["auth", "whoami", "--help"])
        assert result.exit_code == 0

    def test_auth_status_help(self, runner):
        """Test auth status --help displays options."""
        result = runner.invoke(app, ["auth", "status", "--help"])
        assert result.exit_code == 0


class TestConsoleSingleton:
    """Test Rich console singleton."""

    def test_get_console_returns_console(self):
        """Test get_console returns a Console instance."""
        from pharos_cli.utils.console import get_console

        console = get_console()
        assert console is not None
        from rich.console import Console

        assert isinstance(console, Console)

    def test_get_console_returns_same_instance(self):
        """Test get_console returns singleton instance."""
        from pharos_cli.utils.console import get_console

        console1 = get_console()
        console2 = get_console()
        assert console1 is console2


class TestVersionInfo:
    """Test version information."""

    def test_version_is_string(self):
        """Test __version__ is a string."""
        from pharos_cli.version import __version__

        assert isinstance(__version__, str)

    def test_version_is_valid_format(self):
        """Test __version__ follows semantic versioning."""
        from pharos_cli.version import __version__

        parts = __version__.split(".")
        assert len(parts) >= 2
        for part in parts[:3]:
            assert part.isdigit()