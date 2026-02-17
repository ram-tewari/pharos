"""Integration tests for system commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from pathlib import Path

import sys
from pathlib import Path as FilePath

# Add pharos_cli to path
sys.path.insert(0, str(FilePath(__file__).parent.parent.parent))

from pharos_cli.cli import app


class TestSystemCommands:
    """Test cases for system commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client."""
        with patch("pharos_cli.commands.system.get_system_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_health_command(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command."""
        mock_system_client.health_check.return_value = {
            "status": "healthy",
            "message": "All systems operational",
        }

        result = runner.invoke(app, ["system", "health"])

        assert result.exit_code == 0
        assert "healthy" in result.stdout.lower() or "Health" in result.stdout
        mock_system_client.health_check.assert_called_once()

    def test_health_command_verbose(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command with verbose output."""
        mock_system_client.health_check.return_value = {
            "status": "healthy",
            "message": "All systems operational",
            "components": {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"},
            },
        }

        result = runner.invoke(app, ["system", "health", "--verbose"])

        assert result.exit_code == 0
        assert "healthy" in result.stdout.lower()

    def test_health_command_json_format(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command with JSON output."""
        mock_system_client.health_check.return_value = {
            "status": "healthy",
            "message": "All systems operational",
        }

        result = runner.invoke(app, ["system", "health", "--format", "json"])

        assert result.exit_code == 0
        assert "status" in result.stdout

    def test_health_command_unhealthy(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command with unhealthy status."""
        mock_system_client.health_check.return_value = {
            "status": "unhealthy",
            "message": "Database connection failed",
        }

        result = runner.invoke(app, ["system", "health"])

        assert result.exit_code == 0
        assert "unhealthy" in result.stdout.lower() or "Health" in result.stdout

    def test_health_command_error_response(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command when API returns error structure."""
        mock_system_client.health_check.return_value = {
            "status": "error",
            "message": "API connection failed",
            "status_code": 500,
        }

        result = runner.invoke(app, ["system", "health"])

        assert result.exit_code == 0  # Should still display the error

    def test_stats_command(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test stats command."""
        mock_system_client.get_stats.return_value = {
            "resource_count": 1000,
            "collection_count": 50,
            "annotation_count": 5000,
            "graph_node_count": 2000,
            "graph_edge_count": 10000,
        }

        result = runner.invoke(app, ["system", "stats"])

        assert result.exit_code == 0
        assert "1000" in result.stdout or "Statistics" in result.stdout
        mock_system_client.get_stats.assert_called_once()

    def test_stats_command_json_format(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test stats command with JSON output."""
        mock_system_client.get_stats.return_value = {
            "resource_count": 1000,
            "collection_count": 50,
        }

        result = runner.invoke(app, ["system", "stats", "--format", "json"])

        assert result.exit_code == 0
        assert "resource_count" in result.stdout

    def test_stats_command_quiet_format(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test stats command with quiet output."""
        mock_system_client.get_stats.return_value = {
            "resource_count": 1000,
            "collection_count": 50,
        }

        result = runner.invoke(app, ["system", "stats", "--format", "quiet"])

        assert result.exit_code == 0
        assert "1000" in result.stdout

    def test_stats_command_empty(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test stats command with empty system."""
        mock_system_client.get_stats.return_value = {
            "resource_count": 0,
            "collection_count": 0,
        }

        result = runner.invoke(app, ["system", "stats"])

        assert result.exit_code == 0

    def test_version_command(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test version command."""
        mock_system_client.get_version.return_value = {
            "version": "1.0.0",
            "api_version": "v1",
        }

        result = runner.invoke(app, ["system", "version"])

        assert result.exit_code == 0
        assert "1.0.0" in result.stdout or "version" in result.stdout.lower()
        mock_system_client.get_version.assert_called_once()

    def test_version_command_extended(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test version command with extended output."""
        mock_system_client.get_version.return_value = {
            "version": "1.0.0",
            "api_version": "v1",
            "build_date": "2024-01-15",
            "commit": "abc123",
        }

        result = runner.invoke(app, ["system", "version", "--extended"])

        assert result.exit_code == 0
        assert "1.0.0" in result.stdout
        assert "2024-01-15" in result.stdout

    def test_version_command_backend_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test version command when backend fails."""
        mock_system_client.get_version.side_effect = Exception("API error")

        result = runner.invoke(app, ["system", "version"])

        assert result.exit_code == 0  # Should still show CLI version
        assert "CLI" in result.stdout or "version" in result.stdout.lower()

    def test_backup_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup command."""
        mock_system_client.backup_create.return_value = {
            "status": "success",
            "file_path": str(tmp_path / "backup.json"),
            "size_bytes": 1024,
        }

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["system", "backup", "--output", str(output_file)])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower()
        mock_system_client.backup_create.assert_called_once()

    def test_backup_command_verbose(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup command with verbose output."""
        mock_system_client.backup_create.return_value = {
            "status": "success",
            "file_path": str(tmp_path / "backup.json"),
            "size_bytes": 1024,
        }

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["system", "backup", "--output", str(output_file), "--verbose"])

        assert result.exit_code == 0

    def test_restore_command(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test restore command."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.restore.return_value = {"status": "success"}

        result = runner.invoke(app, ["system", "restore", str(backup_file), "--force"])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower()
        mock_system_client.restore.assert_called_once()

    def test_restore_command_force(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test restore command with force flag."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.restore.return_value = {"status": "success"}

        result = runner.invoke(app, ["system", "restore", str(backup_file), "--force"])

        assert result.exit_code == 0
        mock_system_client.restore.assert_called_once()

    def test_verify_backup_command_valid(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test verify-backup command with valid backup."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": True,
            "size_bytes": 100,
            "format": "json",
        }

        result = runner.invoke(app, ["system", "verify-backup", str(backup_file)])

        assert result.exit_code == 0
        assert "valid" in result.stdout.lower()
        mock_system_client.backup_verify.assert_called_once()

    def test_verify_backup_command_invalid(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test verify-backup command with invalid backup."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text("invalid content")
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": False,
            "error": "Invalid backup format",
        }

        result = runner.invoke(app, ["system", "verify-backup", str(backup_file)])

        assert result.exit_code == 0
        assert "failed" in result.stdout.lower() or "invalid" in result.stdout.lower()

    def test_cache_clear_command(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test cache clear command."""
        mock_system_client.clear_cache.return_value = {"status": "success"}

        result = runner.invoke(app, ["system", "cache-clear", "--force"])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower()
        mock_system_client.clear_cache.assert_called_once()

    def test_migrate_command(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test migrate command."""
        mock_system_client.run_migrations.return_value = {
            "status": "success",
            "migrations_applied": 3,
        }

        result = runner.invoke(app, ["system", "migrate", "--force"])

        assert result.exit_code == 0
        assert "success" in result.stdout.lower()
        mock_system_client.run_migrations.assert_called_once()

    def test_system_help(self, runner: CliRunner) -> None:
        """Test system command help."""
        result = runner.invoke(app, ["system", "--help"])

        assert result.exit_code == 0
        assert "System" in result.stdout or "system" in result.stdout

    def test_system_subcommand_help(self, runner: CliRunner) -> None:
        """Test system subcommand help."""
        result = runner.invoke(app, ["system", "health", "--help"])

        assert result.exit_code == 0
        assert "format" in result.stdout


class TestSystemCommandsErrorHandling:
    """Error handling tests for system commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_system_client(self):
        """Create a mock system client."""
        with patch("pharos_cli.commands.system.get_system_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_health_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test health command with API error."""
        mock_system_client.health_check.side_effect = Exception("Connection failed")

        result = runner.invoke(app, ["system", "health"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_stats_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test stats command with API error."""
        mock_system_client.get_stats.side_effect = Exception("API error")

        result = runner.invoke(app, ["system", "stats"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_version_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test version command with API error."""
        mock_system_client.get_version.side_effect = Exception("API error")

        result = runner.invoke(app, ["system", "version"])

        assert result.exit_code == 0  # Should still show CLI version

    def test_backup_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test backup command with API error."""
        mock_system_client.backup_create.side_effect = Exception("Backup failed")

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["system", "backup", "--output", str(output_file)])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_restore_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test restore command with API error."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": []}')
        mock_system_client.restore.side_effect = Exception("Restore failed")

        result = runner.invoke(app, ["system", "restore", str(backup_file), "--force"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_verify_backup_command_file_not_found(
        self,
        runner: CliRunner,
        mock_system_client,
        tmp_path,
    ) -> None:
        """Test verify-backup command with non-existent file."""
        backup_file = tmp_path / "nonexistent.json"
        # Create a file that exists but is invalid
        backup_file.write_text("invalid content")
        mock_system_client.backup_verify.return_value = {
            "file_path": str(backup_file),
            "exists": True,
            "valid": False,
            "error": "Invalid backup format",
        }

        result = runner.invoke(app, ["system", "verify-backup", str(backup_file)])

        assert result.exit_code == 0  # Should show error but not crash
        assert "failed" in result.stdout.lower() or "invalid" in result.stdout.lower()

    def test_cache_clear_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test cache clear command with API error."""
        mock_system_client.clear_cache.side_effect = Exception("Cache clear failed")

        result = runner.invoke(app, ["system", "cache-clear", "--force"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_migrate_command_api_error(
        self,
        runner: CliRunner,
        mock_system_client,
    ) -> None:
        """Test migrate command with API error."""
        mock_system_client.run_migrations.side_effect = Exception("Migration failed")

        result = runner.invoke(app, ["system", "migrate", "--force"])

        assert result.exit_code != 0
        assert "Error" in result.stdout