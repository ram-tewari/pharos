"""Unit tests for Chat command."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Generator
import sys
import tempfile
import os
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typer.testing import CliRunner
from pharos_cli.cli import app
from pharos_cli.commands.chat import (
    load_history,
    save_history,
    add_to_history,
    parse_command,
    show_help,
    show_welcome,
    highlight_code_blocks,
    format_answer,
    HISTORY_FILE,
)


class TestChatCommand:
    """Test cases for Chat command."""

    @pytest.fixture
    def runner(self) -> Generator[CliRunner, None, None]:
        """Create a CLI runner for testing."""
        yield CliRunner()

    @pytest.fixture
    def temp_history_file(self) -> Generator[Path, None, None]:
        """Create a temporary history file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "test_history.txt"
            # Patch the HISTORY_FILE in the chat module
            with patch("pharos_cli.commands.chat.HISTORY_FILE", history_file):
                yield history_file

    def test_chat_help_flag(
        self,
        runner: CliRunner,
    ) -> None:
        """Test chat command with --help flag."""
        result = runner.invoke(app, ["chat", "--help"])

        assert result.exit_code == 0
        # Check that chat help is displayed
        assert "Interactive chat" in result.stdout or "chat" in result.stdout

    def test_chat_command_exists(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that chat command is registered."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "chat" in result.stdout

    def test_chat_subcommand_registration(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that chat subcommands are available."""
        result = runner.invoke(app, ["chat", "--help"])

        assert result.exit_code == 0


class TestHistoryManagement:
    """Test cases for history management functions."""

    @pytest.fixture
    def temp_history_file(self) -> Generator[Path, None, None]:
        """Create a temporary history file for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "test_history.txt"
            with patch("pharos_cli.commands.chat.HISTORY_FILE", history_file):
                yield history_file

    def test_load_history_empty(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test loading empty history."""
        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            history = load_history()
            assert history == []

    def test_load_history_with_data(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test loading history with data."""
        temp_history_file.write_text("command1\ncommand2\ncommand3")

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            history = load_history()

        assert len(history) == 3
        assert "command1" in history
        assert "command2" in history
        assert "command3" in history

    def test_save_history(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test saving history."""
        history = ["cmd1", "cmd2", "cmd3"]

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            save_history(history)

        assert temp_history_file.exists()
        content = temp_history_file.read_text()
        assert "cmd1" in content
        assert "cmd2" in content
        assert "cmd3" in content

    def test_add_to_history_new_command(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test adding a new command to history."""
        history = []

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            add_to_history(history, "new command")

        assert len(history) == 1
        assert history[0] == "new command"

    def test_add_to_history_empty_command(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test adding empty command is ignored."""
        history = ["existing"]

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            add_to_history(history, "")

        assert len(history) == 1
        assert history[0] == "existing"

    def test_add_to_history_whitespace_only(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test adding whitespace-only command is ignored."""
        history = ["existing"]

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            add_to_history(history, "   ")

        assert len(history) == 1
        assert history[0] == "existing"

    def test_add_to_history_duplicate_consecutive(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test adding duplicate consecutive command is ignored."""
        history = ["same command"]

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            add_to_history(history, "same command")

        assert len(history) == 1

    def test_add_to_history_different_command(
        self,
        temp_history_file: Path,
    ) -> None:
        """Test adding different command after existing."""
        history = ["cmd1"]

        with patch("pharos_cli.commands.chat.HISTORY_FILE", temp_history_file):
            add_to_history(history, "cmd2")

        assert len(history) == 2
        assert history[0] == "cmd1"
        assert history[1] == "cmd2"


class TestCommandParsing:
    """Test cases for command parsing."""

    def test_parse_command_empty(self) -> None:
        """Test parsing empty line."""
        cmd, args = parse_command("")
        assert cmd == ""
        assert args == []

    def test_parse_command_whitespace(self) -> None:
        """Test parsing whitespace line."""
        cmd, args = parse_command("   ")
        assert cmd == ""
        assert args == []

    def test_parse_command_simple(self) -> None:
        """Test parsing simple command."""
        cmd, args = parse_command("hello world")
        assert cmd == "hello"
        assert args == ["world"]

    def test_parse_command_with_args(self) -> None:
        """Test parsing command with multiple args."""
        cmd, args = parse_command("search python --type code")
        assert cmd == "search"
        assert args == ["python", "--type", "code"]

    def test_parse_command_case_insensitive(self) -> None:
        """Test parsing command is case insensitive."""
        cmd, args = parse_command("HELLO World")
        assert cmd == "hello"
        assert args == ["World"]

    def test_parse_command_special_chars(self) -> None:
        """Test parsing command with special characters."""
        cmd, args = parse_command("ask 'what is AI?'")
        assert cmd == "ask"
        assert args == ["'what", "is", "AI?'"]


class TestHelpMessages:
    """Test cases for help message functions."""

    def test_show_help_contains_commands(self) -> None:
        """Test help message contains expected commands."""
        help_text = show_help()

        assert "/help" in help_text
        assert "/exit" in help_text
        assert "/clear" in help_text
        assert "/history" in help_text
        assert "/sources" in help_text
        assert "/strategy" in help_text

    def test_show_help_contains_tips(self) -> None:
        """Test help message contains tips."""
        help_text = show_help()

        assert "Multi-line input" in help_text
        assert "Code blocks" in help_text

    def test_show_welcome(self) -> None:
        """Test welcome message."""
        welcome = show_welcome()

        assert "Pharos Chat" in welcome
        assert "/help" in welcome


class TestCodeHighlighting:
    """Test cases for code highlighting function."""

    def test_highlight_code_blocks_python(self) -> None:
        """Test highlighting Python code blocks."""
        text = "Here is Python code:\n```python\nprint('hello')\n```"
        result = highlight_code_blocks(text)

        assert "```python" in result
        assert "print('hello')" in result

    def test_highlight_code_blocks_javascript(self) -> None:
        """Test highlighting JavaScript code blocks."""
        text = "```javascript\nconst x = 42;\n```"
        result = highlight_code_blocks(text)

        assert "```javascript" in result
        assert "const x = 42" in result

    def test_highlight_code_blocks_no_language(self) -> None:
        """Test highlighting code blocks without language."""
        text = "```\nsome code\n```"
        result = highlight_code_blocks(text)

        assert "```" in result
        assert "some code" in result

    def test_highlight_code_blocks_multiple(self) -> None:
        """Test highlighting multiple code blocks."""
        text = "```python\nprint('python')\n```\n\n```javascript\nconsole.log('js');\n```"
        result = highlight_code_blocks(text)

        assert "```python" in result
        assert "```javascript" in result

    def test_highlight_code_blocks_empty(self) -> None:
        """Test highlighting text without code blocks."""
        text = "Just plain text without code blocks."
        result = highlight_code_blocks(text)

        assert result == text

    def test_highlight_code_blocks_nested(self) -> None:
        """Test highlighting with nested backticks in code."""
        text = "```python\nprint(`hello`)\n```"
        result = highlight_code_blocks(text)

        assert "```python" in result


class TestAnswerFormatting:
    """Test cases for answer formatting function."""

    def test_format_answer_basic(self) -> None:
        """Test basic answer formatting."""
        answer = "This is the answer."
        result = format_answer(answer)

        assert result == answer

    def test_format_answer_with_sources(self) -> None:
        """Test answer formatting with sources."""
        answer = "Answer text."
        sources = [
            {"title": "Source 1", "score": 0.9},
            {"title": "Source 2", "score": 0.8},
        ]
        result = format_answer(answer, show_sources=True, sources=sources)

        assert "--- Sources ---" in result
        assert "Source 1" in result
        assert "Source 2" in result
        assert "0.90" in result or "0.9" in result

    def test_format_answer_sources_disabled(self) -> None:
        """Test answer formatting with sources disabled."""
        answer = "Answer text."
        sources = [{"title": "Source 1", "score": 0.9}]
        result = format_answer(answer, show_sources=False, sources=sources)

        assert "--- Sources ---" not in result

    def test_format_answer_empty_sources(self) -> None:
        """Test answer formatting with empty sources."""
        answer = "Answer text."
        result = format_answer(answer, show_sources=True, sources=[])

        assert "--- Sources ---" not in result

    def test_format_answer_with_code_blocks(self) -> None:
        """Test answer formatting with code blocks."""
        answer = "Here is code:\n```python\nprint('hello')\n```"
        result = format_answer(answer)

        assert "```python" in result


class TestChatIntegration:
    """Integration tests for chat command."""

    @pytest.fixture
    def runner(self) -> Generator[CliRunner, None, None]:
        """Create a CLI runner for testing."""
        yield CliRunner()

    def test_chat_command_registration(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that chat command is registered."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "chat" in result.stdout

    def test_chat_subcommand_registration(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that chat subcommands are available."""
        result = runner.invoke(app, ["chat", "--help"])

        assert result.exit_code == 0


class TestChatEdgeCases:
    """Edge case tests for chat functionality."""

    def test_parse_command_unicode(self) -> None:
        """Test parsing command with unicode."""
        cmd, args = parse_command("你好 世界")
        assert cmd == "你好"
        assert args == ["世界"]

    def test_parse_command_emoji(self) -> None:
        """Test parsing command with emoji."""
        cmd, args = parse_command("ask 🤔")
        assert cmd == "ask"
        assert args == ["🤔"]

    def test_highlight_code_blocks_very_long(self) -> None:
        """Test highlighting very long code blocks."""
        long_code = "\n".join([f"line {i}" for i in range(100)])
        text = f"```python\n{long_code}\n```"
        result = highlight_code_blocks(text)

        assert "```python" in result
        assert "line 0" in result
        assert "line 99" in result

    def test_format_answer_very_long(self) -> None:
        """Test formatting very long answers."""
        long_answer = " ".join(["word"] * 1000)
        result = format_answer(long_answer)

        assert len(result) > 0

    def test_show_help_contains_examples(self) -> None:
        """Test help message contains examples."""
        help_text = show_help()

        assert "Examples:" in help_text

    def test_history_limit(self) -> None:
        """Test that history is limited to 1000 entries."""
        # Create a history with more than 1000 entries
        long_history = [f"command {i}" for i in range(1100)]

        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "test_history.txt"
            with patch("pharos_cli.commands.chat.HISTORY_FILE", history_file):
                save_history(long_history)

            # Read back and check limit
            content = history_file.read_text()
            lines = content.splitlines()
            # Should be limited to 1000 entries
            assert len(lines) <= 1000