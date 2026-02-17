"""Integration tests for backup commands."""

import json
import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from pathlib import Path

import sys
from pathlib import Path as FilePath

# Add pharos_cli to path
sys.path.insert(0, str(FilePath(__file__).parent.parent.parent))

from pharos_cli.cli import app


class TestBackupCommands:
    """Test cases for backup commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client."""
        with patch("pharos_cli.commands.backup.get_system_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_backup_create_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command."""
        mock_system_client.backup_create.return_value = {
            "status": "success",
            "file_path": str(tmp_path / "backup.json"),
            "size_bytes": 1024,
        }
        mock_system_client.backup_verify.return_value = {
            "valid": True,
            "size_bytes": 1024,
            "format": "json",
        }

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file)])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower() or "Backup" in result.stdout
        mock_system_client.backup_create.assert_called_once()

    def test_backup_create_command_with_format(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command with format option."""
        mock_system_client.backup_create.return_value = {
            "status": "success",
            "file_path": str(tmp_path / "backup.json"),
            "size_bytes": 1024,
        }
        mock_system_client.backup_verify.return_value = {
            "valid": True,
            "size_bytes": 1024,
            "format": "json",
        }

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file), "--format", "json"])

        assert result.exit_code == 0

    def test_backup_create_command_no_verify(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command with --no-verify."""
        mock_system_client.backup_create.return_value = {
            "status": "success",
            "file_path": str(tmp_path / "backup.json"),
            "size_bytes": 1024,
        }

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file), "--no-verify"])

        assert result.exit_code == 0
        # backup_verify should not be called when --no-verify is used
        mock_system_client.backup_verify.assert_not_called()

    def test_backup_create_command_file_exists(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command when output file already exists."""
        output_file = tmp_path / "backup.json"
        output_file.write_text("existing content")

        result = runner.invoke(app, ["backup", "create", "--output", str(output_file)])

        assert result.exit_code != 0
        assert "exists" in result.stdout.lower() or "Error" in result.stdout

    def test_backup_verify_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup verify command."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }

        result = runner.invoke(app, ["backup", "verify", str(backup_file)])

        assert result.exit_code == 0
        assert "valid" in result.stdout.lower() or "Backup" in result.stdout
        mock_system_client.backup_verify.assert_called_once()

    def test_backup_verify_command_detailed(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup verify command with detailed output."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }

        result = runner.invoke(app, ["backup", "verify", str(backup_file), "--detailed"])

        assert result.exit_code == 0

    def test_backup_verify_command_invalid(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup verify command with invalid backup."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text("invalid content")
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": False,
            "error": "Invalid backup format",
        }

        result = runner.invoke(app, ["backup", "verify", str(backup_file)])

        assert result.exit_code != 0
        assert "failed" in result.stdout.lower() or "invalid" in result.stdout.lower()

    def test_backup_restore_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup restore command."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }
        mock_system_client.restore.return_value = {"status": "success"}

        result = runner.invoke(app, ["backup", "restore", str(backup_file), "--force"])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower() or "Restore" in result.stdout
        mock_system_client.restore.assert_called_once()

    def test_backup_restore_command_with_verify(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup restore command with verification."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }
        mock_system_client.restore.return_value = {"status": "success"}

        result = runner.invoke(app, ["backup", "restore", str(backup_file), "--force", "--verify"])

        assert result.exit_code == 0
        mock_system_client.backup_verify.assert_called_once()

    def test_backup_restore_command_invalid_backup(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup restore command with invalid backup."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text("invalid content")
        mock_system_client.backup_verify.return_value = {
            "valid": False,
            "error": "Invalid backup format",
        }

        result = runner.invoke(app, ["backup", "restore", str(backup_file), "--force"])

        # Should still proceed with --force
        assert result.exit_code == 0

    def test_backup_info_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup info command."""
        backup_file = tmp_path / "backup.json"
        backup_data = {"resources": [], "collections": []}
        backup_file.write_text(json.dumps(backup_data))

        result = runner.invoke(app, ["backup", "info", str(backup_file)])

        assert result.exit_code == 0
        assert "backup" in result.stdout.lower() or "info" in result.stdout.lower()

    def test_backup_info_command_sql(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup info command with SQL file."""
        backup_file = tmp_path / "backup.sql"
        backup_file.write_text("BEGIN; CREATE TABLE test; COMMIT;")

        result = runner.invoke(app, ["backup", "info", str(backup_file)])

        assert result.exit_code == 0

    def test_backup_help(self, runner: CliRunner) -> None:
        """Test backup command help."""
        result = runner.invoke(app, ["backup", "--help"])

        assert result.exit_code == 0
        assert "backup" in result.stdout.lower() or "Backup" in result.stdout

    def test_backup_create_help(self, runner: CliRunner) -> None:
        """Test backup create command help."""
        result = runner.invoke(app, ["backup", "create", "--help"])

        assert result.exit_code == 0
        assert "output" in result.stdout.lower() or "format" in result.stdout.lower()

    def test_backup_verify_help(self, runner: CliRunner) -> None:
        """Test backup verify command help."""
        result = runner.invoke(app, ["backup", "verify", "--help"])

        assert result.exit_code == 0
        assert "detailed" in result.stdout.lower()

    def test_backup_restore_help(self, runner: CliRunner) -> None:
        """Test backup restore command help."""
        result = runner.invoke(app, ["backup", "restore", "--help"])

        assert result.exit_code == 0
        assert "force" in result.stdout.lower() or "verify" in result.stdout.lower()

    def test_backup_info_help(self, runner: CliRunner) -> None:
        """Test backup info command help."""
        result = runner.invoke(app, ["backup", "info", "--help"])

        assert result.exit_code == 0


class TestBackupCommandsErrorHandling:
    """Error handling tests for backup commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client."""
        with patch("pharos_cli.commands.backup.get_system_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_backup_create_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command with API error."""
        from pharos_cli.client.exceptions import APIError

        mock_system_client.backup_create.side_effect = APIError(500, "Backup failed")

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file)])

        assert result.exit_code != 0
        assert "Error" in result.stdout or "API" in result.stdout

    def test_backup_create_command_network_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command with network error."""
        from pharos_cli.client.exceptions import NetworkError

        mock_system_client.backup_create.side_effect = NetworkError("Connection failed")

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file)])

        assert result.exit_code != 0
        assert "Error" in result.stdout or "Network" in result.stdout

    def test_backup_create_command_io_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup create command with IO error."""
        mock_system_client.backup_create.side_effect = IOError("Could not write backup file: permission denied")

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["backup", "create", "--output", str(output_file)])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_backup_verify_command_file_not_found(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup verify command with non-existent file."""
        backup_file = tmp_path / "nonexistent.json"

        result = runner.invoke(app, ["backup", "verify", str(backup_file)])

        # Typer validates file existence before the command runs
        # So the exit code should be 2 (typer usage error)
        assert result.exit_code != 0

    def test_backup_restore_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup restore command with API error."""
        from pharos_cli.client.exceptions import APIError

        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }
        mock_system_client.restore.side_effect = APIError(500, "Restore failed")

        result = runner.invoke(app, ["backup", "restore", str(backup_file), "--force"])

        assert result.exit_code != 0
        assert "Error" in result.stdout or "API" in result.stdout

    def test_backup_restore_command_file_not_found(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup restore command with non-existent file."""
        backup_file = tmp_path / "nonexistent.json"

        result = runner.invoke(app, ["backup", "restore", str(backup_file), "--force"])

        # Typer validates file existence before the command runs
        # So the exit code should be 2 (typer usage error)
        assert result.exit_code != 0

    def test_backup_info_command_file_not_found(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup info command with non-existent file."""
        backup_file = tmp_path / "nonexistent.json"

        result = runner.invoke(app, ["backup", "info", str(backup_file)])

        # Typer validates file existence before the command runs
        # So the exit code should be 2 (typer usage error)
        assert result.exit_code != 0


class TestBackupCommandsAliases:
    """Tests for backup command aliases."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client."""
        with patch("pharos_cli.commands.backup.get_system_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_backup_check_alias(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup check alias command."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }

        result = runner.invoke(app, ["backup", "check", str(backup_file)])

        assert result.exit_code == 0
        mock_system_client.backup_verify.assert_called_once()

    def test_backup_validate_alias(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup validate alias command."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }

        result = runner.invoke(app, ["backup", "validate", str(backup_file)])

        assert result.exit_code == 0
        mock_system_client.backup_verify.assert_called_once()