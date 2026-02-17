"""Unit tests for TaxonomyClient."""

import pytest
from unittest.mock import MagicMock
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.taxonomy_client import TaxonomyClient
from pharos_cli.client.api_client import SyncAPIClient


class TestTaxonomyClient:
    """Test cases for TaxonomyClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def taxonomy_client(self, mock_api_client: MagicMock) -> TaxonomyClient:
        """Create a TaxonomyClient with mock API client."""
        return TaxonomyClient(mock_api_client)

    def test_list_categories(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing taxonomy categories."""
        mock_api_client.get.return_value = {
            "categories": [
                {
                    "id": "cat-1",
                    "name": "Machine Learning",
                    "parent_id": None,
                    "resource_count": 100,
                    "depth": 0,
                },
                {
                    "id": "cat-2",
                    "name": "Deep Learning",
                    "parent_id": "cat-1",
                    "resource_count": 50,
                    "depth": 1,
                },
            ],
            "total_categories": 2,
        }

        result = taxonomy_client.list_categories()

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/categories",
            params={"include_counts": True},
        )
        assert result["total_categories"] == 2
        assert len(result["categories"]) == 2

    def test_list_categories_with_filters(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing categories with filters."""
        mock_api_client.get.return_value = {
            "categories": [],
            "total_categories": 0,
        }

        result = taxonomy_client.list_categories(
            parent_id="cat-1",
            depth=2,
            include_counts=False,
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["parent_id"] == "cat-1"
        assert params["depth"] == 2
        assert params["include_counts"] is False

    def test_get_category(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a specific category."""
        mock_api_client.get.return_value = {
            "id": "cat-1",
            "name": "Machine Learning",
            "description": "ML category",
            "resource_count": 100,
            "depth": 0,
            "parent_id": None,
            "children": [
                {
                    "id": "cat-2",
                    "name": "Deep Learning",
                    "resource_count": 50,
                },
            ],
        }

        result = taxonomy_client.get_category("cat-1")

        mock_api_client.get.assert_called_once_with("/api/v1/taxonomy/categories/cat-1")
        assert result["id"] == "cat-1"
        assert result["name"] == "Machine Learning"
        assert len(result["children"]) == 1

    def test_get_stats(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting taxonomy statistics."""
        mock_api_client.get.return_value = {
            "total_categories": 50,
            "total_resources": 1000,
            "classified_resources": 800,
            "unclassified_resources": 200,
            "classification_rate": 0.80,
            "model_version": "v1.2.0",
            "last_trained": "2024-01-15T10:30:00Z",
        }

        result = taxonomy_client.get_stats()

        mock_api_client.get.assert_called_once_with("/api/v1/taxonomy/stats")
        assert result["total_categories"] == 50
        assert result["classification_rate"] == 0.80

    def test_classify_resource(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test classifying a resource."""
        mock_api_client.post.return_value = {
            "status": "success",
            "resource_id": "1",
            "categories": [
                {
                    "category_id": "cat-1",
                    "name": "Machine Learning",
                    "confidence": 0.95,
                    "path": ["Technology", "AI", "Machine Learning"],
                },
            ],
        }

        result = taxonomy_client.classify_resource("1")

        mock_api_client.post.assert_called_once_with(
            "/api/v1/taxonomy/classify/1",
            params={},
        )
        assert result["status"] == "success"
        assert len(result["categories"]) == 1
        assert result["categories"][0]["confidence"] == 0.95

    def test_classify_resource_with_force(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test classifying a resource with force flag."""
        mock_api_client.post.return_value = {
            "status": "success",
            "resource_id": "1",
            "categories": [],
        }

        result = taxonomy_client.classify_resource("1", force=True)

        call_args = mock_api_client.post.call_args
        assert call_args[1]["params"]["force"] is True

    def test_classify_resource_batch(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test batch classifying resources."""
        mock_api_client.post.return_value = {
            "status": "completed",
            "processed": 3,
            "successful": 3,
            "failed": 0,
        }

        result = taxonomy_client.classify_resource_batch(
            resource_ids=["1", "2", "3"],
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/taxonomy/classify/batch",
            json={"resource_ids": ["1", "2", "3"]},
        )
        assert result["processed"] == 3

    def test_classify_resource_batch_with_force(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test batch classifying with force flag."""
        mock_api_client.post.return_value = {
            "status": "completed",
            "processed": 2,
            "successful": 2,
            "failed": 0,
        }

        result = taxonomy_client.classify_resource_batch(
            resource_ids=["1", "2"],
            force=True,
        )

        call_args = mock_api_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["force"] is True

    def test_get_classification(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting resource classification."""
        mock_api_client.get.return_value = {
            "resource_id": "1",
            "categories": [
                {
                    "category_id": "cat-1",
                    "name": "Machine Learning",
                    "confidence": 0.90,
                    "path": ["Technology", "AI"],
                },
            ],
            "classified_at": "2024-01-15T10:30:00Z",
            "method": "automatic",
        }

        result = taxonomy_client.get_classification("1")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/resources/1/classification",
        )
        assert result["resource_id"] == "1"
        assert len(result["categories"]) == 1

    def test_remove_classification(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test removing classification from a resource."""
        mock_api_client.delete.return_value = {
            "status": "removed",
            "resource_id": "1",
        }

        result = taxonomy_client.remove_classification("1")

        mock_api_client.delete.assert_called_once_with(
            "/api/v1/taxonomy/resources/1/classification",
        )
        assert result["status"] == "removed"

    def test_train_model(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test training the classification model."""
        mock_api_client.post.return_value = {
            "status": "started",
            "message": "Training started for 10 categories",
            "job_id": "job-123",
        }

        result = taxonomy_client.train_model()

        mock_api_client.post.assert_called_once_with(
            "/api/v1/taxonomy/train",
            json={},
        )
        assert result["status"] == "started"

    def test_train_model_with_categories(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test training with specific categories."""
        mock_api_client.post.return_value = {
            "status": "started",
            "message": "Training started for 2 categories",
            "job_id": "job-456",
        }

        result = taxonomy_client.train_model(
            categories=["cat-1", "cat-2"],
        )

        call_args = mock_api_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["categories"] == ["cat-1", "cat-2"]

    def test_get_training_status(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting training status."""
        mock_api_client.get.return_value = {
            "status": "training",
            "progress": 0.45,
            "eta_seconds": 120,
        }

        result = taxonomy_client.get_training_status()

        mock_api_client.get.assert_called_once_with("/api/v1/taxonomy/train/status")
        assert result["status"] == "training"
        assert result["progress"] == 0.45

    def test_get_model_info(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting model information."""
        mock_api_client.get.return_value = {
            "version": "v1.2.0",
            "status": "ready",
            "accuracy": 0.92,
            "last_trained": "2024-01-15T10:30:00Z",
            "categories_trained": 50,
            "training_samples": 10000,
        }

        result = taxonomy_client.get_model_info()

        mock_api_client.get.assert_called_once_with("/api/v1/taxonomy/model")
        assert result["version"] == "v1.2.0"
        assert result["accuracy"] == 0.92

    def test_get_distribution(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting classification distribution."""
        mock_api_client.get.return_value = {
            "dimension": "category",
            "distribution": [
                {"name": "Machine Learning", "count": 100},
                {"name": "Deep Learning", "count": 75},
            ],
        }

        result = taxonomy_client.get_distribution(dimension="category")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/distribution",
            params={"dimension": "category"},
        )
        assert result["dimension"] == "category"

    def test_search_categories(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test searching categories."""
        mock_api_client.get.return_value = {
            "items": [
                {
                    "id": "cat-1",
                    "name": "Machine Learning",
                    "description": "ML techniques",
                    "resource_count": 50,
                },
            ],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = taxonomy_client.search_categories(query="machine", limit=20)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/search",
            params={"query": "machine", "limit": 20},
        )
        assert result.total == 1
        assert result.items[0]["name"] == "Machine Learning"

    def test_get_health(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check."""
        mock_api_client.get.return_value = {
            "status": "healthy",
            "module": "taxonomy",
            "database": True,
            "model_available": True,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = taxonomy_client.get_health()

        mock_api_client.get.assert_called_once_with("/api/v1/taxonomy/health")
        assert result["status"] == "healthy"
        assert result["database"] is True
        assert result["model_available"] is True

    def test_get_similar_categories(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting similar categories."""
        mock_api_client.get.return_value = {
            "category_id": "cat-1",
            "similar_categories": [
                {
                    "id": "cat-2",
                    "name": "Deep Learning",
                    "similarity": 0.85,
                },
            ],
        }

        result = taxonomy_client.get_similar_categories("cat-1", limit=5)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/categories/cat-1/similar",
            params={"limit": 5},
        )
        assert len(result["similar_categories"]) == 1
        assert result["similar_categories"][0]["similarity"] == 0.85

    def test_export_taxonomy(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting taxonomy."""
        mock_api_client.get.return_value = {
            "format": "json",
            "categories": [
                {
                    "id": "cat-1",
                    "name": "Machine Learning",
                    "parent_id": None,
                    "resource_count": 100,
                },
            ],
        }

        result = taxonomy_client.export_taxonomy(format="json")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/taxonomy/export",
            params={"format": "json"},
        )
        assert result["format"] == "json"
        assert len(result["categories"]) == 1


class TestTaxonomyClientEdgeCases:
    """Edge case tests for TaxonomyClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def taxonomy_client(self, mock_api_client: MagicMock) -> TaxonomyClient:
        """Create a TaxonomyClient with mock API client."""
        return TaxonomyClient(mock_api_client)

    def test_list_categories_empty(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing categories when none exist."""
        mock_api_client.get.return_value = {
            "categories": [],
            "total_categories": 0,
        }

        result = taxonomy_client.list_categories()

        assert result["total_categories"] == 0
        assert result["categories"] == []

    def test_get_category_not_found(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting non-existent category."""
        mock_api_client.get.side_effect = Exception("Category not found")

        with pytest.raises(Exception):
            taxonomy_client.get_category("nonexistent")

    def test_classify_resource_not_found(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test classifying non-existent resource."""
        mock_api_client.post.side_effect = Exception("Resource not found")

        with pytest.raises(Exception):
            taxonomy_client.classify_resource("999")

    def test_get_classification_not_classified(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting classification for unclassified resource."""
        mock_api_client.get.return_value = {
            "resource_id": "1",
            "categories": [],
            "classified_at": None,
        }

        result = taxonomy_client.get_classification("1")

        assert result["categories"] == []

    def test_train_model_error(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test training when model is not available."""
        mock_api_client.post.side_effect = Exception("Model not available")

        with pytest.raises(Exception):
            taxonomy_client.train_model()

    def test_get_health_unhealthy(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check when unhealthy."""
        mock_api_client.get.return_value = {
            "status": "unhealthy",
            "module": "taxonomy",
            "database": True,
            "model_available": False,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = taxonomy_client.get_health()

        assert result["status"] == "unhealthy"
        assert result["model_available"] is False

    def test_search_categories_no_results(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test searching with no results."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = taxonomy_client.search_categories(query="nonexistent")

        assert result.total == 0
        assert len(result.items) == 0

    def test_export_taxonomy_csv(
        self,
        taxonomy_client: TaxonomyClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting taxonomy as CSV."""
        mock_api_client.get.return_value = {
            "format": "csv",
            "categories": [
                {"id": "cat-1", "name": "ML", "parent_id": "", "resource_count": 10},
            ],
        }

        result = taxonomy_client.export_taxonomy(format="csv")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["format"] == "csv"