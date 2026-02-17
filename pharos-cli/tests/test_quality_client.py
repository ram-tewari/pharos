"""Unit tests for QualityClient."""

import pytest
from unittest.mock import MagicMock
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.quality_client import QualityClient
from pharos_cli.client.api_client import SyncAPIClient


class TestQualityClient:
    """Test cases for QualityClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def quality_client(self, mock_api_client: MagicMock) -> QualityClient:
        """Create a QualityClient with mock API client."""
        return QualityClient(mock_api_client)

    def test_get_quality_details(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality details for a resource."""
        mock_api_client.get.return_value = {
            "resource_id": "1",
            "quality_dimensions": {
                "accuracy": 0.85,
                "completeness": 0.75,
                "consistency": 0.80,
                "timeliness": 0.70,
                "relevance": 0.90,
            },
            "quality_overall": 0.80,
            "quality_weights": {
                "accuracy": 0.30,
                "completeness": 0.25,
                "consistency": 0.20,
                "timeliness": 0.15,
                "relevance": 0.10,
            },
            "quality_last_computed": "2024-01-15T10:30:00Z",
            "is_quality_outlier": False,
            "needs_quality_review": False,
        }

        result = quality_client.get_quality_details("1")

        mock_api_client.get.assert_called_once_with("/api/v1/quality/resources/1/quality-details")
        assert result["resource_id"] == "1"
        assert result["quality_overall"] == 0.80
        assert "accuracy" in result["quality_dimensions"]

    def test_get_quality_score(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality score summary."""
        mock_api_client.get.return_value = {
            "resource_id": "1",
            "quality_dimensions": {
                "accuracy": 0.85,
                "completeness": 0.75,
            },
            "quality_overall": 0.80,
            "is_quality_outlier": False,
            "needs_quality_review": False,
            "quality_last_computed": "2024-01-15T10:30:00Z",
        }

        result = quality_client.get_quality_score("1")

        mock_api_client.get.assert_called_once_with("/api/v1/quality/resources/1/quality-details")
        assert result["resource_id"] == "1"
        assert result["quality_overall"] == 0.80
        assert result["is_quality_outlier"] is False

    def test_get_outliers(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality outliers."""
        mock_api_client.get.return_value = {
            "items": [
                {
                    "resource_id": "1",
                    "title": "Test Resource 1",
                    "quality_overall": 0.30,
                    "outlier_score": 0.85,
                    "outlier_reasons": ["low_accuracy"],
                    "needs_quality_review": True,
                }
            ],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = quality_client.get_outliers(page=1, limit=20)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/quality/outliers",
            params={"page": 1, "limit": 20},
        )
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]["resource_id"] == "1"

    def test_get_outliers_with_filters(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting outliers with filters."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = quality_client.get_outliers(
            page=1,
            limit=50,
            min_outlier_score=0.5,
            reason="low_accuracy",
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["page"] == 1
        assert params["limit"] == 50
        assert params["min_outlier_score"] == 0.5
        assert params["reason"] == "low_accuracy"

    def test_get_distribution(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality distribution."""
        mock_api_client.get.return_value = {
            "dimension": "overall",
            "bins": 10,
            "distribution": [
                {"range": "0.0-0.1", "count": 5},
                {"range": "0.1-0.2", "count": 10},
            ],
            "statistics": {
                "mean": 0.65,
                "median": 0.70,
                "std_dev": 0.15,
            },
        }

        result = quality_client.get_distribution(bins=10, dimension="overall")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/quality/distribution",
            params={"bins": 10, "dimension": "overall"},
        )
        assert result["dimension"] == "overall"
        assert result["statistics"]["mean"] == 0.65

    def test_get_dimension_averages(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting dimension averages."""
        mock_api_client.get.return_value = {
            "dimensions": {
                "accuracy": {"avg": 0.75, "min": 0.50, "max": 0.95},
                "completeness": {"avg": 0.80, "min": 0.60, "max": 1.00},
            },
            "overall": {"avg": 0.78, "min": 0.55, "max": 0.98},
            "total_resources": 100,
        }

        result = quality_client.get_dimension_averages()

        mock_api_client.get.assert_called_once_with("/api/v1/quality/quality/dimensions")
        assert result["dimensions"]["accuracy"]["avg"] == 0.75
        assert result["total_resources"] == 100

    def test_get_trends(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality trends."""
        mock_api_client.get.return_value = {
            "dimension": "overall",
            "granularity": "weekly",
            "data_points": [
                {"period": "2024-W01", "avg_quality": 0.70, "resource_count": 50},
                {"period": "2024-W02", "avg_quality": 0.72, "resource_count": 55},
            ],
        }

        result = quality_client.get_trends(
            granularity="weekly",
            dimension="overall",
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/quality/trends",
            params={
                "granularity": "weekly",
                "dimension": "overall",
            },
        )
        assert len(result["data_points"]) == 2

    def test_get_trends_with_dates(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting trends with date range."""
        mock_api_client.get.return_value = {
            "dimension": "overall",
            "granularity": "daily",
            "data_points": [],
        }

        result = quality_client.get_trends(
            granularity="daily",
            start_date="2024-01-01",
            end_date="2024-01-31",
        )

        call_args = mock_api_client.get.call_args
        params = call_args[1]["params"]
        assert params["start_date"] == "2024-01-01"
        assert params["end_date"] == "2024-01-31"

    def test_get_degradation_report(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting degradation report."""
        mock_api_client.get.return_value = {
            "time_window_days": 30,
            "degraded_count": 5,
            "degraded_resources": [
                {
                    "resource_id": "1",
                    "title": "Test Resource",
                    "old_quality": 0.80,
                    "new_quality": 0.50,
                    "degradation_pct": 37.5,
                }
            ],
        }

        result = quality_client.get_degradation_report(time_window_days=30)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/quality/degradation",
            params={"time_window_days": 30},
        )
        assert result["degraded_count"] == 5

    def test_get_review_queue(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting review queue."""
        mock_api_client.get.return_value = {
            "items": [
                {
                    "resource_id": "1",
                    "title": "Test Resource",
                    "quality_overall": 0.40,
                    "is_quality_outlier": True,
                    "outlier_score": 0.90,
                    "quality_last_computed": "2024-01-15T10:30:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = quality_client.get_review_queue(page=1, limit=20)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/quality/review-queue",
            params={"page": 1, "limit": 20, "sort_by": "outlier_score"},
        )
        assert result.total == 1

    def test_recompute_quality_single(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test recomputing quality for a single resource."""
        mock_api_client.post.return_value = {
            "status": "accepted",
            "message": "Quality computation queued for 1 resource(s)",
        }

        result = quality_client.recompute_quality(resource_id="1")

        mock_api_client.post.assert_called_once_with(
            "/api/v1/quality/quality/recalculate",
            json={"resource_id": "1"},
        )
        assert result["status"] == "accepted"

    def test_recompute_quality_multiple(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test recomputing quality for multiple resources."""
        mock_api_client.post.return_value = {
            "status": "completed",
            "message": "Quality computation completed for 3 resource(s)",
        }

        result = quality_client.recompute_quality(resource_ids=["1", "2", "3"])

        call_args = mock_api_client.post.call_args
        json_data = call_args[1]["json"]
        assert "resource_ids" in json_data
        assert len(json_data["resource_ids"]) == 3

    def test_recompute_quality_with_weights(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test recomputing quality with custom weights."""
        mock_api_client.post.return_value = {
            "status": "completed",
            "message": "Quality computation completed for 1 resource(s)",
        }

        weights = {
            "accuracy": 0.40,
            "completeness": 0.30,
            "consistency": 0.15,
            "timeliness": 0.10,
            "relevance": 0.05,
        }

        result = quality_client.recompute_quality(resource_id="1", weights=weights)

        call_args = mock_api_client.post.call_args
        json_data = call_args[1]["json"]
        assert json_data["weights"] == weights

    def test_get_collection_quality_report(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting collection quality report."""
        mock_api_client.get.return_value = {
            "collection_id": "1",
            "summary": {
                "total_resources": 50,
                "avg_quality": 0.75,
                "outlier_count": 3,
            },
            "distribution": {
                "overall": {"mean": 0.75, "median": 0.78},
            },
            "recommendations": [
                "Review 3 low-quality resources",
                "Consider adding more complete metadata",
            ],
            "outliers": [
                {
                    "resource_id": "1",
                    "quality_overall": 0.35,
                    "issue": "Low accuracy score",
                }
            ],
        }

        result = quality_client.get_collection_quality_report(collection_id="1")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/quality/collections/1/quality-report",
        )
        assert result["summary"]["total_resources"] == 50
        assert len(result["recommendations"]) == 2

    def test_get_health(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check."""
        mock_api_client.get.return_value = {
            "status": "healthy",
            "module": "quality",
            "database": True,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = quality_client.get_health()

        mock_api_client.get.assert_called_once_with("/api/v1/quality/quality/health")
        assert result["status"] == "healthy"
        assert result["database"] is True


class TestQualityClientEdgeCases:
    """Edge case tests for QualityClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def quality_client(self, mock_api_client: MagicMock) -> QualityClient:
        """Create a QualityClient with mock API client."""
        return QualityClient(mock_api_client)

    def test_get_quality_details_not_found(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting quality details for non-existent resource."""
        mock_api_client.get.side_effect = Exception("Resource not found")

        with pytest.raises(Exception):
            quality_client.get_quality_details("999")

    def test_get_outliers_empty(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting outliers when none exist."""
        mock_api_client.get.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

        result = quality_client.get_outliers()

        assert result.total == 0
        assert len(result.items) == 0

    def test_get_distribution_empty(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting distribution when no data exists."""
        mock_api_client.get.return_value = {
            "dimension": "overall",
            "bins": 10,
            "distribution": [],
            "statistics": {
                "mean": 0.0,
                "median": 0.0,
                "std_dev": 0.0,
            },
        }

        result = quality_client.get_distribution()

        assert result["distribution"] == []
        assert result["statistics"]["mean"] == 0.0

    def test_get_trends_no_data(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting trends when no data exists."""
        mock_api_client.get.return_value = {
            "dimension": "overall",
            "granularity": "weekly",
            "data_points": [],
        }

        result = quality_client.get_trends()

        assert result["data_points"] == []

    def test_recompute_quality_error(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test recompute quality when API fails."""
        mock_api_client.post.side_effect = Exception("API error")

        with pytest.raises(Exception):
            quality_client.recompute_quality(resource_id="1")

    def test_get_collection_report_not_found(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting collection report for non-existent collection."""
        mock_api_client.get.side_effect = Exception("Collection not found")

        with pytest.raises(Exception):
            quality_client.get_collection_quality_report("999")

    def test_get_health_unhealthy(
        self,
        quality_client: QualityClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check when module is unhealthy."""
        mock_api_client.get.return_value = {
            "status": "unhealthy",
            "module": "quality",
            "database": False,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = quality_client.get_health()

        assert result["status"] == "unhealthy"
        assert result["database"] is False