"""Tests for recommendation client."""

import pytest
from unittest.mock import MagicMock, patch
from pharos_cli.client.recommendation_client import RecommendationClient
from pharos_cli.client.models import PaginatedResponse


class TestRecommendationClient:
    """Test cases for the RecommendationClient class."""

    @pytest.fixture
    def mock_api_client(self):
        """Create a mock API client for testing."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def client(self, mock_api_client):
        """Create a RecommendationClient instance with mock API client."""
        return RecommendationClient(mock_api_client)

    @pytest.fixture
    def sample_recommendations(self):
        """Create sample recommendations for testing."""
        return {
            "items": [
                {
                    "id": 1,
                    "title": "Recommended Resource 1",
                    "resource_type": "paper",
                    "language": "en",
                    "score": 0.95,
                },
                {
                    "id": 2,
                    "title": "Recommended Resource 2",
                    "resource_type": "code",
                    "language": "python",
                    "score": 0.87,
                },
                {
                    "id": 3,
                    "title": "Recommended Resource 3",
                    "resource_type": "documentation",
                    "language": "en",
                    "score": 0.82,
                },
            ],
            "total": 3,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }

    def test_get_user_recommendations(self, client, mock_api_client, sample_recommendations):
        """Test getting recommendations for a user."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_user_recommendations(user_id=1, limit=10, skip=0)

        assert isinstance(result, PaginatedResponse)
        assert result.total == 3
        assert len(result.items) == 3
        mock_api_client.get.assert_called_once()
        call_params = mock_api_client.get.call_args[1]["params"]
        assert call_params["user_id"] == 1
        assert call_params["limit"] == 10
        assert call_params["skip"] == 0

    def test_get_user_recommendations_with_explanation(self, client, mock_api_client, sample_recommendations):
        """Test getting recommendations with explanation flag."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_user_recommendations(
            user_id=1, limit=10, skip=0, include_explanation=True
        )

        call_params = mock_api_client.get.call_args[1]["params"]
        assert call_params["include_explanation"] == "true"

    def test_get_similar_resources(self, client, mock_api_client, sample_recommendations):
        """Test getting similar resources."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_similar_resources(resource_id=1, limit=10, skip=0)

        assert isinstance(result, PaginatedResponse)
        assert result.total == 3
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert "/api/v1/resources/1/similar" in call_args[0][0]
        call_params = call_args[1]["params"]
        assert call_params["limit"] == 10
        assert call_params["skip"] == 0

    def test_get_similar_resources_with_explanation(self, client, mock_api_client, sample_recommendations):
        """Test getting similar resources with explanation flag."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_similar_resources(
            resource_id=1, limit=10, skip=0, include_explanation=True
        )

        call_params = mock_api_client.get.call_args[1]["params"]
        assert call_params["include_explanation"] == "true"

    def test_explain_recommendation(self, client, mock_api_client):
        """Test explaining a recommendation."""
        explanation_data = {
            "resource_id": 1,
            "score": 0.95,
            "reasons": ["Similar to your recent reads", "High quality score"],
            "factors": {
                "content_similarity": 0.8,
                "user_interest_match": 0.9,
                "quality_score": 0.95,
            },
        }
        mock_api_client.get.return_value = explanation_data

        result = client.explain_recommendation(resource_id=1, user_id=1)

        assert result["resource_id"] == 1
        assert result["score"] == 0.95
        assert "reasons" in result
        assert "factors" in result
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert "/api/v1/recommendations/explain/1" in call_args[0][0]

    def test_explain_recommendation_without_user(self, client, mock_api_client):
        """Test explaining a recommendation without user ID."""
        explanation_data = {
            "resource_id": 1,
            "score": 0.95,
            "reasons": ["Popular in your field"],
        }
        mock_api_client.get.return_value = explanation_data

        result = client.explain_recommendation(resource_id=1)

        call_params = mock_api_client.get.call_args[1]["params"]
        assert "user_id" not in call_params

    def test_get_trending_resources(self, client, mock_api_client, sample_recommendations):
        """Test getting trending resources."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_trending_resources(limit=10, time_range="week")

        assert isinstance(result, PaginatedResponse)
        assert result.total == 3
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert "/api/v1/recommendations/trending" in call_args[0][0]
        call_params = call_args[1]["params"]
        assert call_params["limit"] == 10
        assert call_params["time_range"] == "week"

    def test_get_trending_resources_different_time_ranges(self, client, mock_api_client, sample_recommendations):
        """Test getting trending resources with different time ranges."""
        mock_api_client.get.return_value = sample_recommendations

        for time_range in ["day", "week", "month"]:
            result = client.get_trending_resources(limit=10, time_range=time_range)
            call_params = mock_api_client.get.call_args[1]["params"]
            assert call_params["time_range"] == time_range

    def test_get_personalized_feed(self, client, mock_api_client, sample_recommendations):
        """Test getting personalized feed."""
        mock_api_client.get.return_value = sample_recommendations

        result = client.get_personalized_feed(user_id=1, limit=20, offset=0)

        assert isinstance(result, PaginatedResponse)
        assert result.total == 3
        mock_api_client.get.assert_called_once()
        call_args = mock_api_client.get.call_args
        assert "/api/v1/users/1/feed" in call_args[0][0]
        call_params = call_args[1]["params"]
        assert call_params["limit"] == 20
        assert call_params["offset"] == 0

    def test_get_user_recommendations_pagination(self, client, mock_api_client, sample_recommendations):
        """Test pagination in user recommendations."""
        mock_api_client.get.return_value = sample_recommendations

        # Test page 2
        result = client.get_user_recommendations(user_id=1, limit=10, skip=10)

        call_params = mock_api_client.get.call_args[1]["params"]
        assert call_params["skip"] == 10
        assert call_params["limit"] == 10

    def test_get_user_recommendations_empty(self, client, mock_api_client):
        """Test getting recommendations when empty."""
        empty_results = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }
        mock_api_client.get.return_value = empty_results

        result = client.get_user_recommendations(user_id=1)

        assert isinstance(result, PaginatedResponse)
        assert result.total == 0
        assert len(result.items) == 0

    def test_get_similar_resources_empty(self, client, mock_api_client):
        """Test getting similar resources when none found."""
        empty_results = {
            "items": [],
            "total": 0,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }
        mock_api_client.get.return_value = empty_results

        result = client.get_similar_resources(resource_id=999)

        assert isinstance(result, PaginatedResponse)
        assert result.total == 0
        assert len(result.items) == 0