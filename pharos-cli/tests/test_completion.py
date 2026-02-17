"""Tests for shell completion functionality."""

import pytest
import sys
from pathlib import Path

# Add scripts/completion to path for imports
completion_scripts_path = Path(__file__).parent.parent / "scripts" / "completion"
sys.path.insert(0, str(completion_scripts_path))


class TestBashCompletion:
    """Tests for bash completion script generation."""

    def test_bash_completion_script_is_generated(self):
        """Test that bash completion script can be generated."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        assert script is not None
        assert len(script) > 0

    def test_bash_completion_has_pharos_command(self):
        """Test that bash completion includes pharos command."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        assert "pharos" in script
        assert "complete -F _pharos_completions pharos" in script

    def test_bash_completion_has_main_commands(self):
        """Test that bash completion includes main commands."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Check for main command groups
        commands = [
            "auth", "config", "resource", "collection", "search",
            "graph", "batch", "chat", "recommend", "annotate",
            "quality", "taxonomy", "code", "ask", "system", "backup"
        ]
        
        for cmd in commands:
            assert cmd in script, f"Missing command: {cmd}"

    def test_bash_completion_has_subcommands(self):
        """Test that bash completion includes subcommands."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Check for subcommand lists
        assert "resource_cmds=" in script
        assert "collection_cmds=" in script
        assert "auth_cmds=" in script
        assert "graph_cmds=" in script

    def test_bash_completion_script_is_valid_bash(self):
        """Test that bash completion script is valid bash syntax."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Basic syntax checks
        assert script.startswith("#")
        assert "_pharos_completions()" in script
        assert "complete -F" in script

    def test_bash_completion_handles_file_arguments(self):
        """Test that bash completion handles file arguments."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Check for _filedir usage
        assert "_filedir" in script

    def test_bash_completion_handles_directory_arguments(self):
        """Test that bash completion handles directory arguments."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Check for _filedir -d usage
        assert "_filedir -d" in script


class TestZshCompletion:
    """Tests for zsh completion script generation."""

    def test_zsh_completion_script_is_generated(self):
        """Test that zsh completion script can be generated."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        assert script is not None
        assert len(script) > 0

    def test_zsh_completion_has_autoload(self):
        """Test that zsh completion uses autoload."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        assert "autoload -U compinit" in script
        assert "compinit" in script

    def test_zsh_completion_has_main_commands(self):
        """Test that zsh completion includes main commands."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Check for main command groups
        assert "pharos_commands=(" in script

    def test_zsh_completion_has_subcommands(self):
        """Test that zsh completion includes subcommands."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Check for subcommand lists
        assert "pharos_resource_commands=(" in script
        assert "pharos_collection_commands=(" in script
        assert "pharos_auth_commands=(" in script

    def test_zsh_completion_has_descriptions(self):
        """Test that zsh completion includes command descriptions."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Check for description format
        assert 'Authentication commands' in script
        assert 'Resource management commands' in script
        assert 'Collection management commands' in script

    def test_zsh_completion_script_is_valid_zsh(self):
        """Test that zsh completion script is valid zsh syntax."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Basic syntax checks
        assert "compdef _pharos pharos" in script
        assert "_pharos()" in script

    def test_zsh_completion_has_helper_functions(self):
        """Test that zsh completion has helper functions."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Check for helper functions
        assert "_pharos_resource_ids" in script
        assert "_pharos_collection_ids" in script
        assert "_pharos_files" in script
        assert "_pharos_directories" in script


