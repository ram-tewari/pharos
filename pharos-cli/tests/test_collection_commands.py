"""Integration tests for collection commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the collection module to ensure it's loaded
from pharos_cli.commands import collection as collection_module


@pytest.fixture
def runner() -> Generator[CliRunner, None, None]:
    """Create a CLI runner for testing commands."""
    yield CliRunner()


class TestCollectionCreateCommand:
    """Test cases for collection create command."""

    def test_create_collection_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating a collection with basic fields."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 1,
                "name": "Test Collection",
                "description": "A test collection",
                "is_public": False,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["create", "Test Collection", "--description", "A test collection"],
            )

            assert result.exit_code == 0
            assert "Collection created successfully" in result.stdout
            assert "ID: 1" in result.stdout
            assert "Test Collection" in result.stdout

    def test_create_collection_public(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating a public collection."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 2,
                "name": "Public Collection",
                "is_public": True,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["create", "Public Collection", "--public"],
            )

            assert result.exit_code == 0
            assert "Public: True" in result.stdout

    def test_create_collection_api_error(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating a collection when API returns an error."""
        from pharos_cli.client.exceptions import APIError

        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.side_effect = APIError(
                status_code=400,
                message="Validation error",
            )
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["create", "Test Collection"],
            )

            assert result.exit_code == 1
            assert "API Error" in result.stdout


class TestCollectionListCommand:
    """Test cases for collection list command."""

    def test_list_collections_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing collections."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list.return_value = MagicMock(
                items=[
                    {"id": 1, "name": "Collection 1", "resource_count": 5, "is_public": False},
                    {"id": 2, "name": "Collection 2", "resource_count": 10, "is_public": True},
                ],
                total=2,
                page=1,
                per_page=25,
                has_more=False,
            )
            mock_get_client.return_value = mock_client

            result = runner.invoke(collection_module.collection_app, ["list"])

            assert result.exit_code == 0
            assert "Collection 1" in result.stdout
            assert "Collection 2" in result.stdout

    def test_list_collections_with_query(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing collections with search query."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list.return_value = MagicMock(
                items=[{"id": 1, "name": "ML Papers", "resource_count": 15, "is_public": True}],
                total=1,
                page=1,
                per_page=25,
                has_more=False,
            )
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["list", "--query", "machine learning"],
            )

            assert result.exit_code == 0
            assert "ML Papers" in result.stdout

    def test_list_collections_empty(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing collections when none exist."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list.return_value = MagicMock(
                items=[],
                total=0,
                page=1,
                per_page=25,
                has_more=False,
            )
            mock_get_client.return_value = mock_client

            result = runner.invoke(collection_module.collection_app, ["list"])

            assert result.exit_code == 0
            assert "No collections found" in result.stdout

    def test_list_collections_json_output(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing collections with JSON output."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list.return_value = MagicMock(
                items=[{"id": 1, "name": "Test"}],
                total=1,
                page=1,
                per_page=25,
                has_more=False,
            )
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["list", "--format", "json"],
            )

            assert result.exit_code == 0
            assert '"items"' in result.stdout


class TestCollectionShowCommand:
    """Test cases for collection show command."""

    def test_show_collection_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test showing collection details."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_collection.id = 1
            mock_collection.name = "Test Collection"
            mock_collection.description = "A test collection"
            mock_collection.is_public = False
            mock_collection.resource_count = 5
            mock_collection.created_at = "2024-01-15T10:30:00Z"
            mock_collection.updated_at = "2024-01-16T14:20:00Z"
            mock_client.get.return_value = mock_collection
            mock_get_client.return_value = mock_client

            result = runner.invoke(collection_module.collection_app, ["show", "1"])

            assert result.exit_code == 0
            assert "Test Collection" in result.stdout
            assert "1" in result.stdout  # ID is in the output
            assert "5" in result.stdout  # Resource count is in the output

    def test_show_collection_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test showing a collection that doesn't exist."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            from pharos_cli.client.exceptions import CollectionNotFoundError

            mock_client = MagicMock()
            mock_client.get.side_effect = CollectionNotFoundError("Collection 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(collection_module.collection_app, ["show", "999"])

            assert result.exit_code == 1
            assert "not found" in result.stdout

    def test_show_collection_with_contents(
        self,
        runner: CliRunner,
    ) -> None:
        """Test showing collection with resources."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock collection
            mock_collection = MagicMock()
            mock_collection.id = 1
            mock_collection.name = "Test Collection"
            mock_collection.description = None
            mock_collection.is_public = False
            mock_collection.resource_count = 2
            mock_collection.created_at = None
            mock_collection.updated_at = None
            mock_client.get.return_value = mock_collection

            # Mock contents
            mock_contents = MagicMock()
            mock_contents.items = [
                {"id": 1, "title": "Resource 1", "resource_type": "code", "quality_score": 0.85},
                {"id": 2, "title": "Resource 2", "resource_type": "paper", "quality_score": 0.92},
            ]
            mock_contents.total = 2
            mock_contents.has_more = False
            mock_client.get_contents.return_value = mock_contents

            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["show", "1", "--contents"],
            )

            assert result.exit_code == 0
            assert "Resource 1" in result.stdout
            assert "Resource 2" in result.stdout


class TestCollectionAddCommand:
    """Test cases for collection add command."""

    def test_add_resource_to_collection(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource to a collection."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.add_resource.return_value = {
                "resource_id": 5,
                "collection_id": 1,
                "success": True,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["add", "1", "5"],
            )

            assert result.exit_code == 0
            assert "added to collection 1 successfully" in result.stdout

    def test_add_resource_collection_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test adding a resource to a non-existent collection."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            from pharos_cli.client.exceptions import CollectionNotFoundError

            mock_client = MagicMock()
            mock_client.add_resource.side_effect = CollectionNotFoundError("Collection 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["add", "999", "5"],
            )

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestCollectionRemoveCommand:
    """Test cases for collection remove command."""

    def test_remove_resource_from_collection(
        self,
        runner: CliRunner,
    ) -> None:
        """Test removing a resource from a collection."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.remove_resource.return_value = {"success": True}
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["remove", "1", "5"],
            )

            assert result.exit_code == 0
            assert "removed from collection 1 successfully" in result.stdout


