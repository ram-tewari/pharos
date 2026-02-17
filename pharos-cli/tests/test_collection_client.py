"""Unit tests for CollectionClient."""

import pytest
from unittest.mock import MagicMock
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.collection_client import CollectionClient
from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse


class TestCollectionClient:
    """Test cases for CollectionClient."""

    @pytest.fixture
    def mock_api_client(self) -> Generator[MagicMock, None, None]:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def collection_client(self, mock_api_client: MagicMock) -> CollectionClient:
        """Create a CollectionClient with mock API client."""
        return CollectionClient(mock_api_client)

    def test_create_basic(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a collection with basic fields."""
        mock_api_client.post.return_value = {
            "id": 1,
            "name": "Test Collection",
            "description": "A test collection",
            "is_public": False,
            "resource_count": 0,
        }

        result = collection_client.create(
            name="Test Collection",
            description="A test collection",
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections",
            json={
                "name": "Test Collection",
                "description": "A test collection",
            },
        )

        assert result["id"] == 1
        assert result["name"] == "Test Collection"

    def test_create_public(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a public collection."""
        mock_api_client.post.return_value = {
            "id": 2,
            "name": "Public Collection",
            "is_public": True,
        }

        result = collection_client.create(
            name="Public Collection",
            is_public=True,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections",
            json={
                "name": "Public Collection",
                "is_public": True,
            },
        )
        assert result["id"] == 2

    def test_create_minimal(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a collection with only required fields."""
        mock_api_client.post.return_value = {
            "id": 3,
            "name": "Minimal Collection",
        }

        result = collection_client.create(name="Minimal Collection")

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections",
            json={"name": "Minimal Collection"},
        )
        assert result["id"] == 3

    def test_list_basic(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing collections without filters."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "name": "Collection 1"},
                {"id": 2, "name": "Collection 2"},
            ],
            "total": 2,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = collection_client.list()

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections",
            params={"skip": 0, "limit": 100},
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2

    def test_list_with_query(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing collections with search query."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "name": "ML Papers"}],
            "total": 1,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = collection_client.list(
            skip=10,
            limit=25,
            query="machine learning",
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections",
            params={
                "skip": 10,
                "limit": 25,
                "query": "machine learning",
            },
        )
        assert len(result.items) == 1

    def test_list_pagination(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test pagination in list method."""
        mock_api_client.get.return_value = {
            "items": [{"id": 51, "name": "Page 2 Collection"}],
            "total": 100,
            "page": 2,
            "per_page": 50,
            "has_more": True,
        }

        result = collection_client.list(skip=50, limit=50)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections",
            params={"skip": 50, "limit": 50},
        )
        assert result.page == 2
        assert result.has_more is True

    def test_get(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a collection by ID."""
        mock_api_client.get.return_value = {
            "id": 1,
            "name": "Test Collection",
            "description": "A test collection",
            "is_public": False,
            "resource_count": 5,
            "created_at": "2024-01-15T10:30:00Z",
        }

        result = collection_client.get(collection_id=1)

        mock_api_client.get.assert_called_once_with("/api/v1/collections/1")
        assert result.id == 1
        assert result.name == "Test Collection"
        assert result.resource_count == 5

    def test_get_not_found(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a collection that doesn't exist raises CollectionNotFoundError."""
        from pharos_cli.client.exceptions import APIError, CollectionNotFoundError

        mock_api_client.get.side_effect = APIError(
            status_code=404,
            message="Collection not found",
            details={"detail": "Collection not found"},
        )

        with pytest.raises(CollectionNotFoundError) as exc_info:
            collection_client.get(collection_id=999)

        assert "999" in str(exc_info.value)
        mock_api_client.get.assert_called_once_with("/api/v1/collections/999")

    def test_get_contents(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting resources in a collection."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "title": "Resource 1"},
                {"id": 2, "title": "Resource 2"},
            ],
            "total": 2,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = collection_client.get_contents(collection_id=1)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections/1/resources",
            params={"skip": 0, "limit": 100},
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2

    def test_update_name(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating collection name."""
        mock_api_client.put.return_value = {
            "id": 1,
            "name": "Updated Name",
            "description": "Original description",
        }

        result = collection_client.update(collection_id=1, name="Updated Name")

        mock_api_client.put.assert_called_once_with(
            "/api/v1/collections/1",
            json={"name": "Updated Name"},
        )
        assert result.name == "Updated Name"

    def test_update_multiple_fields(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating multiple fields."""
        mock_api_client.put.return_value = {
            "id": 1,
            "name": "New Name",
            "description": "New description",
            "is_public": True,
        }

        result = collection_client.update(
            collection_id=1,
            name="New Name",
            description="New description",
            is_public=True,
        )

        mock_api_client.put.assert_called_once_with(
            "/api/v1/collections/1",
            json={
                "name": "New Name",
                "description": "New description",
                "is_public": True,
            },
        )
        assert result.name == "New Name"

    def test_update_not_found(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating a collection that doesn't exist raises CollectionNotFoundError."""
        from pharos_cli.client.exceptions import APIError, CollectionNotFoundError

        mock_api_client.put.side_effect = APIError(
            status_code=404,
            message="Collection not found",
            details={"detail": "Collection not found"},
        )

        with pytest.raises(CollectionNotFoundError) as exc_info:
            collection_client.update(collection_id=999, name="New Name")

        assert "999" in str(exc_info.value)

    def test_delete(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting a collection."""
        mock_api_client.delete.return_value = {"success": True, "message": "Collection deleted"}

        result = collection_client.delete(collection_id=1)

        mock_api_client.delete.assert_called_once_with("/api/v1/collections/1")
        assert result["success"] is True

    def test_delete_not_found(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting a collection that doesn't exist raises CollectionNotFoundError."""
        from pharos_cli.client.exceptions import APIError, CollectionNotFoundError

        mock_api_client.delete.side_effect = APIError(
            status_code=404,
            message="Collection not found",
            details={"detail": "Collection not found"},
        )

        with pytest.raises(CollectionNotFoundError) as exc_info:
            collection_client.delete(collection_id=999)

        assert "999" in str(exc_info.value)
        mock_api_client.delete.assert_called_once_with("/api/v1/collections/999")

    def test_add_resource(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test adding a resource to a collection."""
        mock_api_client.post.return_value = {
            "resource_id": 5,
            "collection_id": 1,
            "success": True,
        }

        result = collection_client.add_resource(
            collection_id=1,
            resource_id=5,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections/1/resources",
            json={"resource_id": 5},
        )
        assert result["success"] is True

    def test_remove_resource(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test removing a resource from a collection."""
        mock_api_client.delete.return_value = {"success": True}

        result = collection_client.remove_resource(
            collection_id=1,
            resource_id=5,
        )

        mock_api_client.delete.assert_called_once_with(
            "/api/v1/collections/1/resources/5",
        )
        assert result["success"] is True

    def test_export_json(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting a collection as JSON."""
        mock_api_client.get.return_value = {
            "id": 1,
            "name": "Test Collection",
            "resources": [
                {"id": 1, "title": "Resource 1"},
            ],
        }

        result = collection_client.export(collection_id=1, format="json")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections/1/export",
            params={"format": "json"},
        )
        assert result["id"] == 1

    def test_get_stats(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting collection statistics."""
        mock_api_client.get.return_value = {
            "resource_count": 10,
            "quality_avg": 0.85,
            "type_distribution": {"code": 5, "paper": 5},
        }

        result = collection_client.get_stats(collection_id=1)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections/1/stats",
        )
        assert result["resource_count"] == 10
        assert result["quality_avg"] == 0.85


class TestCollectionClientEdgeCases:
    """Edge case tests for CollectionClient."""

    @pytest.fixture
    def mock_api_client(self) -> Generator[MagicMock, None, None]:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def collection_client(self, mock_api_client: MagicMock) -> CollectionClient:
        """Create a CollectionClient with mock API client."""
        return CollectionClient(mock_api_client)

    def test_list_empty_results(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list when no collections match filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = collection_client.list(query="nonexistent")

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
        assert result.total == 0

    def test_list_boundary_values(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list with boundary values for pagination."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 0,
            "has_more": False,
        }

        result = collection_client.list(skip=0, limit=0)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections",
            params={"skip": 0, "limit": 0},
        )
        assert result.per_page == 0

    def test_list_large_pagination(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list with large skip value."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 1000,
            "page": 11,
            "per_page": 100,
            "has_more": False,
        }

        result = collection_client.list(skip=1000, limit=100)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/collections",
            params={"skip": 1000, "limit": 100},
        )
        assert result.page == 11

    def test_update_no_fields(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test update with no fields (should send empty dict)."""
        mock_api_client.put.return_value = {"id": 1, "name": "No Change"}

        result = collection_client.update(collection_id=1)

        mock_api_client.put.assert_called_once_with(
            "/api/v1/collections/1",
            json={},
        )
        assert result.id == 1

    def test_create_with_special_characters(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a collection with special characters in name."""
        mock_api_client.post.return_value = {
            "id": 10,
            "name": "Collection with \"quotes\" & <special> chars",
        }

        result = collection_client.create(
            name="Collection with \"quotes\" & <special> chars",
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections",
            json={"name": "Collection with \"quotes\" & <special> chars"},
        )
        assert result["id"] == 10


class TestCollectionClientErrorHandling:
    """Error handling tests for CollectionClient."""

    @pytest.fixture
    def mock_api_client(self) -> Generator[MagicMock, None, None]:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def collection_client(self, mock_api_client: MagicMock) -> CollectionClient:
        """Create a CollectionClient with mock API client."""
        return CollectionClient(mock_api_client)

    def test_get_non_404_error_re_raised(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that non-404 API errors are re-raised."""
        from pharos_cli.client.exceptions import APIError

        mock_api_client.get.side_effect = APIError(
            status_code=500,
            message="Internal Server Error",
            details={"detail": "Something went wrong"},
        )

        with pytest.raises(APIError) as exc_info:
            collection_client.get(collection_id=1)

        assert exc_info.value.status_code == 500

    def test_update_non_404_error_re_raised(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that non-404 API errors on update are re-raised."""
        from pharos_cli.client.exceptions import APIError

        mock_api_client.put.side_effect = APIError(
            status_code=400,
            message="Validation Error",
            details={"name": ["This field is required"]},
        )

        with pytest.raises(APIError) as exc_info:
            collection_client.update(collection_id=1, name="New Name")

        assert exc_info.value.status_code == 400

    def test_delete_non_404_error_re_raised(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that non-404 API errors on delete are re-raised."""
        from pharos_cli.client.exceptions import APIError

        mock_api_client.delete.side_effect = APIError(
            status_code=403,
            message="Forbidden",
            details={"detail": "Permission denied"},
        )

        with pytest.raises(APIError) as exc_info:
            collection_client.delete(collection_id=1)

        assert exc_info.value.status_code == 403

    def test_get_network_error(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.get.side_effect = NetworkError("Connection refused")

        with pytest.raises(NetworkError) as exc_info:
            collection_client.get(collection_id=1)

        assert "Connection refused" in str(exc_info.value)

    def test_list_network_error(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors on list are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.get.side_effect = NetworkError("Connection timeout")

        with pytest.raises(NetworkError):
            collection_client.list()

    def test_create_network_error(
        self,
        collection_client: CollectionClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors on create are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.post.side_effect = NetworkError("Connection reset by peer")

        with pytest.raises(NetworkError):
            collection_client.create(name="Test Collection")