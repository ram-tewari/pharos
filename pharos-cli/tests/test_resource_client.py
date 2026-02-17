"""Unit tests for ResourceClient."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse


class TestResourceClient:
    """Test cases for ResourceClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def resource_client(self, mock_api_client: MagicMock) -> ResourceClient:
        """Create a ResourceClient with mock API client."""
        return ResourceClient(mock_api_client)

    def test_create_basic(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a resource with basic fields."""
        # Setup mock response
        mock_api_client.post.return_value = {
            "id": 1,
            "title": "Test Resource",
            "content": "Test content",
            "resource_type": "code",
            "language": "python",
        }

        # Call create
        result = resource_client.create(
            title="Test Resource",
            content="Test content",
            resource_type="code",
            language="python",
        )

        # Verify API call
        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources",
            json={
                "title": "Test Resource",
                "content": "Test content",
                "resource_type": "code",
                "language": "python",
            },
        )

        # Verify result
        assert result["id"] == 1
        assert result["title"] == "Test Resource"

    def test_create_with_url(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a resource with URL."""
        mock_api_client.post.return_value = {
            "id": 2,
            "title": "Remote Resource",
            "url": "https://example.com/resource",
            "resource_type": "paper",
        }

        result = resource_client.create(
            title="Remote Resource",
            url="https://example.com/resource",
            resource_type="paper",
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources",
            json={
                "title": "Remote Resource",
                "url": "https://example.com/resource",
                "resource_type": "paper",
            },
        )
        assert result["id"] == 2

    def test_create_with_metadata(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a resource with metadata."""
        mock_api_client.post.return_value = {
            "id": 3,
            "title": "Resource with Metadata",
            "metadata": {"author": "Test Author", "version": "1.0"},
        }

        result = resource_client.create(
            title="Resource with Metadata",
            metadata={"author": "Test Author", "version": "1.0"},
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources",
            json={
                "title": "Resource with Metadata",
                "metadata": {"author": "Test Author", "version": "1.0"},
            },
        )
        assert result["id"] == 3

    def test_list_basic(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing resources without filters."""
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

        result = resource_client.list()

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={"skip": 0, "limit": 100},
        )
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2

    def test_list_with_filters(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing resources with filters."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "title": "Python Code"}],
            "total": 1,
            "page": 1,
            "per_page": 50,
            "has_more": False,
        }

        result = resource_client.list(
            skip=10,
            limit=50,
            resource_type="code",
            language="python",
            query="test",
            min_quality=0.8,
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={
                "skip": 10,
                "limit": 50,
                "resource_type": "code",
                "language": "python",
                "query": "test",
                "min_quality": 0.8,
            },
        )
        assert len(result.items) == 1

    def test_list_with_tags(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing resources with tag filter."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "title": "Tagged Resource"}],
            "total": 1,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = resource_client.list(tags=["important", "python"])

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={
                "skip": 0,
                "limit": 100,
                "tags": "important,python",
            },
        )
        assert len(result.items) == 1

    def test_list_with_collection_id(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing resources filtered by collection."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "title": "Collection Resource"}],
            "total": 1,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = resource_client.list(collection_id=5)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={
                "skip": 0,
                "limit": 100,
                "collection_id": 5,
            },
        )
        assert len(result.items) == 1

    def test_get(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a resource by ID."""
        mock_api_client.get.return_value = {
            "id": 1,
            "title": "Test Resource",
            "content": "Test content",
            "resource_type": "code",
        }

        result = resource_client.get(resource_id=1)

        mock_api_client.get.assert_called_once_with("/api/v1/resources/1")
        assert result.id == 1
        assert result.title == "Test Resource"
        assert result.content == "Test content"
        assert result.resource_type == "code"

    def test_get_not_found(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a resource that doesn't exist raises ResourceNotFoundError."""
        from pharos_cli.client.exceptions import APIError, ResourceNotFoundError

        # Simulate 404 error from API
        mock_api_client.get.side_effect = APIError(
            status_code=404,
            message="Resource not found",
            details={"detail": "Resource not found"},
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            resource_client.get(resource_id=999)

        assert "999" in str(exc_info.value)
        mock_api_client.get.assert_called_once_with("/api/v1/resources/999")

    def test_update_title(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating resource title."""
        mock_api_client.put.return_value = {
            "id": 1,
            "title": "Updated Title",
            "content": "Test content",
        }

        result = resource_client.update(resource_id=1, title="Updated Title")

        mock_api_client.put.assert_called_once_with(
            "/api/v1/resources/1",
            json={"title": "Updated Title"},
        )
        assert result.title == "Updated Title"

    def test_update_multiple_fields(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating multiple fields."""
        mock_api_client.put.return_value = {
            "id": 1,
            "title": "New Title",
            "content": "New content",
            "resource_type": "paper",
            "language": "english",
        }

        result = resource_client.update(
            resource_id=1,
            title="New Title",
            content="New content",
            resource_type="paper",
            language="english",
        )

        mock_api_client.put.assert_called_once_with(
            "/api/v1/resources/1",
            json={
                "title": "New Title",
                "content": "New content",
                "resource_type": "paper",
                "language": "english",
            },
        )
        assert result.title == "New Title"

    def test_update_with_metadata(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating resource metadata."""
        mock_api_client.put.return_value = {
            "id": 1,
            "title": "Test",
            "metadata": {"key": "value"},
        }

        result = resource_client.update(
            resource_id=1,
            metadata={"key": "value"},
        )

        mock_api_client.put.assert_called_once_with(
            "/api/v1/resources/1",
            json={"metadata": {"key": "value"}},
        )
        assert result.metadata["key"] == "value"

    def test_update_returns_resource_model(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that update returns a Resource model, not a dict."""
        from pharos_cli.client.models import Resource

        mock_api_client.put.return_value = {
            "id": 1,
            "title": "Updated Resource",
            "content": "Updated content",
            "resource_type": "code",
            "language": "python",
        }

        result = resource_client.update(resource_id=1, title="Updated Resource")

        assert isinstance(result, Resource)
        assert result.id == 1
        assert result.title == "Updated Resource"
        assert result.content == "Updated content"
        assert result.resource_type == "code"
        assert result.language == "python"

    def test_update_not_found(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating a resource that doesn't exist raises ResourceNotFoundError."""
        from pharos_cli.client.exceptions import APIError, ResourceNotFoundError

        # Simulate 404 error from API
        mock_api_client.put.side_effect = APIError(
            status_code=404,
            message="Resource not found",
            details={"detail": "Resource not found"},
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            resource_client.update(resource_id=999, title="New Title")

        assert "999" in str(exc_info.value)
        mock_api_client.put.assert_called_once_with(
            "/api/v1/resources/999",
            json={"title": "New Title"},
        )

    def test_delete(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting a resource."""
        mock_api_client.delete.return_value = {"success": True, "message": "Resource deleted"}

        result = resource_client.delete(resource_id=1)

        mock_api_client.delete.assert_called_once_with("/api/v1/resources/1")
        assert result["success"] is True
        assert result["message"] == "Resource deleted"

    def test_delete_not_found(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting a resource that doesn't exist raises ResourceNotFoundError."""
        from pharos_cli.client.exceptions import APIError, ResourceNotFoundError

        # Simulate 404 error from API
        mock_api_client.delete.side_effect = APIError(
            status_code=404,
            message="Resource not found",
            details={"detail": "Resource not found"},
        )

        with pytest.raises(ResourceNotFoundError) as exc_info:
            resource_client.delete(resource_id=999)

        assert "999" in str(exc_info.value)
        mock_api_client.delete.assert_called_once_with("/api/v1/resources/999")

    def test_add_to_collection(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test adding a resource to a collection."""
        mock_api_client.post.return_value = {
            "resource_id": 1,
            "collection_id": 5,
            "success": True,
        }

        result = resource_client.add_to_collection(
            resource_id=1,
            collection_id=5,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/collections/5/resources",
            json={"resource_id": 1},
        )
        assert result["success"] is True

    def test_remove_from_collection(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test removing a resource from a collection."""
        mock_api_client.delete.return_value = {"success": True}

        result = resource_client.remove_from_collection(
            resource_id=1,
            collection_id=5,
        )

        mock_api_client.delete.assert_called_once_with(
            "/api/v1/collections/5/resources/1",
        )
        assert result["success"] is True

    def test_get_quality_score(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality score for a resource."""
        mock_api_client.get.return_value = {
            "resource_id": 1,
            "overall_score": 0.85,
            "clarity": 0.9,
            "completeness": 0.8,
            "correctness": 0.9,
            "originality": 0.75,
        }

        result = resource_client.get_quality_score(resource_id=1)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources/1/quality",
        )
        assert result["overall_score"] == 0.85

    def test_get_annotations(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting annotations for a resource."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Note 1"},
                {"id": 2, "text": "Note 2"},
            ],
            "total": 2,
        }

        result = resource_client.get_annotations(resource_id=1)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources/1/annotations",
        )
        assert len(result) == 2
        assert result[0]["text"] == "Note 1"

    def test_get_annotations_empty(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting annotations when list is empty."""
        mock_api_client.get.return_value = {"items": []}

        result = resource_client.get_annotations(resource_id=1)

        assert len(result) == 0

    def test_get_annotations_direct_list(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting annotations when API returns a list directly."""
        mock_api_client.get.return_value = [
            {"id": 1, "text": "Note 1"},
        ]

        result = resource_client.get_annotations(resource_id=1)

        assert len(result) == 1
        assert result[0]["id"] == 1


class TestResourceClientEdgeCases:
    """Edge case tests for ResourceClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def resource_client(self, mock_api_client: MagicMock) -> ResourceClient:
        """Create a ResourceClient with mock API client."""
        return ResourceClient(mock_api_client)

    def test_create_minimal(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a resource with only required fields."""
        mock_api_client.post.return_value = {
            "id": 1,
            "title": "Minimal Resource",
        }

        result = resource_client.create(title="Minimal Resource")

        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources",
            json={"title": "Minimal Resource"},
        )
        assert result["id"] == 1

    def test_list_pagination(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test pagination in list method."""
        mock_api_client.get.return_value = {
            "items": [{"id": 101, "title": "Page 2 Resource"}],
            "total": 150,
            "page": 2,
            "per_page": 50,
            "has_more": True,
        }

        result = resource_client.list(skip=50, limit=50)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={"skip": 50, "limit": 50},
        )
        assert result.page == 2
        assert result.has_more is True

    def test_update_no_fields(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test update with no fields (should send empty dict)."""
        mock_api_client.put.return_value = {"id": 1, "title": "No Change"}

        result = resource_client.update(resource_id=1)

        mock_api_client.put.assert_called_once_with(
            "/api/v1/resources/1",
            json={},
        )
        assert result.id == 1

    def test_list_all_filters_combined(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list with all filters combined."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = resource_client.list(
            skip=0,
            limit=25,
            resource_type="code",
            language="python",
            query="test",
            min_quality=0.5,
            collection_id=1,
            tags=["tag1", "tag2"],
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={
                "skip": 0,
                "limit": 25,
                "resource_type": "code",
                "language": "python",
                "query": "test",
                "min_quality": 0.5,
                "collection_id": 1,
                "tags": "tag1,tag2",
            },
        )

    def test_list_empty_results(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list when no resources match filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = resource_client.list(resource_type="nonexistent")

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 0
        assert result.total == 0
        assert result.has_more is False

    def test_list_boundary_values(
        self,
        resource_client: ResourceClient,
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

        result = resource_client.list(skip=0, limit=0)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={"skip": 0, "limit": 0},
        )
        assert result.per_page == 0

    def test_list_large_pagination(
        self,
        resource_client: ResourceClient,
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

        result = resource_client.list(skip=1000, limit=100)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={"skip": 1000, "limit": 100},
        )
        assert result.page == 11

    def test_create_with_complex_metadata(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating a resource with complex nested metadata."""
        complex_metadata = {
            "author": {"name": "John Doe", "email": "john@example.com"},
            "versions": ["v1.0", "v1.1", "v2.0"],
            "config": {"nested": {"setting": True, "count": 42}},
        }
        mock_api_client.post.return_value = {
            "id": 10,
            "title": "Complex Metadata Resource",
            "metadata": complex_metadata,
        }

        result = resource_client.create(
            title="Complex Metadata Resource",
            metadata=complex_metadata,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources",
            json={"title": "Complex Metadata Resource", "metadata": complex_metadata},
        )
        assert result["id"] == 10
        assert result["metadata"]["author"]["name"] == "John Doe"
        assert result["metadata"]["versions"] == ["v1.0", "v1.1", "v2.0"]

    def test_list_with_single_tag(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test list with a single tag."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "title": "Single Tag Resource"}],
            "total": 1,
            "page": 1,
            "per_page": 100,
            "has_more": False,
        }

        result = resource_client.list(tags=["python"])

        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources",
            params={"skip": 0, "limit": 100, "tags": "python"},
        )
        assert len(result.items) == 1


class TestResourceClientErrorHandling:
    """Error handling tests for ResourceClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def resource_client(self, mock_api_client: MagicMock) -> ResourceClient:
        """Create a ResourceClient with mock API client."""
        return ResourceClient(mock_api_client)

    def test_get_non_404_error_re_raised(
        self,
        resource_client: ResourceClient,
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
            resource_client.get(resource_id=1)

        assert exc_info.value.status_code == 500
        assert "500" in str(exc_info.value)

    def test_update_non_404_error_re_raised(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that non-404 API errors on update are re-raised."""
        from pharos_cli.client.exceptions import APIError

        mock_api_client.put.side_effect = APIError(
            status_code=400,
            message="Validation Error",
            details={"title": ["This field is required"]},
        )

        with pytest.raises(APIError) as exc_info:
            resource_client.update(resource_id=1, title="New Title")

        assert exc_info.value.status_code == 400

    def test_delete_non_404_error_re_raised(
        self,
        resource_client: ResourceClient,
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
            resource_client.delete(resource_id=1)

        assert exc_info.value.status_code == 403

    def test_get_network_error(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.get.side_effect = NetworkError(
            "Connection refused"
        )

        with pytest.raises(NetworkError) as exc_info:
            resource_client.get(resource_id=1)

        assert "Connection refused" in str(exc_info.value)

    def test_list_network_error(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors on list are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.get.side_effect = NetworkError(
            "Connection timeout"
        )

        with pytest.raises(NetworkError):
            resource_client.list()

    def test_create_network_error(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that network errors on create are propagated."""
        from pharos_cli.client.exceptions import NetworkError

        mock_api_client.post.side_effect = NetworkError(
            "Connection reset by peer"
        )

        with pytest.raises(NetworkError):
            resource_client.create(title="Test Resource")


class TestResourceClientModelValidation:
    """Model validation tests for ResourceClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def resource_client(self, mock_api_client: MagicMock) -> ResourceClient:
        """Create a ResourceClient with mock API client."""
        return ResourceClient(mock_api_client)

    def test_get_returns_resource_model(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that get returns a Resource model with all fields."""
        from pharos_cli.client.models import Resource

        mock_api_client.get.return_value = {
            "id": 42,
            "title": "Full Resource",
            "content": "Full content here",
            "resource_type": "documentation",
            "language": "markdown",
            "url": "https://example.com/doc",
            "quality_score": 0.92,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T14:20:00Z",
        }

        result = resource_client.get(resource_id=42)

        assert isinstance(result, Resource)
        assert result.id == 42
        assert result.title == "Full Resource"
        assert result.content == "Full content here"
        assert result.resource_type == "documentation"
        assert result.language == "markdown"
        assert result.url == "https://example.com/doc"

    def test_update_returns_resource_model(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that update returns a Resource model."""
        from pharos_cli.client.models import Resource

        mock_api_client.put.return_value = {
            "id": 1,
            "title": "Updated",
            "content": "Updated content",
            "resource_type": "code",
            "language": "python",
        }

        result = resource_client.update(resource_id=1, title="Updated")

        assert isinstance(result, Resource)
        assert result.title == "Updated"

    def test_list_returns_paginated_response(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that list returns a PaginatedResponse with correct metadata."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "title": "Resource 1"},
                {"id": 2, "title": "Resource 2"},
                {"id": 3, "title": "Resource 3"},
            ],
            "total": 50,
            "page": 1,
            "per_page": 3,
            "has_more": True,
        }

        result = resource_client.list(limit=3)

        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 3
        assert result.total == 50
        assert result.page == 1
        assert result.per_page == 3
        assert result.has_more is True

    def test_get_annotations_returns_list(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that get_annotations returns a list of dicts."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "type": "highlight", "text": "Important note"},
                {"id": 2, "type": "note", "text": "Another note"},
            ],
            "total": 2,
        }

        result = resource_client.get_annotations(resource_id=1)

        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], dict)
        assert result[0]["type"] == "highlight"

    def test_get_quality_score_returns_dict(
        self,
        resource_client: ResourceClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test that get_quality_score returns a dict with scores."""
        mock_api_client.get.return_value = {
            "resource_id": 1,
            "overall_score": 0.87,
            "dimensions": {
                "clarity": 0.9,
                "completeness": 0.85,
                "correctness": 0.88,
                "originality": 0.82,
            },
        }

        result = resource_client.get_quality_score(resource_id=1)

        assert isinstance(result, dict)
        assert result["overall_score"] == 0.87
        assert "dimensions" in result
        assert result["dimensions"]["clarity"] == 0.9