class TestCollectionDeleteCommand:
    """Test cases for collection delete command."""

    def test_delete_collection_with_confirmation(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a collection with confirmation."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()

            # Mock collection for confirmation
            mock_collection = MagicMock()
            mock_collection.name = "Test Collection"
            mock_collection.resource_count = 0
            mock_client.get.return_value = mock_collection
            mock_client.delete.return_value = {"success": True}

            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["delete", "1"],
                input="y\n",
            )

            assert result.exit_code == 0
            assert "deleted successfully" in result.stdout

    def test_delete_collection_force(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a collection with --force flag."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get.return_value = MagicMock(name="Test", resource_count=0)
            mock_client.delete.return_value = {"success": True}
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["delete", "1", "--force"],
            )

            assert result.exit_code == 0
            # Should not prompt for confirmation
            assert "Confirm Deletion" not in result.stdout

    def test_delete_collection_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting a collection that doesn't exist."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            from pharos_cli.client.exceptions import CollectionNotFoundError

            mock_client = MagicMock()
            mock_client.get.side_effect = CollectionNotFoundError("Collection 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["delete", "999"],
            )

            assert result.exit_code == 1
            assert "not found" in result.stdout


class TestCollectionUpdateCommand:
    """Test cases for collection update command."""

    def test_update_collection_name(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating collection name."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_collection = MagicMock()
            mock_collection.id = 1
            mock_collection.name = "New Name"
            mock_collection.description = "Description"
            mock_collection.is_public = False
            mock_client.update.return_value = mock_collection
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["update", "1", "--name", "New Name"],
            )

            assert result.exit_code == 0
            assert "updated successfully" in result.stdout

    def test_update_collection_no_fields(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating collection with no fields."""
        result = runner.invoke(
            collection_module.collection_app,
            ["update", "1"],
        )

        assert result.exit_code == 1
        assert "Must specify at least one field" in result.stdout


class TestCollectionExportCommand:
    """Test cases for collection export command."""

    def test_export_collection_json(
        self,
        runner: CliRunner,
    ) -> None:
        """Test exporting a collection as JSON."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.export.return_value = {
                "id": 1,
                "name": "Test Collection",
                "resources": [],
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["export", "1"],
            )

            assert result.exit_code == 0
            assert "Test Collection" in result.stdout


class TestCollectionStatsCommand:
    """Test cases for collection stats command."""

    def test_collection_stats(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting collection statistics."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get_stats.return_value = {
                "resource_count": 10,
                "quality_avg": 0.85,
                "type_distribution": {"code": 5, "paper": 5},
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["stats", "1"],
            )

            assert result.exit_code == 0
            assert "Resource Count" in result.stdout
            assert "10" in result.stdout

    def test_collection_stats_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting stats for a non-existent collection."""
        with patch.object(collection_module, "get_collection_client") as mock_get_client:
            from pharos_cli.client.exceptions import CollectionNotFoundError

            mock_client = MagicMock()
            mock_client.get_stats.side_effect = CollectionNotFoundError("Collection 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                collection_module.collection_app,
                ["stats", "999"],
            )

            assert result.exit_code == 1
            assert "not found" in result.stdout