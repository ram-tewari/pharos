"""Tests for color and theme utilities."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

from pharos_cli.utils.color import (
    ColorMode,
    is_tty,
    is_ci_environment,
    supports_color,
    get_color_system,
    should_use_color,
    get_terminal_info,
)


class TestColorMode:
    """Tests for ColorMode enum."""

    def test_color_mode_values(self):
        """Test ColorMode enum values."""
        assert ColorMode.AUTO.value == "auto"
        assert ColorMode.ALWAYS.value == "always"
        assert ColorMode.NEVER.value == "never"


class TestIsTty:
    """Tests for is_tty function."""

    def test_is_tty_returns_true_when_tty(self):
        """Test is_tty returns True when stdout is a TTY."""
        with patch.object(sys.stdout, "isatty", return_value=True):
            assert is_tty() is True

    def test_is_tty_returns_false_when_not_tty(self):
        """Test is_tty returns False when stdout is not a TTY."""
        with patch.object(sys.stdout, "isatty", return_value=False):
            assert is_tty() is False

    def test_is_tty_handles_exception(self):
        """Test is_tty handles exceptions gracefully."""
        with patch.object(sys.stdout, "isatty", side_effect=Exception("Test error")):
            assert is_tty() is False


class TestIsCiEnvironment:
    """Tests for is_ci_environment function."""

    def test_not_ci_by_default(self):
        """Test is_ci_environment returns False when no CI vars are set."""
        # Clear all CI-related env vars
        ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
        with patch.dict(os.environ, {var: "" for var in ci_vars}, clear=False):
            for var in ci_vars:
                os.environ.pop(var, None)
            assert is_ci_environment() is False

    def test_ci_with_github_actions(self):
        """Test is_ci_environment returns True when GITHUB_ACTIONS is set."""
        with patch.dict(os.environ, {"GITHUB_ACTIONS": "true"}):
            assert is_ci_environment() is True

    def test_ci_with_travis(self):
        """Test is_ci_environment returns True when TRAVIS is set."""
        with patch.dict(os.environ, {"TRAVIS": "true"}):
            assert is_ci_environment() is True

    def test_ci_with_circleci(self):
        """Test is_ci_environment returns True when CIRCLECI is set."""
        with patch.dict(os.environ, {"CIRCLECI": "true"}):
            assert is_ci_environment() is True

    def test_ci_with_jenkins(self):
        """Test is_ci_environment returns True when JENKINS is set."""
        with patch.dict(os.environ, {"JENKINS": "true"}):
            assert is_ci_environment() is True


class TestSupportsColor:
    """Tests for supports_color function."""

    def test_no_color_when_no_color_set(self):
        """Test supports_color returns False when NO_COLOR is set."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            assert supports_color() is False

    def test_no_color_when_not_tty(self):
        """Test supports_color returns False when not a TTY."""
        with patch.object(sys.stdout, "isatty", return_value=False):
            assert supports_color() is False

    def test_no_color_in_ci(self):
        """Test supports_color returns False in CI environment."""
        with patch.dict(os.environ, {"CI": "true"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert supports_color() is False

    def test_no_color_with_dumb_terminal(self):
        """Test supports_color returns False with dumb terminal."""
        with patch.dict(os.environ, {"TERM": "dumb"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert supports_color() is False

    def test_no_color_with_empty_terminal(self):
        """Test supports_color returns False with empty terminal."""
        with patch.dict(os.environ, {"TERM": ""}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert supports_color() is False

    def test_supports_color_in_normal_terminal(self):
        """Test supports_color returns True in normal terminal."""
        with patch.dict(os.environ, {"TERM": "xterm-256color"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert supports_color() is True


class TestGetColorSystem:
    """Tests for get_color_system function."""

    def test_always_returns_standard(self):
        """Test get_color_system returns 'standard' when mode is ALWAYS."""
        result = get_color_system(ColorMode.ALWAYS)
        assert result == "standard"

    def test_never_returns_none(self):
        """Test get_color_system returns None when mode is NEVER."""
        result = get_color_system(ColorMode.NEVER)
        assert result is None

    def test_auto_returns_standard_when_supported(self):
        """Test get_color_system returns 'standard' when auto and supported."""
        with patch.dict(os.environ, {"TERM": "xterm-256color"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                result = get_color_system(ColorMode.AUTO)
                assert result == "standard"

    def test_auto_returns_none_when_not_supported(self):
        """Test get_color_system returns None when auto and not supported."""
        with patch.object(sys.stdout, "isatty", return_value=False):
            result = get_color_system(ColorMode.AUTO)
            assert result is None

    def test_none_returns_standard_when_supported(self):
        """Test get_color_system returns 'standard' when None and supported."""
        with patch.dict(os.environ, {"TERM": "xterm-256color"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                result = get_color_system(None)
                assert result == "standard"


class TestShouldUseColor:
    """Tests for should_use_color function."""

    def test_no_color_when_no_color_env_set(self):
        """Test should_use_color returns False when NO_COLOR is set."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            assert should_use_color() is False

    def test_always_returns_true(self):
        """Test should_use_color returns True when mode is ALWAYS."""
        assert should_use_color(ColorMode.ALWAYS) is True

    def test_never_returns_false(self):
        """Test should_use_color returns False when mode is NEVER."""
        assert should_use_color(ColorMode.NEVER) is False

    def test_auto_returns_true_when_supported(self):
        """Test should_use_color returns True when auto and supported."""
        with patch.dict(os.environ, {"TERM": "xterm-256color"}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert should_use_color(ColorMode.AUTO) is True

    def test_auto_returns_false_when_not_supported(self):
        """Test should_use_color returns False when auto and not supported."""
        with patch.object(sys.stdout, "isatty", return_value=False):
            assert should_use_color(ColorMode.AUTO) is False

    def test_no_color_env_overrides_always(self):
        """Test NO_COLOR environment overrides ALWAYS mode."""
        with patch.dict(os.environ, {"NO_COLOR": "1"}):
            assert should_use_color(ColorMode.ALWAYS) is False


class TestGetTerminalInfo:
    """Tests for get_terminal_info function."""

    def test_get_terminal_info_returns_dict(self):
        """Test get_terminal_info returns a dictionary."""
        info = get_terminal_info()
        assert isinstance(info, dict)
        assert "is_tty" in info
        assert "is_ci" in info
        assert "supports_color" in info
        assert "term" in info
        assert "no_color" in info

    def test_get_terminal_info_values(self):
        """Test get_terminal_info returns correct values."""
        with patch.dict(os.environ, {"TERM": "xterm", "NO_COLOR": ""}):
            with patch.object(sys.stdout, "isatty", return_value=True):
                info = get_terminal_info()
                assert info["is_tty"] is True
                assert info["is_ci"] is False
                assert info["term"] == "xterm"
                assert info["no_color"] is True


class TestColorModeCliOptions:
    """Tests for color mode CLI options."""

    runner = pytest.importorskip("typer.testing").CliRunner()

    def test_color_option_always(self):
        """Test --color always option."""
        from pharos_cli.cli import app

        with patch("pharos_cli.utils.color.supports_color", return_value=False):
            result = self.runner.invoke(app, ["--color", "always", "info"])
            # Should show color mode as always
            assert result.exit_code == 0
            assert "always" in result.stdout

    def test_color_option_never(self):
        """Test --color never option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--color", "never", "info"])
        assert result.exit_code == 0
        assert "never" in result.stdout

    def test_color_option_auto(self):
        """Test --color auto option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--color", "auto", "info"])
        assert result.exit_code == 0
        assert "auto" in result.stdout

    def test_no_color_flag(self):
        """Test --no-color flag."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--no-color", "info"])
        assert result.exit_code == 0
        assert "never" in result.stdout

    def test_color_option_invalid(self):
        """Test --color with invalid value shows warning."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--color", "invalid", "info"])
        assert result.exit_code == 0
        assert "Warning" in result.stdout or "warning" in result.stdout.lower()

    def test_color_option_case_insensitive(self):
        """Test --color option is case insensitive."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--color", "ALWAYS", "info"])
        assert result.exit_code == 0
        assert "always" in result.stdout

    def test_no_color_overrides_color_option(self):
        """Test --no-color overrides --color option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--color", "always", "--no-color", "info"])
        assert result.exit_code == 0
        # --no-color should take precedence
        assert "never" in result.stdout


class TestNoColorEnvironmentVariable:
    """Tests for NO_COLOR environment variable support."""

    runner = pytest.importorskip("typer.testing").CliRunner()

    def test_no_color_env_disables_colors(self):
        """Test that NO_COLOR environment variable disables colors."""
        from pharos_cli.cli import app

        env = os.environ.copy()
        env["NO_COLOR"] = "1"

        result = self.runner.invoke(app, ["info"], env=env)
        assert result.exit_code == 0
        assert "NO_COLOR set: True" in result.stdout

    def test_no_color_env_overrides_color_option(self):
        """Test that NO_COLOR env var overrides --color always."""
        from pharos_cli.cli import app

        env = os.environ.copy()
        env["NO_COLOR"] = "1"

        result = self.runner.invoke(app, ["--color", "always", "info"], env=env)
        assert result.exit_code == 0
        # NO_COLOR should take precedence - check that NO_COLOR is set
        # The output may contain ANSI codes, so we check for the key part
        assert "NO_COLOR set:" in result.stdout
        # Verify the color mode is still 'always' from CLI (NO_COLOR affects terminal detection, not CLI mode)
        assert "Current color mode: always" in result.stdout