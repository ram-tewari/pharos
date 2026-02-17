"""Unit tests for SystemClient."""

import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path
from typing import Generator

import sys
from pathlib import Path as FilePath

# Add pharos_cli to path
sys.path.insert(0, str(FilePath(__file__).parent.parent))

from pharos_cli.client.system_client import SystemClient
from pharos_cli.client.api_client import SyncAPIClient


class TestSystemClient:
    """Test cases for SystemClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def system_client(self, mock_api_client: MagicMock) -> SystemClient:
        """Create a SystemClient with mock API client."""
        return SystemClient(mock_api_client)

    def test_health_check_success(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check with successful response."""
        mock_api_client.get.return_value = {
            "status": "healthy",
            "message": "All systems operational",
            "components": {
                "database": {"status": "healthy"},
                "cache": {"status": "healthy"},
            },
        }

        result = system_client.health_check()

        mock_api_client.get.assert_called_once_with("/api/v1/health")
        assert result["status"] == "healthy"
        assert result["message"] == "All systems operational"

    def test_health_check_error_response(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check returns error structure when API fails."""
        mock_api_client.get.side_effect = Exception("API Error")

        result = system_client.health_check()

        assert result["status"] == "error"
        assert "API Error" in result["message"]

    def test_get_stats(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting system statistics."""
        mock_api_client.get.return_value = {
            "resource_count": 1000,
            "collection_count": 50,
            "annotation_count": 5000,
            "graph_node_count": 2000,
            "graph_edge_count": 10000,
            "database_size_mb": 256.5,
            "uptime_seconds": 86400,
        }

        result = system_client.get_stats()

        mock_api_client.get.assert_called_once_with("/api/v1/stats")
        assert result["resource_count"] == 1000
        assert result["collection_count"] == 50

    def test_get_version(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting version information."""
        mock_api_client.get.return_value = {
            "version": "1.0.0",
            "api_version": "v1",
            "build_date": "2024-01-15",
            "commit": "abc123",
        }

        result = system_client.get_version()

        mock_api_client.get.assert_called_once_with("/api/v1/version")
        assert result["version"] == "1.0.0"
        assert result["api_version"] == "v1"

    def test_backup_create(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test creating a backup."""
        mock_api_client.post.return_value = {
            "data": {"resources": [], "collections": []},
        }

        output_path = tmp_path / "backup.json"
        result = system_client.backup_create(output_path)

        mock_api_client.post.assert_called_once_with("/api/v1/system/backup")
        assert result["status"] == "success"
        assert result["file_path"] == str(output_path)
        assert output_path.exists()

    def test_backup_create_sql_format(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test creating a backup with SQL format."""
        mock_api_client.post.return_value = "BEGIN; CREATE TABLE test; COMMIT;"

        output_path = tmp_path / "backup.sql"
        result = system_client.backup_create(output_path)

        assert result["status"] == "success"
        assert output_path.exists()
        content = output_path.read_text()
        assert "CREATE TABLE" in content

    def test_backup_verify_valid_json(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test verifying a valid JSON backup file."""
        backup_data = {"resources": [], "collections": []}
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": [], "collections": []}')

        result = system_client.backup_verify(backup_file)

        assert result["exists"] is True
        assert result["valid"] is True
        assert result["format"] == "json"

    def test_backup_verify_valid_sql(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test verifying a valid SQL backup file."""
        backup_file = tmp_path / "backup.sql"
        backup_file.write_text("BEGIN; CREATE TABLE test (id INT); COMMIT;")

        result = system_client.backup_verify(backup_file)

        assert result["exists"] is True
        assert result["valid"] is True
        assert result["format"] == "sql"

    def test_backup_verify_file_not_found(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test verifying a non-existent backup file."""
        backup_file = tmp_path / "nonexistent.json"

        result = system_client.backup_verify(backup_file)

        assert result["exists"] is False
        assert result["valid"] is False
        assert "not found" in result["error"].lower()

    def test_backup_verify_invalid_format(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test verifying an invalid backup file."""
        backup_file = tmp_path / "backup.txt"
        backup_file.write_text("This is not valid JSON or SQL")

        result = system_client.backup_verify(backup_file)

        assert result["valid"] is False
        assert "invalid" in result["error"].lower()

    def test_restore_json(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test restoring from JSON backup."""
        backup_file = tmp_path / "backup.json"
        backup_file.write_text('{"resources": [], "collections": []}')
        mock_api_client.post.return_value = {"status": "success"}

        result = system_client.restore(backup_file)

        mock_api_client.post.assert_called_once_with(
            "/api/v1/system/restore",
            json={"resources": [], "collections": []},
        )
        assert result["status"] == "success"

    def test_restore_sql(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test restoring from SQL backup."""
        backup_file = tmp_path / "backup.sql"
        backup_file.write_text("BEGIN; CREATE TABLE test; COMMIT;")
        mock_api_client.post.return_value = {"status": "success"}

        result = system_client.restore(backup_file)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[1]["data"] == "BEGIN; CREATE TABLE test; COMMIT;"

    def test_restore_file_not_found(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test restoring from non-existent file."""
        backup_file = tmp_path / "nonexistent.sql"

        with pytest.raises(IOError, match="not found"):
            system_client.restore(backup_file)

    def test_clear_cache(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test clearing the cache."""
        mock_api_client.post.return_value = {"status": "success", "cleared_items": 150}

        result = system_client.clear_cache()

        mock_api_client.post.assert_called_once_with("/api/v1/system/cache/clear")
        assert result["status"] == "success"
        assert result["cleared_items"] == 150

    def test_run_migrations(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test running database migrations."""
        mock_api_client.post.return_value = {
            "status": "success",
            "migrations_applied": 3,
        }

        result = system_client.run_migrations()

        mock_api_client.post.assert_called_once_with("/api/v1/system/migrate")
        assert result["status"] == "success"
        assert result["migrations_applied"] == 3


class TestSystemClientEdgeCases:
    """Edge case tests for SystemClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def system_client(self, mock_api_client: MagicMock) -> SystemClient:
        """Create a SystemClient with mock API client."""
        return SystemClient(mock_api_client)

    def test_health_check_empty_response(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check with empty response."""
        mock_api_client.get.return_value = {}

        result = system_client.health_check()

        # Empty response returns empty dict
        assert result == {}

    def test_health_check_various_statuses(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check with various status values."""
        statuses = ["healthy", "ok", "ready", "up", "degraded", "warning", "unhealthy", "error", "down"]

        for status in statuses:
            mock_api_client.get.return_value = {"status": status}
            result = system_client.health_check()
            assert result["status"] == status

    def test_get_stats_empty(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting stats for empty system."""
        mock_api_client.get.return_value = {
            "resource_count": 0,
            "collection_count": 0,
        }

        result = system_client.get_stats()

        assert result["resource_count"] == 0
        assert result["collection_count"] == 0

    def test_backup_create_creates_parent_dirs(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test that backup create creates parent directories."""
        mock_api_client.post.return_value = {"data": {}}

        nested_path = tmp_path / "nested" / "deep" / "backup.json"
        result = system_client.backup_create(nested_path)

        assert result["status"] == "success"
        assert nested_path.exists()

    def test_backup_verify_large_file(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test verifying a large backup file."""
        backup_file = tmp_path / "large_backup.json"
        # Create a large JSON file with actual content
        large_data = {"data": ["item"] * 10000}
        backup_file.write_text(json.dumps(large_data))

        result = system_client.backup_verify(backup_file)

        assert result["exists"] is True
        assert result["size_bytes"] > 50000  # More than 50KB

    def test_restore_json_with_nested_structure(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
        tmp_path,
    ) -> None:
        """Test restoring JSON with nested structure."""
        backup_file = tmp_path / "backup.json"
        nested_data = {
            "resources": [{"id": 1, "metadata": {"tags": ["test"]}}],
            "collections": [{"id": 1, "name": "Test Collection"}],
        }
        backup_file.write_text('{"resources": [{"id": 1, "metadata": {"tags": ["test"]}}], "collections": [{"id": 1, "name": "Test Collection"}]}')
        mock_api_client.post.return_value = {"status": "success"}

        result = system_client.restore(backup_file)

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[1]["json"]["resources"][0]["id"] == 1

    def test_clear_cache_error(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test clear cache with API error."""
        mock_api_client.post.side_effect = Exception("Cache clear failed")

        with pytest.raises(Exception, match="Cache clear failed"):
            system_client.clear_cache()

    def test_run_migrations_error(
        self,
        system_client: SystemClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test run migrations with API error."""
        mock_api_client.post.side_effect = Exception("Migration failed")

        with pytest.raises(Exception, match="Migration failed"):
            system_client.run_migrations()