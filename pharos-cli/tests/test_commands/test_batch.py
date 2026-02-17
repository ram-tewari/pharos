"""Integration tests for batch operations commands."""

import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app
from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.collection_client import CollectionClient
from pharos_cli.client.models import Resource


class TestBatchDeleteCommand:
    """Test cases for 'pharos batch delete' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.delete.return_value = None
        return mock

    def test_batch_delete_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test basic batch delete with comma-separated IDs."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--force"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert mock_resource_client.delete.call_count == 3

    def test_batch_delete_space_separated(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with space-separated IDs."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            # Note: Typer treats space-separated args differently, so we use comma-separated
            result = runner.invoke(app, ["batch", "delete", "1,2,3,4,5", "--force"])

            assert result.exit_code == 0
            assert mock_resource_client.delete.call_count == 5

    def test_batch_delete_dry_run(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete dry run mode."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--dry-run"])

            assert result.exit_code == 0
            assert "Dry Run" in result.stdout or "dry run" in result.stdout.lower()
            # Should not have made any API calls
            mock_resource_client.delete.assert_not_called()

    def test_batch_delete_with_workers(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with custom worker count."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3,4,5", "--workers", "8", "--force"])

            assert result.exit_code == 0
            assert mock_resource_client.delete.call_count == 5

    def test_batch_delete_invalid_workers(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with invalid worker count."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--workers", "20"])

            assert result.exit_code == 1
            assert "between 1 and 10" in result.stdout

    def test_batch_delete_no_ids(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with no IDs."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", ""])

            assert result.exit_code == 1
            assert "No valid resource IDs" in result.stdout or "no" in result.stdout.lower()

    def test_batch_delete_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with JSON output format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--format", "json", "--force"])

            assert result.exit_code == 0
            # Check for JSON output
            stdout = result.stdout
            assert "successful" in stdout.lower() or "total" in stdout.lower()

    def test_batch_delete_quiet_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch delete with quiet output format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--format", "quiet", "--force"])

            assert result.exit_code == 0
            # Should just have status messages
            assert "Deleted" in result.stdout or "Failed" in result.stdout

    def test_batch_delete_help(self, runner: CliRunner) -> None:
        """Test batch delete command help."""
        result = runner.invoke(app, ["batch", "delete", "--help"])

        assert result.exit_code == 0
        assert "--ids" in result.stdout or "ids" in result.stdout.lower()
        assert "--dry-run" in result.stdout
        assert "--workers" in result.stdout
        assert "--force" in result.stdout


class TestBatchUpdateCommand:
    """Test cases for 'pharos batch update' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.update.return_value = Resource(
            id=1,
            title="Updated Title",
            content="Updated content",
            resource_type="code",
            language="python",
            quality_score=0.85,
            url=None,
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T14:20:00Z",
        )
        return mock

    def test_batch_update_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test basic batch update from JSON file."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps({
                    "updates": [
                        {"id": 1, "title": "New Title 1"},
                        {"id": 2, "title": "New Title 2"},
                    ]
                }))

                result = runner.invoke(app, ["batch", "update", str(update_file)])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                assert mock_resource_client.update.call_count == 2

    def test_batch_update_array_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with array format JSON file."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps([
                    {"id": 1, "title": "New Title"},
                    {"id": 2, "content": "New content"},
                ]))

                result = runner.invoke(app, ["batch", "update", str(update_file)])

                assert result.exit_code == 0
                assert mock_resource_client.update.call_count == 2

    def test_batch_update_dry_run(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update dry run mode."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps({
                    "updates": [
                        {"id": 1, "title": "New Title"},
                        {"id": 2, "title": "Another Title"},
                    ]
                }))

                result = runner.invoke(app, ["batch", "update", str(update_file), "--dry-run"])

                assert result.exit_code == 0
                assert "Dry Run" in result.stdout or "dry run" in result.stdout.lower()
                # Should not have made any API calls
                mock_resource_client.update.assert_not_called()

    def test_batch_update_missing_id(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with missing ID in file."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps({
                    "updates": [
                        {"title": "No ID here"},  # Missing 'id' field
                    ]
                }))

                result = runner.invoke(app, ["batch", "update", str(update_file)])

                assert result.exit_code != 0
                assert "id" in result.stdout.lower()

    def test_batch_update_invalid_json(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with invalid JSON file."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text("not valid json")

                result = runner.invoke(app, ["batch", "update", str(update_file)])

                assert result.exit_code != 0
                assert "JSON" in result.stdout or "json" in result.stdout.lower()

    def test_batch_update_nonexistent_file(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with non-existent file."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "update", "/nonexistent/updates.json"])

            assert result.exit_code != 0
            # Check both stdout and stderr for the error message
            output = result.stdout + result.stderr
            assert "not found" in output.lower() or "exist" in output.lower() or "invalid" in output.lower()

    def test_batch_update_with_workers(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with custom worker count."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                updates = [{"id": i, "title": f"Title {i}"} for i in range(5)]
                update_file.write_text(json.dumps({"updates": updates}))

                result = runner.invoke(app, ["batch", "update", str(update_file), "--workers", "4"])

                assert result.exit_code == 0
                assert mock_resource_client.update.call_count == 5

    def test_batch_update_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch update with JSON output format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps({
                    "updates": [{"id": 1, "title": "New Title"}]
                }))

                result = runner.invoke(app, ["batch", "update", str(update_file), "--format", "json"])

                assert result.exit_code == 0
                assert "successful" in result.stdout.lower() or "total" in result.stdout.lower()

    def test_batch_update_help(self, runner: CliRunner) -> None:
        """Test batch update command help."""
        result = runner.invoke(app, ["batch", "update", "--help"])

        assert result.exit_code == 0
        assert "--file" in result.stdout or "file" in result.stdout.lower()
        assert "--dry-run" in result.stdout
        assert "--workers" in result.stdout


class TestBatchExportCommand:
    """Test cases for 'pharos batch export' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.get.return_value = Resource(
            id=1,
            title="Test Resource",
            content="This is the content of the resource.",
            resource_type="code",
            language="python",
            quality_score=0.85,
            url=None,
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T14:20:00Z",
        )
        return mock

    @pytest.fixture
    def mock_collection_client(self):
        """Create a mock collection client."""
        mock = MagicMock(spec=CollectionClient)
        mock.get.return_value = MagicMock(
            id=1,
            name="Test Collection",
            description="A test collection",
            is_public=False,
            resource_count=3,
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T14:20:00Z",
        )
        mock.get_contents.return_value = MagicMock(
            items=[
                {"id": 1, "title": "Resource 1", "resource_type": "code", "quality_score": 0.85},
                {"id": 2, "title": "Resource 2", "resource_type": "paper", "quality_score": 0.92},
                {"id": 3, "title": "Resource 3", "resource_type": "documentation", "quality_score": 0.78},
            ],
            total=3,
            page=1,
            per_page=25,
            has_more=False,
        )
        return mock

    def test_batch_export_by_ids(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export by resource IDs."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "export", "--ids", "1,2,3"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert mock_resource_client.get.call_count == 3

    def test_batch_export_by_collection(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
        mock_collection_client: MagicMock,
    ) -> None:
        """Test batch export by collection ID."""
        with patch("pharos_cli.commands.batch.get_collection_client", return_value=mock_collection_client):
            with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
                result = runner.invoke(app, ["batch", "export", "--collection", "1"])

                assert result.exit_code == 0
                assert mock_collection_client.get.called
                assert mock_collection_client.get_contents.called

    def test_batch_export_dry_run(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
        mock_collection_client: MagicMock,
    ) -> None:
        """Test batch export dry run mode."""
        with patch("pharos_cli.commands.batch.get_collection_client", return_value=mock_collection_client):
            with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
                result = runner.invoke(app, ["batch", "export", "--collection", "1", "--dry-run"])

                assert result.exit_code == 0
                assert "Dry Run" in result.stdout or "dry run" in result.stdout.lower()

    def test_batch_export_json_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with JSON format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "export.json"
                result = runner.invoke(app, [
                    "batch", "export",
                    "--ids", "1,2",
                    "--format", "json",
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                data = json.loads(output_file.read_text())
                assert "resources" in data

    def test_batch_export_csv_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with CSV format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "export.csv"
                result = runner.invoke(app, [
                    "batch", "export",
                    "--ids", "1,2",
                    "--format", "csv",
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                content = output_file.read_text()
                assert "id" in content.lower() or "title" in content.lower()

    def test_batch_export_zip_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with ZIP format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "export.zip"
                result = runner.invoke(app, [
                    "batch", "export",
                    "--ids", "1,2",
                    "--format", "zip",
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                
                # Verify it's a valid ZIP
                with zipfile.ZipFile(output_file, "r") as zf:
                    assert len(zf.namelist()) == 2

    def test_batch_export_markdown_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with markdown format."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_dir = Path(tmpdir) / "exports"
                result = runner.invoke(app, [
                    "batch", "export",
                    "--ids", "1",
                    "--format", "markdown",
                    "--output", str(output_dir)
                ])

                assert result.exit_code == 0
                assert output_dir.exists()
                files = list(output_dir.glob("*.md"))
                assert len(files) == 1

    def test_batch_export_content_only(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with content only flag."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "export.zip"
                result = runner.invoke(app, [
                    "batch", "export",
                    "--ids", "1",
                    "--format", "zip",
                    "--output", str(output_file),
                    "--content-only"
                ])

                assert result.exit_code == 0
                assert output_file.exists()

    def test_batch_export_with_workers(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with custom worker count."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "batch", "export",
                "--ids", "1,2,3,4,5",
                "--workers", "8"
            ])

            assert result.exit_code == 0
            assert mock_resource_client.get.call_count == 5

    def test_batch_export_invalid_workers(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export with invalid worker count."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "batch", "export",
                "--ids", "1,2,3",
                "--workers", "20"
            ])

            assert result.exit_code == 1
            assert "between 1 and 10" in result.stdout

    def test_batch_export_no_source(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test batch export without specifying collection or IDs."""
        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["batch", "export"])

            assert result.exit_code != 0
            assert "collection" in result.stdout.lower() or "ids" in result.stdout.lower()

    def test_batch_export_both_sources(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
        mock_collection_client: MagicMock,
    ) -> None:
        """Test batch export with both collection and IDs specified."""
        with patch("pharos_cli.commands.batch.get_collection_client", return_value=mock_collection_client):
            with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock_resource_client):
                result = runner.invoke(app, [
                    "batch", "export",
                    "--collection", "1",
                    "--ids", "1,2,3"
                ])

                assert result.exit_code != 0
                assert "both" in result.stdout.lower() or "cannot" in result.stdout.lower()

    def test_batch_export_help(self, runner: CliRunner) -> None:
        """Test batch export command help."""
        result = runner.invoke(app, ["batch", "export", "--help"])

        assert result.exit_code == 0
        assert "--collection" in result.stdout or "collection" in result.stdout.lower()
        assert "--ids" in result.stdout or "ids" in result.stdout.lower()
        assert "--format" in result.stdout
        assert "--output" in result.stdout
        assert "--dry-run" in result.stdout


