"""Unit tests for AnnotationClient."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.annotation_client import AnnotationClient
from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import Annotation, PaginatedResponse
from pharos_cli.client.exceptions import AnnotationNotFoundError, APIError


class TestAnnotationClient:
    """Test cases for AnnotationClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def annotation_client(self, mock_api_client: MagicMock) -> AnnotationClient:
        """Create an AnnotationClient with mock API client."""
        return AnnotationClient(mock_api_client)

    def test_create_basic(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating an annotation with basic fields."""
        # Setup mock response
        mock_api_client.post.return_value = {
            "id": 1,
            "resource_id": 123,
            "text": "Test annotation",
            "annotation_type": "highlight",
            "tags": ["important"],
            "created_at": "2024-01-01T10:00:00Z",
        }

        # Call create
        result = annotation_client.create(
            resource_id=123,
            text="Test annotation",
            annotation_type="highlight",
            tags=["important"],
        )

        # Verify API call
        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources/123/annotations",
            json={
                "text": "Test annotation",
                "annotation_type": "highlight",
                "tags": ["important"],
            },
        )

        # Verify result
        assert result["id"] == 1
        assert result["resource_id"] == 123
        assert result["text"] == "Test annotation"

    def test_create_with_offsets(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test creating an annotation with character offsets."""
        # Setup mock response
        mock_api_client.post.return_value = {
            "id": 2,
            "resource_id": 123,
            "text": "Highlighted text",
            "annotation_type": "highlight",
            "start_offset": 100,
            "end_offset": 150,
            "tags": [],
        }

        # Call create with offsets
        result = annotation_client.create(
            resource_id=123,
            text="Highlighted text",
            annotation_type="highlight",
            start_offset=100,
            end_offset=150,
        )

        # Verify API call
        mock_api_client.post.assert_called_once_with(
            "/api/v1/resources/123/annotations",
            json={
                "text": "Highlighted text",
                "annotation_type": "highlight",
                "start_offset": 100,
                "end_offset": 150,
            },
        )

        # Verify result
        assert result["id"] == 2
        assert result["start_offset"] == 100
        assert result["end_offset"] == 150

    def test_list_for_resource(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing annotations for a resource."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Note 1", "resource_id": 123},
                {"id": 2, "text": "Note 2", "resource_id": 123},
            ]
        }

        # Call list_for_resource
        result = annotation_client.list_for_resource(resource_id=123)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources/123/annotations",
            params={},
        )

        # Verify result
        assert len(result) == 2
        assert result[0]["text"] == "Note 1"
        assert result[1]["text"] == "Note 2"

    def test_list_for_resource_with_filters(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing annotations for a resource with filters."""
        # Setup mock response
        mock_api_client.get.return_value = {"items": []}

        # Call list_for_resource with filters
        result = annotation_client.list_for_resource(
            resource_id=123,
            include_shared=True,
            tags=["important", "review"],
        )

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/resources/123/annotations",
            params={"include_shared": "true", "tags": "important,review"},
        )

        # Verify result
        assert result == []

    def test_list_for_resource_direct_list(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing annotations when API returns a list directly."""
        # Setup mock response (list instead of dict with items)
        mock_api_client.get.return_value = [
            {"id": 1, "text": "Note 1"},
            {"id": 2, "text": "Note 2"},
        ]

        # Call list_for_resource
        result = annotation_client.list_for_resource(resource_id=123)

        # Verify result
        assert len(result) == 2
        assert isinstance(result, list)

    def test_list_all(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing all annotations with pagination."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Note 1", "resource_id": 123},
                {"id": 2, "text": "Note 2", "resource_id": 456},
            ],
            "total": 2,
            "page": 1,
            "per_page": 50,
            "has_more": False,
        }

        # Call list_all
        result = annotation_client.list_all(limit=50, offset=0, sort_by="recent")

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations",
            params={"limit": 50, "offset": 0, "sort_by": "recent"},
        )

        # Verify result
        assert isinstance(result, PaginatedResponse)
        assert len(result.items) == 2
        assert result.total == 2
        assert result.page == 1

    def test_get_success(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting an annotation by ID."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "id": 1,
            "resource_id": 123,
            "text": "Test annotation",
            "annotation_type": "note",
            "tags": ["important"],
            "created_at": "2024-01-01T10:00:00Z",
        }

        # Call get
        result = annotation_client.get(annotation_id=1)

        # Verify API call
        mock_api_client.get.assert_called_once_with("/api/v1/annotations/1")

        # Verify result
        assert isinstance(result, Annotation)
        assert result.id == 1
        assert result.text == "Test annotation"
        assert result.annotation_type == "note"

    def test_get_not_found(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a non-existent annotation."""
        # Setup mock to raise 404 error
        mock_api_client.get.side_effect = APIError(
            status_code=404,
            message="Annotation not found",
        )

        # Call get and expect AnnotationNotFoundError
        with pytest.raises(AnnotationNotFoundError) as exc_info:
            annotation_client.get(annotation_id=999)

        # Verify error message
        assert "Annotation with ID 999 not found" in str(exc_info.value)

    def test_update_success(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating an annotation."""
        # Setup mock response
        mock_api_client.put.return_value = {
            "id": 1,
            "resource_id": 123,
            "text": "Updated annotation",
            "annotation_type": "note",
            "tags": ["important", "updated"],
            "updated_at": "2024-01-01T11:00:00Z",
        }

        # Call update
        result = annotation_client.update(
            annotation_id=1,
            text="Updated annotation",
            tags=["important", "updated"],
        )

        # Verify API call
        mock_api_client.put.assert_called_once_with(
            "/api/v1/annotations/1",
            json={"text": "Updated annotation", "tags": ["important", "updated"]},
        )

        # Verify result
        assert isinstance(result, Annotation)
        assert result.text == "Updated annotation"
        assert "updated" in result.tags

    def test_update_not_found(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test updating a non-existent annotation."""
        # Setup mock to raise 404 error
        mock_api_client.put.side_effect = APIError(
            status_code=404,
            message="Annotation not found",
        )

        # Call update and expect AnnotationNotFoundError
        with pytest.raises(AnnotationNotFoundError) as exc_info:
            annotation_client.update(annotation_id=999, text="Updated")

        # Verify error message
        assert "Annotation with ID 999 not found" in str(exc_info.value)

    def test_delete_success(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting an annotation."""
        # Setup mock response
        mock_api_client.delete.return_value = {"success": True}

        # Call delete
        result = annotation_client.delete(annotation_id=1)

        # Verify API call
        mock_api_client.delete.assert_called_once_with("/api/v1/annotations/1")

        # Verify result
        assert result["success"] is True

    def test_delete_not_found(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test deleting a non-existent annotation."""
        # Setup mock to raise 404 error
        mock_api_client.delete.side_effect = APIError(
            status_code=404,
            message="Annotation not found",
        )

        # Call delete and expect AnnotationNotFoundError
        with pytest.raises(AnnotationNotFoundError) as exc_info:
            annotation_client.delete(annotation_id=999)

        # Verify error message
        assert "Annotation with ID 999 not found" in str(exc_info.value)

    def test_search_fulltext(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test full-text search."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Note about machine learning", "similarity_score": None},
                {"id": 2, "text": "Another note about AI", "similarity_score": None},
            ],
            "total": 2,
            "query": "machine learning",
        }

        # Call search_fulltext
        result = annotation_client.search_fulltext(query="machine learning", limit=50)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations/search/fulltext",
            params={"query": "machine learning", "limit": 50},
        )

        # Verify result
        assert len(result["items"]) == 2
        assert result["query"] == "machine learning"

    def test_search_semantic(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test semantic search."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Note about deep learning", "similarity_score": 0.87},
                {"id": 2, "text": "Another note about neural networks", "similarity_score": 0.75},
            ],
            "total": 2,
            "query": "deep learning concepts",
        }

        # Call search_semantic
        result = annotation_client.search_semantic(query="deep learning concepts", limit=10)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations/search/semantic",
            params={"query": "deep learning concepts", "limit": 10},
        )

        # Verify result
        assert len(result["items"]) == 2
        assert result["items"][0]["similarity_score"] == 0.87

    def test_search_tags(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test tag search."""
        # Setup mock response
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "text": "Important note", "tags": ["important", "review"]},
                {"id": 2, "text": "Another note", "tags": ["important"]},
            ],
            "total": 2,
            "query": "tags: important, review",
        }

        # Call search_tags
        result = annotation_client.search_tags(tags=["important", "review"], match_all=False)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations/search/tags",
            params={"match_all": "false", "tags": ["important", "review"]},
        )

        # Verify result
        assert len(result["items"]) == 2
        assert "important" in result["items"][0]["tags"]

    def test_export_markdown(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting annotations to markdown."""
        # Setup mock response
        mock_api_client.get.return_value = "# Annotations Export\n\n## Resource 123\n\n### Note 1\nText"

        # Call export_markdown
        result = annotation_client.export_markdown(resource_id=123)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations/export/markdown",
            params={"resource_id": 123},
        )

        # Verify result
        assert result.startswith("# Annotations Export")

    def test_export_json(
        self,
        annotation_client: AnnotationClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting annotations to JSON."""
        # Setup mock response
        mock_api_client.get.return_value = [
            {"id": 1, "text": "Note 1", "resource_id": 123},
            {"id": 2, "text": "Note 2", "resource_id": 123},
        ]

        # Call export_json
        result = annotation_client.export_json(resource_id=123)

        # Verify API call
        mock_api_client.get.assert_called_once_with(
            "/api/v1/annotations/export/json",
            params={"resource_id": 123},
        )

        # Verify result
        assert len(result) == 2
        assert result[0]["resource_id"] == 123