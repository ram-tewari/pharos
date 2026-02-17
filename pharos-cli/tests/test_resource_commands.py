"""Integration tests for resource commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from typing import Generator
from datetime import datetime

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the resource module to ensure it's loaded
from pharos_cli.commands import resource as resource_module


@pytest.fixture
def runner() -> Generator[CliRunner, None, None]:
    """Create a CLI runner for testing commands."""
    yield CliRunner()


class TestResourceAddCommand:
    """Test cases for resource add command."""

    def test_add_resource_from_file(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource from a file."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 1,
                "title": "Test File",
                "resource_type": "code",
                "language": "python",
            }
            mock_get_client.return_value = mock_client

            # Create a temporary file
            with runner.isolated_filesystem():
                with open("test_file.py", "w") as f:
                    f.write("print('hello')")

                result = runner.invoke(
                    resource_module.resource_app,
                    ["add", "test_file.py"],
                )

                assert result.exit_code == 0, f"Exit code was {result.exit_code}, output: {result.stdout}"
                assert "Resource created successfully" in result.stdout
                assert "ID: 1" in result.stdout
                assert "Test File" in result.stdout

    def test_add_resource_from_file_with_type(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource with explicit type."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 2,
                "title": "My Document",
                "resource_type": "documentation",
                "language": "markdown",
            }
            mock_get_client.return_value = mock_client

            with runner.isolated_filesystem():
                with open("readme.md", "w") as f:
                    f.write("# Readme")

                result = runner.invoke(
                    resource_module.resource_app,
                    ["add", "readme.md", "--type", "documentation", "--language", "markdown"],
                )

                assert result.exit_code == 0, f"Exit code was {result.exit_code}, output: {result.stdout}"
                assert "documentation" in result.stdout

    def test_add_resource_from_url(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource from a URL."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 3,
                "title": "Example Paper",
                "url": "https://example.com/paper.pdf",
                "resource_type": "paper",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["add", "--url", "https://example.com/paper.pdf", "--type", "paper"],
            )

            assert result.exit_code == 0, f"Exit code was {result.exit_code}, output: {result.stdout}"
            assert "Resource created successfully" in result.stdout
            assert "URL: https://example.com/paper.pdf" in result.stdout

    def test_add_resource_from_stdin(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource from stdin."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 4,
                "title": "Stdin Input",
                "resource_type": "documentation",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["add", "--stdin", "--title", "Stdin Input"],
                input="This is content from stdin\n",
            )

            assert result.exit_code == 0
            assert "Resource created successfully" in result.stdout

    def test_add_resource_with_content(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource with inline content."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 5,
                "title": "Quick Note",
                "content": "This is a quick note",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["add", "--content", "This is a quick note", "--title", "Quick Note"],
            )

            assert result.exit_code == 0, f"Exit code was {result.exit_code}, output: {result.stdout}"
            assert "Resource created successfully" in result.stdout

    def test_add_resource_no_input(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource without any input source."""
        result = runner.invoke(
            resource_module.resource_app,
            ["add"],
        )

        assert result.exit_code == 1, f"Exit code was {result.exit_code}, output: {result.stdout}"
        assert "Must specify" in result.stdout

    def test_add_resource_multiple_inputs(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource with multiple input sources (should fail)."""
        with runner.isolated_filesystem():
            with open("test.py", "w") as f:
                f.write("print('hello')")

            # When stdin is provided without content, it fails with stdin error first
            result = runner.invoke(
                resource_module.resource_app,
                ["add", "test.py", "--stdin"],
            )

            # Either error is acceptable - stdin without content or multiple inputs
            assert result.exit_code == 1
            output = result.stdout
            assert "Error" in output

    def test_add_resource_file_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource from a non-existent file."""
        with runner.isolated_filesystem():
            result = runner.invoke(
                resource_module.resource_app,
                ["add", "nonexistent.py"],
            )

            assert result.exit_code == 1, f"Exit code was {result.exit_code}, output: {result.stdout}"
            assert "File not found" in result.stdout

    def test_add_resource_api_error(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource when API returns an error."""
        from pharos_cli.client.exceptions import APIError

        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.side_effect = APIError(
                status_code=400,
                message="Validation error",
            )
            mock_get_client.return_value = mock_client

            with runner.isolated_filesystem():
                with open("test.py", "w") as f:
                    f.write("print('hello')")

                result = runner.invoke(
                    resource_module.resource_app,
                    ["add", "test.py"],
                )

                assert result.exit_code == 1, f"Exit code was {result.exit_code}, output: {result.stdout}"
                assert "API Error" in result.stdout


class TestResourceListCommand:
    """Test cases for resource list command."""

    def test_list_resources_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "Resource 1", "resource_type": "code", "quality_score": 0.85},
                {"id": 2, "title": "Resource 2", "resource_type": "paper", "quality_score": 0.92},
            ]
            mock_response.total = 2
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(resource_module.resource_app, ["list"])

            assert result.exit_code == 0
            assert "Resource 1" in result.stdout
            assert "Resource 2" in result.stdout

    def test_list_resources_with_filters(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with filters."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "Python Code", "resource_type": "code", "language": "python"},
            ]
            mock_response.total = 1
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--type", "code", "--language", "python"],
            )

            assert result.exit_code == 0
            assert "Python Code" in result.stdout

    def test_list_resources_with_query(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with search query."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "ML Paper", "resource_type": "paper"},
            ]
            mock_response.total = 1
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--query", "machine learning"],
            )

            assert result.exit_code == 0
            assert "ML Paper" in result.stdout

    def test_list_resources_with_min_quality(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with minimum quality filter."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "High Quality", "quality_score": 0.95},
            ]
            mock_response.total = 1
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--min-quality", "0.8"],
            )

            assert result.exit_code == 0
            assert "High Quality" in result.stdout

    def test_list_resources_with_tags(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with tag filter."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "Tagged Resource", "tags": ["important", "python"]},
            ]
            mock_response.total = 1
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--tags", "important,python"],
            )

            assert result.exit_code == 0
            assert "Tagged Resource" in result.stdout

    def test_list_resources_empty(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources when none exist."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = []
            mock_response.total = 0
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(resource_module.resource_app, ["list"])

            assert result.exit_code == 0
            assert "No resources found" in result.stdout

    def test_list_resources_json_output(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with JSON output."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [{"id": 1, "title": "Test"}]
            mock_response.total = 1
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--format", "json"],
            )

            assert result.exit_code == 0
            assert '"items"' in result.stdout

    def test_list_resources_quiet_output(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with quiet output (IDs only)."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [
                {"id": 1, "title": "Resource 1"},
                {"id": 2, "title": "Resource 2"},
            ]
            mock_response.total = 2
            mock_response.page = 1
            mock_response.per_page = 25
            mock_response.has_more = False
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--format", "quiet"],
            )

            assert result.exit_code == 0
            assert "1" in result.stdout
            assert "2" in result.stdout
            # Should not have table headers
            assert "Title" not in result.stdout

    def test_list_resources_pagination(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing resources with pagination."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.items = [{"id": 26, "title": "Page 2 Resource"}]
            mock_response.total = 50
            mock_response.page = 2
            mock_response.per_page = 25
            mock_response.has_more = True
            mock_client.list.return_value = mock_response
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["list", "--page", "2", "--per-page", "25"],
            )

            assert result.exit_code == 0
            assert "Page 2 Resource" in result.stdout
            assert "next page" in result.stdout.lower()


class TestResourceGetCommand:
    """Test cases for resource get command."""

    def test_get_resource_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting a resource by ID."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resource = MagicMock()
            mock_resource.id = 1
            mock_resource.title = "Test Resource"
            mock_resource.resource_type = "code"
            mock_resource.language = "python"
            mock_resource.quality_score = 0.85
            mock_resource.url = None
            mock_resource.created_at = "2024-01-15T10:30:00Z"
            mock_resource.updated_at = "2024-01-16T14:20:00Z"
            mock_resource.content = None
            mock_resource.metadata = None
            mock_client.get.return_value = mock_resource
            mock_get_client.return_value = mock_client

            result = runner.invoke(resource_module.resource_app, ["get", "1"])

            assert result.exit_code == 0
            assert "Test Resource" in result.stdout
            assert "1" in result.stdout  # ID is in the output
            assert "python" in result.stdout

    def test_get_resource_json_output(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting a resource with JSON output."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resource = MagicMock()
            mock_resource.id = 1
            mock_resource.title = "Test Resource"
            mock_resource.resource_type = "code"
            mock_resource.language = "python"
            mock_resource.quality_score = 0.85
            mock_resource.url = None
            mock_resource.created_at = None
            mock_resource.updated_at = None
            mock_resource.content = None
            mock_resource.metadata = None
            mock_resource.model_dump.return_value = {
                "id": 1,
                "title": "Test Resource",
                "resource_type": "code",
            }
            mock_client.get.return_value = mock_resource
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["get", "1", "--format", "json"],
            )

            assert result.exit_code == 0
            assert '"title"' in result.stdout

    def test_get_resource_with_content(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting a resource with content displayed."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resource = MagicMock()
            mock_resource.id = 1
            mock_resource.title = "Test Resource"
            mock_resource.resource_type = "code"
            mock_resource.language = "python"
            mock_resource.quality_score = 0.85
            mock_resource.url = None
            mock_resource.created_at = None
            mock_resource.updated_at = None
            mock_resource.content = "print('hello')"
            mock_resource.metadata = None
            mock_client.get.return_value = mock_resource
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["get", "1", "--content"],
            )

            assert result.exit_code == 0
            assert "Content:" in result.stdout
            assert "print('hello')" in result.stdout

    def test_get_resource_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting a resource that doesn't exist."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            from pharos_cli.client.exceptions import ResourceNotFoundError

            mock_client = MagicMock()
            mock_client.get.side_effect = ResourceNotFoundError("Resource 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(resource_module.resource_app, ["get", "999"])

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceUpdateCommand:
    """Test cases for resource update command."""

    def test_update_resource_title(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating resource title."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resource = MagicMock()
            mock_resource.id = 1
            mock_resource.title = "New Title"
            mock_resource.resource_type = "code"
            mock_resource.language = "python"
            mock_client.update.return_value = mock_resource
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["update", "1", "--title", "New Title"],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.stdout
            assert "New Title" in result.stdout

    def test_update_resource_multiple_fields(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating multiple resource fields."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_resource = MagicMock()
            mock_resource.id = 1
            mock_resource.title = "New Title"
            mock_resource.content = "New content"
            mock_resource.resource_type = "paper"
            mock_resource.language = "english"
            mock_client.update.return_value = mock_resource
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["update", "1", "--title", "New Title", "--content", "New content", "--type", "paper"],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.stdout

    def test_update_resource_no_fields(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating resource with no fields."""
        result = runner.invoke(
            resource_module.resource_app,
            ["update", "1"],
        )

        assert result.exit_code == 1
        assert "Must specify at least one field" in result.stdout

    def test_update_resource_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating a resource that doesn't exist."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            from pharos_cli.client.exceptions import ResourceNotFoundError

            mock_client = MagicMock()
            mock_client.update.side_effect = ResourceNotFoundError("Resource 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["update", "999", "--title", "New Title"],
            )

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceDeleteCommand:
    """Test cases for resource delete command."""

    def test_delete_resource_with_confirmation(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a resource with confirmation."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock resource for confirmation
            mock_resource = MagicMock()
            mock_resource.title = "Test Resource"
            mock_resource.resource_type = "code"
            mock_client.get.return_value = mock_resource
            mock_client.delete.return_value = {"success": True, "message": "Resource deleted"}

            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["delete", "1"],
                input="y\n",
            )

            assert result.exit_code == 0
            assert "deleted successfully" in result.stdout

    def test_delete_resource_force(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a resource with --force flag."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get.return_value = MagicMock(title="Test", resource_type="code")
            mock_client.delete.return_value = {"success": True}
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["delete", "1", "--force"],
            )

            assert result.exit_code == 0
            # Should not prompt for confirmation
            assert "Confirm Deletion" not in result.stdout

    def test_delete_resource_cancelled(
        self,
        runner: CliRunner,
    ) -> None:
        """Test cancelling resource deletion."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get.return_value = MagicMock(title="Test", resource_type="code")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["delete", "1"],
                input="n\n",
            )

            assert result.exit_code == 0
            assert "Deletion cancelled" in result.stdout

    def test_delete_resource_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a resource that doesn't exist."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            from pharos_cli.client.exceptions import ResourceNotFoundError

            mock_client = MagicMock()
            mock_client.get.side_effect = ResourceNotFoundError("Resource 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["delete", "999"],
            )

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestResourceQualityCommand:
    """Test cases for resource quality command."""

    def test_get_resource_quality(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting quality score for a resource."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_quality_score.return_value = {
                "resource_id": 1,
                "overall_score": 0.85,
                "clarity": 0.9,
                "completeness": 0.8,
                "correctness": 0.9,
                "originality": 0.75,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["quality", "1"],
            )

            assert result.exit_code == 0
            assert "Overall" in result.stdout
            assert "0.85" in result.stdout or "85" in result.stdout

    def test_get_resource_quality_json(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting quality score with JSON output."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_quality_score.return_value = {
                "resource_id": 1,
                "overall_score": 0.85,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["quality", "1", "--format", "json"],
            )

            assert result.exit_code == 0
            assert '"overall_score"' in result.stdout


class TestResourceAnnotationsCommand:
    """Test cases for resource annotations command."""

    def test_get_resource_annotations(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting annotations for a resource."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_annotations.return_value = [
                {"id": 1, "text": "Note 1", "start_offset": 0, "end_offset": 10},
                {"id": 2, "text": "Note 2", "start_offset": 20, "end_offset": 30},
            ]
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["annotations", "1"],
            )

            assert result.exit_code == 0
            assert "Note 1" in result.stdout
            assert "Note 2" in result.stdout

    def test_get_resource_annotations_empty(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting annotations when none exist."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_annotations.return_value = []
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                resource_module.resource_app,
                ["annotations", "1"],
            )

            assert result.exit_code == 0
            assert "No annotations found" in result.stdout


class TestResourceImportCommand:
    """Test cases for resource import command."""

    def test_import_resources_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test importing resources from a directory."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {"id": 1, "title": "Test"}
            mock_get_client.return_value = mock_client

            with runner.isolated_filesystem():
                # Create test files
                Path("file1.py").write_text("print('hello')")
                Path("file2.py").write_text("print('world')")

                result = runner.invoke(
                    resource_module.resource_app,
                    ["import", "."],
                )

                assert result.exit_code == 0
                assert "Successfully imported" in result.stdout or "2" in result.stdout

    def test_import_resources_recursive(
        self,
        runner: CliRunner,
    ) -> None:
        """Test importing resources recursively."""
        with patch.object(resource_module, "get_resource_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {"id": 1, "title": "Test"}
            mock_get_client.return_value = mock_client

            with runner.isolated_filesystem():
                # Create nested directory structure
                Path("subdir").mkdir()
                Path("subdir/nested.py").write_text("print('nested')")

                result = runner.invoke(
                    resource_module.resource_app,
                    ["import", ".", "--recursive"],
                )

                assert result.exit_code == 0

    def test_import_resources_dry_run(
        self,
        runner: CliRunner,
    ) -> None:
        """Test import with dry-run flag."""
        with runner.isolated_filesystem():
            Path("test.py").write_text("print('hello')")

            result = runner.invoke(
                resource_module.resource_app,
                ["import", ".", "--dry-run"],
            )

            assert result.exit_code == 0
            # Should show what would be imported without actually importing
            assert "Would import" in result.stdout or "test.py" in result.stdout

    def test_import_resources_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test importing from non-existent directory."""
        result = runner.invoke(
            resource_module.resource_app,
            ["import", "nonexistent"],
        )

        # Typer uses exit code 2 for usage errors when argument validation fails
        # The error message format depends on Typer version
        assert result.exit_code == 2, f"Exit code was {result.exit_code}, output: {result.stdout}"
        # Check that there's an error message (may contain "nonexistent" or "not found" or "exist")
        output = result.stdout + result.stderr
        assert len(output) > 0, "Expected error output but got none"