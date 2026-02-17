"""Integration tests for resource batch operations (import/export)."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app
from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.models import Resource


class TestResourceImportCommand:
    """Test cases for 'pharos resource import' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.create.return_value = {
            "id": 1,
            "title": "Test Resource",
            "content": "Test content",
            "resource_type": "code",
            "language": "python",
        }
        return mock

    def test_import_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing a single file."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_file = Path(tmpdir) / "test.py"
                temp_file.write_text("def hello():\n    print('Hello')")

                result = runner.invoke(app, ["resource", "import", tmpdir])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                assert "Import Summary" in result.stdout or "imported" in result.stdout.lower()
                mock_resource_client.create.assert_called()

    def test_import_recursive(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing files recursively."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create nested directory structure
                subdir = Path(tmpdir) / "subdir"
                subdir.mkdir()
                (subdir / "nested.py").write_text("def nested():\n    pass")

                result = runner.invoke(app, ["resource", "import", tmpdir, "--recursive"])

                assert result.exit_code == 0
                # Should find the nested file
                assert mock_resource_client.create.called

    def test_import_with_pattern(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing with custom pattern."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create files with different extensions
                (Path(tmpdir) / "file.py").write_text("print('python')")
                (Path(tmpdir) / "file.js").write_text("console.log('js')")

                result = runner.invoke(app, ["resource", "import", tmpdir, "--pattern", "*.py"])

                assert result.exit_code == 0
                # Should only import .py files
                call_count = mock_resource_client.create.call_count
                assert call_count == 1

    def test_import_with_type(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing with explicit resource type."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_file = Path(tmpdir) / "test.txt"
                temp_file.write_text("Some text content")

                result = runner.invoke(app, [
                    "resource", "import", tmpdir,
                    "--type", "documentation"
                ])

                assert result.exit_code == 0

                # Verify the type was passed
                call_kwargs = mock_resource_client.create.call_args[1]
                assert call_kwargs["resource_type"] == "documentation"

    def test_import_with_language(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing with explicit language."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_file = Path(tmpdir) / "test.py"
                temp_file.write_text("print('hello')")

                result = runner.invoke(app, [
                    "resource", "import", tmpdir,
                    "--language", "python"
                ])

                assert result.exit_code == 0

                call_kwargs = mock_resource_client.create.call_args[1]
                assert call_kwargs["language"] == "python"

    def test_import_parallel(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test importing with parallel workers."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create multiple files
                for i in range(5):
                    (Path(tmpdir) / f"file{i}.py").write_text(f"print({i})")

                result = runner.invoke(app, [
                    "resource", "import", tmpdir,
                    "--workers", "4"
                ])

                assert result.exit_code == 0
                assert mock_resource_client.create.call_count == 5

    def test_import_dry_run(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test import dry run mode."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.py").write_text("print('test')")

                result = runner.invoke(app, ["resource", "import", tmpdir, "--dry-run"])

                assert result.exit_code == 0
                assert "Dry run" in result.stdout or "dry run" in result.stdout.lower()
                # Should not actually import
                mock_resource_client.create.assert_not_called()

    def test_import_no_files(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test import when no files match."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                result = runner.invoke(app, ["resource", "import", tmpdir, "--pattern", "*.nonexistent"])

                assert result.exit_code == 0
                assert "No files found" in result.stdout

    def test_import_workers_validation(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test workers parameter validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = runner.invoke(app, ["resource", "import", tmpdir, "--workers", "0"])

            assert result.exit_code == 1
            assert "Workers must be between 1 and 10" in result.stdout

    def test_import_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test import with JSON output format."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.py").write_text("print('test')")

                result = runner.invoke(app, ["resource", "import", tmpdir, "--format", "json"])

                assert result.exit_code == 0
                # Extract JSON from output (may have ANSI codes and progress bar output)
                import json
                # Find the JSON object in the output
                json_start = result.stdout.find("{")
                assert json_start != -1, "JSON output not found"
                data = json.loads(result.stdout[json_start:])
                assert "successful" in data or "total" in data

    def test_import_quiet_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test import with quiet output format."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                (Path(tmpdir) / "test.py").write_text("print('test')")

                result = runner.invoke(app, ["resource", "import", tmpdir, "--format", "quiet"])

                assert result.exit_code == 0
                # Should just print resource IDs
                assert "1" in result.stdout


class TestResourceExportCommand:
    """Test cases for 'pharos resource export' command."""

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
            content="Test content here",
            resource_type="code",
            language="python",
            quality_score=0.85,
            url=None,
            created_at="2024-01-15T10:30:00Z",
            updated_at="2024-01-16T14:20:00Z",
        )
        return mock

    def test_export_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting a resource."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.txt"

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file)
                ])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                assert "exported successfully" in result.stdout.lower()
                assert output_file.exists()

    def test_export_json_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting with JSON format."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.json"

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file),
                    "--format", "json"
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                import json
                data = json.loads(output_file.read_text())
                assert data["title"] == "Test Resource"

    def test_export_markdown_format(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting with markdown format."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.md"

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file),
                    "--format", "markdown"
                ])

                assert result.exit_code == 0
                assert output_file.exists()
                content = output_file.read_text()
                assert "# Test Resource" in content
                assert "Test content here" in content

    def test_export_content_only(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting content only."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.txt"

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file),
                    "--content-only"
                ])

                assert result.exit_code == 0
                content = output_file.read_text()
                assert content.strip() == "Test content here"
                assert "Type:" not in content

    def test_export_auto_filename(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting with auto-generated filename."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                import os
                old_cwd = os.getcwd()
                try:
                    os.chdir(tmpdir)
                    result = runner.invoke(app, ["resource", "export", "1"])

                    assert result.exit_code == 0
                    # Should create file based on title
                    assert Path("Test_Resource.py").exists() or Path("Test Resource.py").exists()
                finally:
                    os.chdir(old_cwd)

    def test_export_overwrite(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting with overwrite flag."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.txt"
                output_file.write_text("original content")

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file),
                    "--overwrite"
                ])

                assert result.exit_code == 0
                content = output_file.read_text()
                assert "Test content here" in content

    def test_export_file_exists_error(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test export fails when file exists without --overwrite."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.TemporaryDirectory() as tmpdir:
                output_file = Path(tmpdir) / "exported.txt"
                output_file.write_text("existing content")

                result = runner.invoke(app, [
                    "resource", "export", "1",
                    "--output", str(output_file)
                ])

                assert result.exit_code == 1
                assert "File already exists" in result.stdout

    def test_export_not_found(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test exporting non-existent resource."""
        from pharos_cli.client.exceptions import ResourceNotFoundError

        mock_resource_client.get.side_effect = ResourceNotFoundError("Resource 999 not found")

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "export", "999"])

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceBatchCommandIntegration:
    """Integration tests for batch operations."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_import_help(self, runner: CliRunner) -> None:
        """Test import command help."""
        result = runner.invoke(app, ["resource", "import", "--help"])

        assert result.exit_code == 0
        assert "--recursive" in result.stdout
        assert "--pattern" in result.stdout
        assert "--workers" in result.stdout
        assert "--dry-run" in result.stdout

    def test_export_help(self, runner: CliRunner) -> None:
        """Test export command help."""
        result = runner.invoke(app, ["resource", "export", "--help"])

        assert result.exit_code == 0
        assert "--output" in result.stdout
        assert "--format" in result.stdout
        assert "--content-only" in result.stdout
        assert "--overwrite" in result.stdout