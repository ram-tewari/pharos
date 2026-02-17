"""Tests for pager utilities."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, mock_open


class TestPagerMode:
    """Tests for PagerMode enum."""

    def test_pager_mode_values(self):
        """Test PagerMode enum values."""
        from pharos_cli.utils.pager import PagerMode

        assert PagerMode.AUTO.value == "auto"
        assert PagerMode.ALWAYS.value == "always"
        assert PagerMode.NEVER.value == "never"


class TestGetPagerExecutable:
    """Tests for get_pager_executable function."""

    def test_returns_none_when_no_pager(self):
        """Test get_pager_executable returns None when no pager is available."""
        from pharos_cli.utils.pager import get_pager_executable

        with patch("shutil.which", return_value=None):
            result = get_pager_executable()
            assert result is None

    def test_returns_less_when_available(self):
        """Test get_pager_executable returns less when available."""
        from pharos_cli.utils.pager import get_pager_executable

        def mock_which(cmd):
            if cmd == "less":
                return "/usr/bin/less"
            return None

        with patch("shutil.which", side_effect=mock_which):
            result = get_pager_executable()
            assert result is not None
            assert "less" in result

    def test_returns_more_when_less_not_available(self):
        """Test get_pager_executable returns more when less is not available."""
        from pharos_cli.utils.pager import get_pager_executable

        def mock_which(cmd):
            if cmd == "more":
                return "/usr/bin/more"
            return None

        with patch("shutil.which", side_effect=mock_which):
            result = get_pager_executable()
            assert result is not None
            assert "more" in result

    def test_returns_bat_when_available(self):
        """Test get_pager_executable returns bat when available."""
        from pharos_cli.utils.pager import get_pager_executable

        def mock_which(cmd):
            if cmd == "bat":
                return "/usr/bin/bat"
            return None

        with patch("shutil.which", side_effect=mock_which):
            result = get_pager_executable()
            assert result is not None
            assert "bat" in result

    def test_checks_bat_pager_env_first(self):
        """Test BAT_PAGER environment variable is checked first."""
        from pharos_cli.utils.pager import get_pager_executable

        def mock_which(cmd):
            if cmd == "bat":
                return "/usr/bin/bat"
            return None

        with patch.dict(os.environ, {"BAT_PAGER": "bat --paging=always"}):
            with patch("shutil.which", side_effect=mock_which):
                result = get_pager_executable()
                # Should return the BAT_PAGER value when bat is in PATH
                assert result == "bat --paging=always"

    def test_checks_pager_env_variable(self):
        """Test PAGER environment variable is checked."""
        from pharos_cli.utils.pager import get_pager_executable

        def mock_which(cmd):
            if cmd == "custom-pager":
                return "/usr/bin/custom-pager"
            return None

        with patch.dict(os.environ, {"PAGER": "custom-pager"}):
            with patch("shutil.which", side_effect=mock_which):
                result = get_pager_executable()
                assert result == "custom-pager"


class TestIsPagerAvailable:
    """Tests for is_pager_available function."""

    def test_returns_true_when_pager_available(self):
        """Test is_pager_available returns True when pager is available."""
        from pharos_cli.utils.pager import is_pager_available

        with patch("shutil.which", return_value="/usr/bin/less"):
            assert is_pager_available() is True

    def test_returns_false_when_no_pager(self):
        """Test is_pager_available returns False when no pager is available."""
        from pharos_cli.utils.pager import is_pager_available

        with patch("shutil.which", return_value=None):
            assert is_pager_available() is False


class TestShouldUsePager:
    """Tests for should_use_pager function."""

    def test_never_returns_false(self):
        """Test should_use_pager returns False when mode is NEVER."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            assert should_use_pager(PagerMode.NEVER) is False

    def test_always_returns_true_when_available(self):
        """Test should_use_pager returns True when mode is ALWAYS and pager available."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            assert should_use_pager(PagerMode.ALWAYS) is True

    def test_always_returns_false_when_not_available(self):
        """Test should_use_pager returns False when mode is ALWAYS and no pager."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value=None):
            assert should_use_pager(PagerMode.ALWAYS) is False

    def test_auto_returns_false_when_not_tty(self):
        """Test should_use_pager returns False when AUTO and not a TTY."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=False):
                assert should_use_pager(PagerMode.AUTO) is False

    def test_auto_returns_false_in_ci(self):
        """Test should_use_pager returns False when AUTO and in CI environment."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=True):
                with patch.dict(os.environ, {"CI": "true"}):
                    assert should_use_pager(PagerMode.AUTO) is False

    def test_auto_returns_true_when_conditions_met(self):
        """Test should_use_pager returns True when AUTO and all conditions met."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=True):
                # Clear CI environment
                ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
                with patch.dict(os.environ, {var: "" for var in ci_vars}, clear=False):
                    for var in ci_vars:
                        os.environ.pop(var, None)
                    assert should_use_pager(PagerMode.AUTO) is True

    def test_auto_returns_false_when_no_pager(self):
        """Test should_use_pager returns False when AUTO and no pager available."""
        from pharos_cli.utils.pager import should_use_pager, PagerMode

        with patch("shutil.which", return_value=None):
            with patch.object(sys.stdout, "isatty", return_value=True):
                assert should_use_pager(PagerMode.AUTO) is False


class TestGetPagerModeFromString:
    """Tests for get_pager_mode_from_string function."""

    def test_auto_mode(self):
        """Test parsing 'auto' mode."""
        from pharos_cli.utils.pager import get_pager_mode_from_string, PagerMode

        assert get_pager_mode_from_string("auto") == PagerMode.AUTO
        assert get_pager_mode_from_string("Auto") == PagerMode.AUTO
        assert get_pager_mode_from_string("AUTO") == PagerMode.AUTO

    def test_always_mode(self):
        """Test parsing 'always' mode."""
        from pharos_cli.utils.pager import get_pager_mode_from_string, PagerMode

        assert get_pager_mode_from_string("always") == PagerMode.ALWAYS
        assert get_pager_mode_from_string("Always") == PagerMode.ALWAYS
        assert get_pager_mode_from_string("ALWAYS") == PagerMode.ALWAYS

    def test_never_mode(self):
        """Test parsing 'never' mode."""
        from pharos_cli.utils.pager import get_pager_mode_from_string, PagerMode

        assert get_pager_mode_from_string("never") == PagerMode.NEVER
        assert get_pager_mode_from_string("Never") == PagerMode.NEVER
        assert get_pager_mode_from_string("NEVER") == PagerMode.NEVER
        assert get_pager_mode_from_string("no") == PagerMode.NEVER

    def test_invalid_mode_raises_error(self):
        """Test invalid mode raises ValueError."""
        from pharos_cli.utils.pager import get_pager_mode_from_string

        with pytest.raises(ValueError):
            get_pager_mode_from_string("invalid")


class TestPagerManager:
    """Tests for PagerManager class."""

    def test_default_mode_is_auto(self):
        """Test PagerManager default mode is AUTO."""
        from pharos_cli.utils.pager import PagerManager, PagerMode

        manager = PagerManager()
        assert manager.mode == PagerMode.AUTO

    def test_set_mode(self):
        """Test setting pager mode."""
        from pharos_cli.utils.pager import PagerManager, PagerMode

        manager = PagerManager()
        manager.mode = PagerMode.ALWAYS
        assert manager.mode == PagerMode.ALWAYS

    def test_set_mode_from_string(self):
        """Test setting pager mode from string."""
        from pharos_cli.utils.pager import PagerManager, PagerMode

        manager = PagerManager()
        manager.set_mode_from_string("always")
        assert manager.mode == PagerMode.ALWAYS

    def test_get_pager_info(self):
        """Test getting pager info."""
        from pharos_cli.utils.pager import PagerManager

        manager = PagerManager()
        info = manager.get_pager_info()

        assert "mode" in info
        assert "pager_available" in info
        assert "pager_executable" in info
        assert "should_use_pager" in info

    def test_display_returns_false_when_no_pager(self):
        """Test display returns False when pager not available."""
        from pharos_cli.utils.pager import PagerManager, PagerMode

        manager = PagerManager()
        manager.mode = PagerMode.NEVER

        with patch("shutil.which", return_value=None):
            result = manager.display("test content")
            assert result is False


class TestPagerContext:
    """Tests for pager_context context manager."""

    def test_prints_to_stdout_when_no_pager(self):
        """Test pager_context prints to stdout when pager not available."""
        from pharos_cli.utils.pager import pager_context, PagerMode

        with patch("shutil.which", return_value=None):
            with pager_context("test content", PagerMode.AUTO) as cm:
                # Context should yield None
                assert cm is None

    def test_uses_pager_when_available(self):
        """Test pager_context uses pager when available."""
        from pharos_cli.utils.pager import pager_context, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=True):
                # Clear CI environment
                ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
                with patch.dict(os.environ, {var: "" for var in ci_vars}, clear=False):
                    for var in ci_vars:
                        os.environ.pop(var, None)

                    with patch("subprocess.Popen") as mock_popen:
                        mock_process = MagicMock()
                        mock_process.returncode = 0
                        mock_process.communicate.return_value = ("", "")
                        mock_popen.return_value = mock_process

                        with pager_context("test content", PagerMode.AUTO):
                            pass

                        mock_popen.assert_called_once()


class TestDisplayThroughPager:
    """Tests for display_through_pager function."""

    def test_prints_to_stdout_when_no_pager(self):
        """Test display_through_pager prints to stdout when no pager."""
        from pharos_cli.utils.pager import display_through_pager, PagerMode

        with patch("shutil.which", return_value=None):
            with patch("sys.stdout.write") as mock_write:
                result = display_through_pager("test content", PagerMode.NEVER)
                assert result is False
                mock_write.assert_called_once_with("test content")

    def test_uses_pager_when_available(self):
        """Test display_through_pager uses pager when available."""
        from pharos_cli.utils.pager import display_through_pager, PagerMode

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=True):
                # Clear CI environment
                ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
                with patch.dict(os.environ, {var: "" for var in ci_vars}, clear=False):
                    for var in ci_vars:
                        os.environ.pop(var, None)

                    with patch("subprocess.Popen") as mock_popen:
                        mock_process = MagicMock()
                        mock_process.returncode = 0
                        mock_process.communicate.return_value = ("", "")
                        mock_popen.return_value = mock_process

                        result = display_through_pager("test content", PagerMode.AUTO)
                        assert result is True
                        mock_popen.assert_called_once()


class TestPagerManagerGlobal:
    """Tests for global pager manager functions."""

    def test_get_pager_manager_returns_singleton(self):
        """Test get_pager_manager returns the same instance."""
        from pharos_cli.utils.pager import get_pager_manager, reset_pager_manager

        reset_pager_manager()
        manager1 = get_pager_manager()
        manager2 = get_pager_manager()
        assert manager1 is manager2

    def test_reset_pager_manager(self):
        """Test reset_pager_manager creates new instance."""
        from pharos_cli.utils.pager import get_pager_manager, reset_pager_manager

        manager1 = get_pager_manager()
        reset_pager_manager()
        manager2 = get_pager_manager()
        assert manager1 is not manager2


class TestPagerCliOptions:
    """Tests for pager CLI options."""

    runner = pytest.importorskip("typer.testing").CliRunner()

    def test_pager_option_always(self):
        """Test --pager always option."""
        from pharos_cli.cli import app

        with patch("shutil.which", return_value="/usr/bin/less"):
            with patch.object(sys.stdout, "isatty", return_value=True):
                # Clear CI environment
                ci_vars = ["CI", "GITHUB_ACTIONS", "GITLAB_CI", "TRAVIS", "CIRCLECI", "JENKINS"]
                with patch.dict(os.environ, {var: "" for var in ci_vars}, clear=False):
                    for var in ci_vars:
                        os.environ.pop(var, None)

                    result = self.runner.invoke(app, ["--pager", "always", "info"])
                    assert result.exit_code == 0
                    assert "always" in result.stdout

    def test_pager_option_never(self):
        """Test --pager never option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--pager", "never", "info"])
        assert result.exit_code == 0
        assert "never" in result.stdout

    def test_pager_option_auto(self):
        """Test --pager auto option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--pager", "auto", "info"])
        assert result.exit_code == 0
        assert "auto" in result.stdout

    def test_no_pager_flag(self):
        """Test --no-pager flag."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--no-pager", "info"])
        assert result.exit_code == 0
        assert "never" in result.stdout

    def test_pager_option_invalid(self):
        """Test --pager with invalid value shows warning."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--pager", "invalid", "info"])
        assert result.exit_code == 0
        assert "Warning" in result.stdout or "warning" in result.stdout.lower()

    def test_pager_option_case_insensitive(self):
        """Test --pager option is case insensitive."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--pager", "ALWAYS", "info"])
        assert result.exit_code == 0
        assert "always" in result.stdout

    def test_no_pager_overrides_pager_option(self):
        """Test --no-pager overrides --pager option."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["--pager", "always", "--no-pager", "info"])
        assert result.exit_code == 0
        # --no-pager should take precedence
        assert "never" in result.stdout

    def test_info_displays_pager_info(self):
        """Test info command displays pager information."""
        from pharos_cli.cli import app

        result = self.runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Pager Information" in result.stdout
        assert "Pager Available" in result.stdout
        assert "Pager Executable" in result.stdout
        assert "Should Use Pager" in result.stdout
        assert "Current pager mode" in result.stdout


class TestPagerNotAvailableError:
    """Tests for PagerNotAvailableError exception."""

    def test_error_message(self):
        """Test PagerNotAvailableError has correct message."""
        from pharos_cli.utils.pager import PagerNotAvailableError

        error = PagerNotAvailableError("No pager available")
        assert "No pager available" in str(error)

    def test_error_is_exception(self):
        """Test PagerNotAvailableError is an Exception."""
        from pharos_cli.utils.pager import PagerNotAvailableError

        assert issubclass(PagerNotAvailableError, Exception)