class TestFishCompletion:
    """Tests for fish completion script generation."""

    def test_fish_completion_script_is_generated(self):
        """Test that fish completion script can be generated."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        assert script is not None
        assert len(script) > 0

    def test_fish_completion_has_main_command(self):
        """Test that fish completion includes main command."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        assert "complete -c pharos" in script

    def test_fish_completion_has_main_commands(self):
        """Test that fish completion includes main commands."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Check for main command groups - fish uses combined -a flags
        commands = [
            "auth", "config", "resource", "collection", "search",
            "graph", "batch", "chat", "recommend", "annotate",
            "quality", "taxonomy", "code", "ask", "system", "backup"
        ]
        
        # Check that all commands are present in the script
        for cmd in commands:
            assert cmd in script, f"Missing command: {cmd}"

    def test_fish_completion_has_options(self):
        """Test that fish completion includes options."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Check for common options
        assert "-l color" in script
        assert "-l no-color" in script
        assert "-l help" in script
        assert "-l version" in script

    def test_fish_completion_has_descriptions(self):
        """Test that fish completion includes descriptions."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Check for description format
        assert "-d 'Color output'" in script
        assert "-d 'Show help'" in script
        assert "-d 'Authentication commands'" in script

    def test_fish_completion_script_is_valid_fish(self):
        """Test that fish completion script is valid fish syntax."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Basic syntax checks
        assert script.startswith("#")
        assert "-c pharos" in script
        assert "-f" in script  # Fish uses -f for file-type completions

    def test_fish_completion_has_file_and_directory_completion(self):
        """Test that fish completion handles files and directories."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Check for file and directory completion
        assert "-r" in script  # Fish uses -r for requirefile
        assert "-a" in script  # Fish uses -a for arguments


class TestCompletionIntegration:
    """Integration tests for completion functionality."""

    def test_all_completion_scripts_are_different(self):
        """Test that completion scripts for different shells are different."""
        from bash import get_bash_completion_script
        from zsh import get_zsh_completion_script
        from fish import get_fish_completion_script
        
        bash_script = get_bash_completion_script()
        zsh_script = get_zsh_completion_script()
        fish_script = get_fish_completion_script()
        
        # All scripts should be different
        assert bash_script != zsh_script
        assert bash_script != fish_script
        assert zsh_script != fish_script

    def test_all_completion_scripts_have_common_elements(self):
        """Test that all completion scripts include common elements."""
        from bash import get_bash_completion_script
        from zsh import get_zsh_completion_script
        from fish import get_fish_completion_script
        
        bash_script = get_bash_completion_script()
        zsh_script = get_zsh_completion_script()
        fish_script = get_fish_completion_script()
        
        # All scripts should mention pharos
        assert "pharos" in bash_script
        assert "pharos" in zsh_script
        assert "pharos" in fish_script

    def test_all_completion_scripts_cover_all_commands(self):
        """Test that all completion scripts cover all main commands."""
        from bash import get_bash_completion_script
        from zsh import get_zsh_completion_script
        from fish import get_fish_completion_script
        
        bash_script = get_bash_completion_script()
        zsh_script = get_zsh_completion_script()
        fish_script = get_fish_completion_script()
        
        # Commands that should be in all scripts
        commands = ["resource", "collection", "search", "graph", "annotate"]
        
        for cmd in commands:
            assert cmd in bash_script, f"Bash missing: {cmd}"
            assert cmd in zsh_script, f"Zsh missing: {cmd}"
            assert cmd in fish_script, f"Fish missing: {cmd}"


class TestCompletionScriptOutput:
    """Tests for completion script output format."""

    def test_bash_completion_script_is_executable_format(self):
        """Test that bash completion script is in executable format."""
        from bash import get_bash_completion_script
        
        script = get_bash_completion_script()
        
        # Should start with a comment (shebang or comment)
        assert script.strip().startswith("#")

    def test_zsh_completion_script_has_compdef(self):
        """Test that zsh completion script has compdef."""
        from zsh import get_zsh_completion_script
        
        script = get_zsh_completion_script()
        
        # Should have compdef for registration
        assert "compdef" in script

    def test_fish_completion_script_uses_complete_command(self):
        """Test that fish completion script uses complete command."""
        from fish import get_fish_completion_script
        
        script = get_fish_completion_script()
        
        # Should use complete command
        assert "complete -c" in script


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
class TestCompletionCommand:
    """Tests for the CLI completion command."""

    def test_completion_command_exists(self):
        """Test that completion command exists in CLI."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["--help"])
        
        assert result.exit_code == 0
        assert "completion" in result.stdout

    def test_completion_bash(self):
        """Test bash completion generation."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["completion", "bash"])
        
        assert result.exit_code == 0
        assert "pharos" in result.stdout
        # Typer uses _pharos_completion (not _pharos_completions)
        assert "_pharos_completion" in result.stdout

    def test_completion_zsh(self):
        """Test zsh completion generation."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["completion", "zsh"])
        
        assert result.exit_code == 0
        assert "pharos" in result.stdout
        assert "compdef" in result.stdout

    def test_completion_fish(self):
        """Test fish completion generation."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["completion", "fish"])
        
        assert result.exit_code == 0
        # Typer uses "complete --command pharos" (not "complete -c pharos")
        assert "complete --command pharos" in result.stdout

    def test_completion_no_args(self):
        """Test completion command with no arguments."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["completion"])
        
        # Should exit with code 0 and show usage
        assert result.exit_code == 0
        assert "bash" in result.stdout or "zsh" in result.stdout or "fish" in result.stdout

    def test_completion_invalid_shell(self):
        """Test completion command with invalid shell."""
        from typer.testing import CliRunner
        from pharos_cli.cli import app
        
        runner = CliRunner()
        result = runner.invoke(app, ["completion", "invalid"])
        
        # Should exit with error
        assert result.exit_code != 0


class TestInstallScript:
    """Tests for the installation script."""

    def test_install_script_exists(self):
        """Test that install script exists."""
        import os
        script_path = Path(__file__).parent.parent / "scripts" / "install_completion.sh"
        assert script_path.exists()
        assert os.path.isfile(script_path)

    def test_install_script_is_executable(self):
        """Test that install script is executable."""
        import os
        script_path = Path(__file__).parent.parent / "scripts" / "install_completion.sh"
        # Check that the script has a shebang
        with open(script_path, 'r') as f:
            first_line = f.readline()
        assert first_line.startswith("#!")

    def test_install_script_has_all_shells(self):
        """Test that install script supports all shells."""
        script_path = Path(__file__).parent.parent / "scripts" / "install_completion.sh"
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert "bash" in content
        assert "zsh" in content
        assert "fish" in content
        assert "all" in content

    def test_install_script_has_help(self):
        """Test that install script has help option."""
        script_path = Path(__file__).parent.parent / "scripts" / "install_completion.sh"
        with open(script_path, 'r') as f:
            content = f.read()
        
        assert "--help" in content or "usage" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])