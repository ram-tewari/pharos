"""Integration tests for resource commands."""

import pytest
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from io import StringIO

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app
from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import Resource, PaginatedResponse


class TestResourceAddCommand:
    """Test cases for 'pharos resource add' command."""

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

    def test_add_file(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a resource from a file."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            # Use a predictable filename for title testing
            with tempfile.TemporaryDirectory() as tmpdir:
                temp_file = Path(tmpdir) / "hello_world.py"
                temp_file.write_text("def hello():\n    print('Hello, World!')")

                result = runner.invoke(app, ["resource", "add", str(temp_file)])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                assert "Resource created successfully" in result.stdout
                assert "ID: 1" in result.stdout
                assert "Test Resource" in result.stdout

                mock_resource_client.create.assert_called_once()
                call_kwargs = mock_resource_client.create.call_args[1]
                assert call_kwargs["title"] == "Hello World"
                assert "def hello" in call_kwargs["content"]
                assert call_kwargs["resource_type"] == "code"
                assert call_kwargs["language"] == "python"

    def test_add_file_with_type(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a file with explicit type."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
                f.write("This is a document")
                temp_file = Path(f.name)

            try:
                result = runner.invoke(app, ["resource", "add", str(temp_file), "--type", "documentation"])

                assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
                mock_resource_client.create.assert_called_once()
                call_kwargs = mock_resource_client.create.call_args[1]
                assert call_kwargs["resource_type"] == "documentation"
            finally:
                temp_file.unlink()

    def test_add_url(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a resource from URL."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "add",
                "--url", "https://example.com/paper.pdf",
                "--title", "My Paper",
                "--type", "paper"
            ])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Resource created successfully" in result.stdout

            mock_resource_client.create.assert_called_once()
            call_kwargs = mock_resource_client.create.call_args[1]
            assert call_kwargs["title"] == "My Paper"
            assert call_kwargs["url"] == "https://example.com/paper.pdf"
            assert call_kwargs["resource_type"] == "paper"

    def test_add_stdin(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a resource from stdin."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "add",
                "--stdin",
                "--title", "Stdin Resource"
            ], input="Content from stdin\nLine 2\nLine 3")

            assert result.exit_code == 0
            assert "Resource created successfully" in result.stdout

            mock_resource_client.create.assert_called_once()
            call_kwargs = mock_resource_client.create.call_args[1]
            assert call_kwargs["title"] == "Stdin Resource"
            assert "Content from stdin" in call_kwargs["content"]

    def test_add_content(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a resource with inline content."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "add",
                "--title", "Inline Content",
                "--content", "This is inline content"
            ])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"

            mock_resource_client.create.assert_called_once()
            call_kwargs = mock_resource_client.create.call_args[1]
            assert call_kwargs["title"] == "Inline Content"
            assert call_kwargs["content"] == "This is inline content"

    def test_add_multiple_sources_error(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test that specifying multiple sources raises an error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("File content")
            temp_file = Path(f.name)

        try:
            result = runner.invoke(app, [
                "resource", "add",
                str(temp_file),
                "--url", "https://example.com"
            ])

            assert result.exit_code == 1
            assert "Cannot specify multiple input sources" in result.stdout
        finally:
            temp_file.unlink()

    def test_add_file_not_found(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding a non-existent file."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "add", "/nonexistent/file.txt"])

            assert result.exit_code == 1
            assert "File not found" in result.stdout or "not found" in result.stdout.lower()

    def test_add_invalid_url(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test adding with invalid URL."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "add",
                "--url", "not-a-valid-url"
            ])

            assert result.exit_code == 1
            assert "Invalid URL" in result.stdout or "Invalid" in result.stdout


class TestResourceListCommand:
    """Test cases for 'pharos resource list' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.list.return_value = PaginatedResponse(
            items=[
                {"id": 1, "title": "Resource 1", "resource_type": "code", "quality_score": 0.85},
                {"id": 2, "title": "Resource 2", "resource_type": "paper", "quality_score": 0.72},
            ],
            total=2,
            page=1,
            per_page=25,
            has_more=False,
        )
        return mock

    def test_list_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing resources without filters."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "list"])

            assert result.exit_code == 0
            assert "Resource 1" in result.stdout or "Resource 2" in result.stdout

            mock_resource_client.list.assert_called_once()
            call_kwargs = mock_resource_client.list.call_args[1]
            assert call_kwargs["skip"] == 0
            assert call_kwargs["limit"] == 25

    def test_list_with_filters(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing resources with filters."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "list",
                "--type", "code",
                "--language", "python",
                "--min-quality", "0.8"
            ])

            assert result.exit_code == 0

            mock_resource_client.list.assert_called_once()
            call_kwargs = mock_resource_client.list.call_args[1]
            assert call_kwargs["resource_type"] == "code"
            assert call_kwargs["language"] == "python"
            assert call_kwargs["min_quality"] == 0.8

    def test_list_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing resources with JSON output."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "list", "--format", "json"])

            assert result.exit_code == 0
            # JSON output should be valid JSON
            import json
            data = json.loads(result.stdout)
            assert "items" in data
            assert "total" in data

    def test_list_quiet_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing resources with quiet output (IDs only)."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "list", "--format", "quiet"])

            assert result.exit_code == 0
            # Should just have IDs
            assert "1" in result.stdout
            assert "2" in result.stdout

    def test_list_empty(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing when no resources found."""
        mock_resource_client.list.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=25,
            has_more=False,
        )

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "list"])

            assert result.exit_code == 0
            assert "No resources found" in result.stdout

    def test_list_with_tags(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test listing resources with tag filter."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "list", "--tags", "important,python"])

            assert result.exit_code == 0

            mock_resource_client.list.assert_called_once()
            call_kwargs = mock_resource_client.list.call_args[1]
            assert call_kwargs["tags"] == ["important", "python"]


class TestResourceGetCommand:
    """Test cases for 'pharos resource get' command."""

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

    def test_get_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting a resource by ID."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "get", "1"])

            assert result.exit_code == 0
            assert "Test Resource" in result.stdout
            assert "code" in result.stdout
            assert "python" in result.stdout

            mock_resource_client.get.assert_called_once_with(resource_id=1)

    def test_get_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting a resource with JSON output."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "get", "1", "--format", "json"])

            assert result.exit_code == 0
            import json
            data = json.loads(result.stdout)
            assert data["title"] == "Test Resource"

    def test_get_with_content(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting a resource with content shown."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "get", "1", "--content"])

            assert result.exit_code == 0
            assert "Test content here" in result.stdout

    def test_get_not_found(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting a non-existent resource."""
        from pharos_cli.client.exceptions import ResourceNotFoundError

        mock_resource_client.get.side_effect = ResourceNotFoundError("Resource 999 not found")

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "get", "999"])

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceUpdateCommand:
    """Test cases for 'pharos resource update' command."""

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
        )
        return mock

    def test_update_title(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test updating resource title."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "update", "1", "--title", "New Title"])

            assert result.exit_code == 0
            assert "updated successfully" in result.stdout.lower()

            mock_resource_client.update.assert_called_once()
            call_kwargs = mock_resource_client.update.call_args[1]
            assert call_kwargs["title"] == "New Title"

    def test_update_multiple_fields(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test updating multiple fields."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, [
                "resource", "update", "1",
                "--title", "New Title",
                "--type", "paper",
                "--language", "english"
            ])

            assert result.exit_code == 0

            mock_resource_client.update.assert_called_once()
            call_kwargs = mock_resource_client.update.call_args[1]
            assert call_kwargs["title"] == "New Title"
            assert call_kwargs["resource_type"] == "paper"
            assert call_kwargs["language"] == "english"

    def test_update_no_fields_error(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test that updating without fields raises an error."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "update", "1"])

            assert result.exit_code == 1
            assert "Must specify at least one field" in result.stdout

    def test_update_not_found(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test updating a non-existent resource."""
        from pharos_cli.client.exceptions import ResourceNotFoundError

        mock_resource_client.update.side_effect = ResourceNotFoundError("Resource 999 not found")

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "update", "999", "--title", "New Title"])

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceDeleteCommand:
    """Test cases for 'pharos resource delete' command."""

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
            title="Resource to Delete",
            resource_type="code",
        )
        mock.delete.return_value = {"success": True, "message": "Resource deleted"}
        return mock

    def test_delete_with_confirmation(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test deleting a resource with confirmation."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "delete", "1"], input="y\n")

            assert result.exit_code == 0
            assert "deleted successfully" in result.stdout

            mock_resource_client.delete.assert_called_once_with(resource_id=1)

    def test_delete_cancelled(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test that deletion is cancelled when user says no."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "delete", "1"], input="n\n")

            assert result.exit_code == 0
            assert "cancelled" in result.stdout
            mock_resource_client.delete.assert_not_called()

    def test_delete_force(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test deleting a resource with --force flag."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "delete", "1", "--force"])

            assert result.exit_code == 0
            assert "deleted successfully" in result.stdout
            mock_resource_client.delete.assert_called_once()

    def test_delete_not_found(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test deleting a non-existent resource."""
        from pharos_cli.client.exceptions import ResourceNotFoundError

        mock_resource_client.get.side_effect = ResourceNotFoundError("Resource 999 not found")

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "delete", "999"])

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceQualityCommand:
    """Test cases for 'pharos resource quality' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.get_quality_score.return_value = {
            "resource_id": 1,
            "overall_score": 0.85,
            "clarity": 0.9,
            "completeness": 0.8,
            "correctness": 0.9,
            "originality": 0.75,
            "computed_at": "2024-01-15T10:30:00Z",
        }
        return mock

    def test_quality_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting quality score."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "quality", "1"])

            assert result.exit_code == 0
            assert "Quality Score" in result.stdout or "0.85" in result.stdout

            mock_resource_client.get_quality_score.assert_called_once_with(resource_id=1)

    def test_quality_json_output(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting quality score with JSON output."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "quality", "1", "--format", "json"])

            assert result.exit_code == 0
            import json
            data = json.loads(result.stdout)
            assert "overall_score" in data


class TestResourceAnnotationsCommand:
    """Test cases for 'pharos resource annotations' command."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_resource_client(self):
        """Create a mock resource client."""
        mock = MagicMock(spec=ResourceClient)
        mock.get_annotations.return_value = [
            {"id": 1, "text": "First annotation", "annotation_type": "highlight"},
            {"id": 2, "text": "Second annotation", "annotation_type": "note"},
        ]
        return mock

    def test_annotations_basic(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting annotations."""
        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "annotations", "1"])

            assert result.exit_code == 0
            assert "First annotation" in result.stdout or "Second annotation" in result.stdout

            mock_resource_client.get_annotations.assert_called_once_with(resource_id=1)

    def test_annotations_empty(
        self,
        runner: CliRunner,
        mock_resource_client: MagicMock,
    ) -> None:
        """Test getting annotations when none exist."""
        mock_resource_client.get_annotations.return_value = []

        with patch("pharos_cli.commands.resource.get_resource_client", return_value=mock_resource_client):
            result = runner.invoke(app, ["resource", "annotations", "1"])

            assert result.exit_code == 0
            assert "No annotations found" in result.stdout


class TestResourceCommandIntegration:
    """Integration tests for resource commands."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner."""
        return CliRunner()

    def test_resource_help(self, runner: CliRunner) -> None:
        """Test resource command help."""
        result = runner.invoke(app, ["resource", "--help"])

        assert result.exit_code == 0
        assert "add" in result.stdout
        assert "list" in result.stdout
        assert "get" in result.stdout
        assert "update" in result.stdout
        assert "delete" in result.stdout

    def test_resource_add_help(self, runner: CliRunner) -> None:
        """Test resource add command help."""
        result = runner.invoke(app, ["resource", "add", "--help"])

        assert result.exit_code == 0
        assert "--url" in result.stdout
        assert "--title" in result.stdout
        assert "--type" in result.stdout
        assert "--stdin" in result.stdout

    def test_resource_list_help(self, runner: CliRunner) -> None:
        """Test resource list command help."""
        result = runner.invoke(app, ["resource", "list", "--help"])

        assert result.exit_code == 0
        assert "--type" in result.stdout
        assert "--language" in result.stdout
        assert "--format" in result.stdout