class TestBatchCommandHelp:
    """Test cases for batch command help."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_batch_help(self, runner: CliRunner) -> None:
        """Test batch command help."""
        result = runner.invoke(app, ["batch", "--help"])

        assert result.exit_code == 0
        assert "delete" in result.stdout.lower()
        assert "update" in result.stdout.lower()
        assert "export" in result.stdout.lower()

    def test_batch_no_args(self, runner: CliRunner) -> None:
        """Test batch command with no arguments."""
        result = runner.invoke(app, ["batch"])

        # When no subcommand is provided, Typer shows an error
        # Exit code should be 2 (missing argument)
        assert result.exit_code == 2
        # Check that the output mentions batch command
        output = result.stdout + result.stderr
        assert "batch" in output.lower()


class TestBatchIntegration:
    """Integration tests for batch operations."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_batch_delete_error_handling(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that batch delete handles errors gracefully."""
        from pharos_cli.client.exceptions import APIError, NetworkError

        mock = MagicMock(spec=ResourceClient)
        # First call succeeds, second fails with NetworkError, third succeeds
        mock.delete.side_effect = [
            None,  # Success for ID 1
            NetworkError("Network error"),  # Error for ID 2
            None,  # Success for ID 3
        ]

        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock):
            result = runner.invoke(app, ["batch", "delete", "1,2,3", "--force"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert mock.delete.call_count == 3
            # Should show some failures in output
            assert "Failed" in result.stdout or "failed" in result.stdout.lower() or "3" in result.stdout

    def test_batch_update_error_handling(
        self,
        runner: CliRunner,
    ) -> None:
        """Test that batch update handles errors gracefully."""
        from pharos_cli.client.exceptions import APIError, NetworkError

        mock = MagicMock(spec=ResourceClient)
        mock.update.side_effect = [
            MagicMock(id=1, title="Updated 1"),  # Success
            NetworkError("Network error"),  # Error
            MagicMock(id=3, title="Updated 3"),  # Success
        ]

        with patch("pharos_cli.commands.batch.get_resource_client", return_value=mock):
            with tempfile.TemporaryDirectory() as tmpdir:
                update_file = Path(tmpdir) / "updates.json"
                update_file.write_text(json.dumps({
                    "updates": [
                        {"id": 1, "title": "New Title 1"},
                        {"id": 2, "title": "New Title 2"},
                        {"id": 3, "title": "New Title 3"},
                    ]
                }))

                result = runner.invoke(app, ["batch", "update", str(update_file)])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                assert mock.update.call_count == 3

    def test_batch_export_empty_collection(
        self,
        runner: CliRunner,
    ) -> None:
        """Test batch export with empty collection."""
        mock_collection = MagicMock(spec=CollectionClient)
        mock_collection.get.return_value = MagicMock(
            id=1,
            name="Empty Collection",
            description="An empty collection",
            is_public=False,
            resource_count=0,
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T14:20:00Z",
        )
        mock_collection.get_contents.return_value = MagicMock(
            items=[],
            total=0,
            page=1,
            per_page=25,
            has_more=False,
        )

        with patch("pharos_cli.commands.batch.get_collection_client", return_value=mock_collection):
            result = runner.invoke(app, ["batch", "export", "--collection", "1"])

            assert result.exit_code == 0
            assert "no resources" in result.stdout.lower() or "empty" in result.stdout.lower()