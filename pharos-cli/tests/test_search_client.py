"""Unit tests for SearchClient."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.search_client import (
    SearchClient,
)
from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse, SearchResult


class TestSearchClient:
    """Test cases for SearchClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def search_client(self, mock_api_client: MagicMock) -> SearchClient:
        """Create a SearchClient with mock API client."""
        return SearchClient(mock_api_client)

    def test_search_basic(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test basic search."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "title": "ML Paper", "score": 0.9},
                {"id": 2, "title": "Deep Learning", "score": 0.8},
            ],
            "total": 2,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(query="machine learning")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == "/api/v1/search"
        assert call_args[1]["params"]["query"] == "machine learning"
        assert call_args[1]["params"]["limit"] == 100

        assert result.total == 2
        assert len(result.items) == 2
        # Items are dicts, not SearchResult objects
        assert result.items[0]["id"] == 1
        assert result.items[0]["title"] == "ML Paper"
        assert result.items[0]["score"] == 0.9

    def test_search_with_pagination(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with pagination."""
        mock_api_client.get.return_value = {
            "items": [{"id": 3, "title": "Python Guide"}],
            "total": 100,
            "page": 3,
            "per_page": 10,
            "has_more": True,
        }

        result = search_client.search(
            query="python",
            skip=20,
            limit=10,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["skip"] == 20
        assert call_args[1]["params"]["limit"] == 10

    def test_search_with_filters(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(
            query="test",
            resource_type="code",
            language="python",
            min_quality=0.8,
            tags=["important", "tutorial"],
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["resource_type"] == "code"
        assert params["language"] == "python"
        assert params["min_quality"] == 0.8
        assert params["tags"] == "important,tutorial"

    def test_search_with_hybrid_weight(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with hybrid weight."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(
            query="test",
            search_type="hybrid",
            weight=0.7,
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["type"] == "hybrid"
        assert params["weight"] == 0.7

    def test_semantic_search_basic(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test basic semantic search."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 5, "title": "Neural Networks", "score": 0.95},
            ],
            "total": 1,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.semantic_search(query="neural networks")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == "/api/v1/search"
        assert call_args[1]["params"]["type"] == "semantic"

        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]["id"] == 5
        assert result.items[0]["score"] == 0.95

    def test_hybrid_search_basic(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test basic hybrid search."""
        mock_api_client.get.return_value = {
            "total": 10,
            "items": [
                {"id": 1, "title": "Hybrid Result 1", "score": 0.92},
                {"id": 2, "title": "Hybrid Result 2", "score": 0.88},
            ],
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.hybrid_search(query="AI")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == "/api/v1/search"
        assert call_args[1]["params"]["type"] == "hybrid"
        assert call_args[1]["params"]["weight"] == 0.5  # default weight

        assert result.total == 10
        assert len(result.items) == 2

    def test_hybrid_search_with_custom_weight(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test hybrid search with custom weight."""
        mock_api_client.get.return_value = {
            "total": 5,
            "items": [],
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.hybrid_search(
            query="test",
            weight=0.7,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["weight"] == 0.7

    def test_keyword_search_basic(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test basic keyword search."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": 1, "title": "Keyword Result", "score": 0.85},
            ],
            "total": 1,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.keyword_search(query="def function")

        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert call_args[0][0] == "/api/v1/search"
        assert call_args[1]["params"]["type"] == "keyword"

        assert result.total == 1
        assert result.items[0]["title"] == "Keyword Result"

    def test_keyword_search_with_filters(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test keyword search with filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.keyword_search(
            query="import pandas",
            resource_type="code",
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["type"] == "keyword"
        assert params["resource_type"] == "code"


class TestSearchClientEdgeCases:
    """Edge case tests for SearchClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def search_client(self, mock_api_client: MagicMock) -> SearchClient:
        """Create a SearchClient with mock API client."""
        return SearchClient(mock_api_client)

    def test_search_empty_results(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with no results."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(query="nonexistent")

        assert result.total == 0
        assert len(result.items) == 0

    def test_search_with_collection_filter(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with collection filter."""
        mock_api_client.get.return_value = {
            "items": [{"id": 1, "title": "Collection Result"}],
            "total": 1,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(
            query="test",
            collection_id=5,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["collection_id"] == 5

    def test_search_with_max_quality(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with max quality filter."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.search(
            query="test",
            max_quality=0.9,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["max_quality"] == 0.9

    def test_search_pagination_boundary(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test search with boundary pagination values."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 101,
            "per_page": 10,
            "has_more": False,
        }

        result = search_client.search(
            query="test",
            skip=1000,
            limit=10,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["skip"] == 1000
        assert call_args[1]["params"]["limit"] == 10

    def test_semantic_search_with_all_filters(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test semantic search with all filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.semantic_search(
            query="neural networks",
            resource_type="paper",
            language="en",
            min_quality=0.8,
            max_quality=0.95,
            tags=["ai", "ml"],
            collection_id=1,
            skip=0,
            limit=50,
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["type"] == "semantic"
        assert params["resource_type"] == "paper"
        assert params["language"] == "en"
        assert params["min_quality"] == 0.8
        assert params["max_quality"] == 0.95
        assert params["tags"] == "ai,ml"
        assert params["collection_id"] == 1
        assert params["limit"] == 50

    def test_hybrid_search_with_all_filters(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test hybrid search with all filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.hybrid_search(
            query="machine learning",
            weight=0.7,
            resource_type="documentation",
            language="python",
            min_quality=0.6,
            tags=["tutorial"],
            collection_id=2,
            skip=10,
            limit=20,
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["type"] == "hybrid"
        assert params["weight"] == 0.7
        assert params["resource_type"] == "documentation"
        assert params["language"] == "python"
        assert params["min_quality"] == 0.6
        assert params["tags"] == "tutorial"
        assert params["collection_id"] == 2
        assert params["skip"] == 10
        assert params["limit"] == 20

    def test_keyword_search_with_all_filters(
        self,
        search_client: SearchClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test keyword search with all filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 25,
            "has_more": False,
        }

        result = search_client.keyword_search(
            query="def function",
            resource_type="code",
            language="python",
            min_quality=0.5,
            max_quality=0.9,
            tags=["function", "definition"],
            collection_id=3,
            skip=5,
            limit=15,
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["type"] == "keyword"
        assert params["resource_type"] == "code"
        assert params["language"] == "python"
        assert params["min_quality"] == 0.5
        assert params["max_quality"] == 0.9
        assert params["tags"] == "function,definition"
        assert params["collection_id"] == 3
        assert params["skip"] == 5
        assert params["limit"] == 15