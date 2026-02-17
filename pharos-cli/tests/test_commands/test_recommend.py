"""Tests for recommendation commands."""

import json
import sys
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
import pytest
from pharos_cli.cli import app as main_app


class TestRecommendCommand:
    """Test cases for the recommend command group."""

    @pytest.fixture
    def runner(self):
        """Create a CLI runner for testing."""
        return CliRunner()

    @pytest.fixture
    def mock_recommendation_client(self):
        """Create a mock recommendation client."""
        mock = MagicMock()
        return mock

    @pytest.fixture
    def sample_recommendations(self):
        """Create sample recommendations for testing."""
        return {
            "items": [
                {"id": 1, "title": "Recommended Resource 1", "resource_type": "paper", "language": "en", "score": 0.95},
                {"id": 2, "title": "Recommended Resource 2", "resource_type": "code", "language": "python", "score": 0.87},
                {"id": 3, "title": "Recommended Resource 3", "resource_type": "documentation", "language": "en", "score": 0.82},
            ],
            "total": 3,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }

    def test_recommend_for_user_basic(self, runner, mock_recommendation_client, sample_recommendations):
        """Test basic for-user command."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1"])
        assert result.exit_code == 0
        assert "Recommended Resource 1" in result.stdout
        mock_recommendation_client.get_user_recommendations.assert_called_once()
        call_kwargs = mock_recommendation_client.get_user_recommendations.call_args[1]
        assert call_kwargs["user_id"] == 1
        assert call_kwargs["limit"] == 10

    def test_recommend_for_user_with_limit(self, runner, mock_recommendation_client, sample_recommendations):
        """Test for-user command with --limit option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1", "--limit", "20"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_user_recommendations.call_args[1]
        assert call_kwargs["limit"] == 20

    def test_recommend_for_user_with_pagination(self, runner, mock_recommendation_client, sample_recommendations):
        """Test for-user command with pagination options."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1", "--page", "2", "--limit", "10"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_user_recommendations.call_args[1]
        assert call_kwargs["skip"] == 10
        assert call_kwargs["limit"] == 10

    def test_recommend_for_user_with_explain(self, runner, mock_recommendation_client, sample_recommendations):
        """Test for-user command with --explain flag."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1", "--explain"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_user_recommendations.call_args[1]
        assert call_kwargs["include_explanation"] is True

    def test_recommend_for_user_json_output(self, runner, mock_recommendation_client, sample_recommendations):
        """Test for-user command with JSON output format."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1", "--format", "json"])
        assert result.exit_code == 0

    def test_recommend_for_user_quiet_output(self, runner, mock_recommendation_client, sample_recommendations):
        """Test for-user command with quiet output (IDs only)."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**sample_recommendations)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1", "--format", "quiet"])
        assert result.exit_code == 0
        lines = [line for line in result.stdout.strip().split("\n") if line.strip()]
        assert len(lines) >= 3
        assert "1" in lines[0]
        assert "2" in lines[1]
        assert "3" in lines[2]

    def test_recommend_for_user_empty_results(self, runner, mock_recommendation_client):
        """Test for-user command with no results."""
        from pharos_cli.client.models import PaginatedResponse
        empty_results = {"items": [], "total": 0, "page": 1, "per_page": 10, "has_more": False}
        mock_recommendation_client.get_user_recommendations.return_value = PaginatedResponse(**empty_results)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "999"])
        assert result.exit_code == 0

    def test_recommend_for_user_error_handling(self, runner, mock_recommendation_client):
        """Test for-user command error handling."""
        mock_recommendation_client.get_user_recommendations.side_effect = Exception("API error")
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "for-user", "1"])
        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()


class TestSimilarCommand:
    """Test cases for the similar command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_recommendation_client(self):
        return MagicMock()

    @pytest.fixture
    def sample_similar_resources(self):
        return {
            "items": [
                {"id": 2, "title": "Similar Resource 1", "resource_type": "code", "language": "python", "score": 0.92},
                {"id": 3, "title": "Similar Resource 2", "resource_type": "paper", "language": "en", "score": 0.85},
            ],
            "total": 2,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }

    def test_similar_basic(self, runner, mock_recommendation_client, sample_similar_resources):
        """Test basic similar command."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_similar_resources.return_value = PaginatedResponse(**sample_similar_resources)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "similar", "1"])
        assert result.exit_code == 0
        assert "Similar Resource 1" in result.stdout
        mock_recommendation_client.get_similar_resources.assert_called_once()
        call_kwargs = mock_recommendation_client.get_similar_resources.call_args[1]
        assert call_kwargs["resource_id"] == 1

    def test_similar_with_limit(self, runner, mock_recommendation_client, sample_similar_resources):
        """Test similar command with --limit option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_similar_resources.return_value = PaginatedResponse(**sample_similar_resources)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "similar", "1", "--limit", "20"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_similar_resources.call_args[1]
        assert call_kwargs["limit"] == 20

    def test_similar_with_explain(self, runner, mock_recommendation_client, sample_similar_resources):
        """Test similar command with --explain flag."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_similar_resources.return_value = PaginatedResponse(**sample_similar_resources)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "similar", "1", "--explain"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_similar_resources.call_args[1]
        assert call_kwargs["include_explanation"] is True

    def test_similar_json_output(self, runner, mock_recommendation_client, sample_similar_resources):
        """Test similar command with JSON output format."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_similar_resources.return_value = PaginatedResponse(**sample_similar_resources)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "similar", "1", "--format", "json"])
        assert result.exit_code == 0

    def test_similar_empty_results(self, runner, mock_recommendation_client):
        """Test similar command with no results."""
        from pharos_cli.client.models import PaginatedResponse
        empty_results = {"items": [], "total": 0, "page": 1, "per_page": 10, "has_more": False}
        mock_recommendation_client.get_similar_resources.return_value = PaginatedResponse(**empty_results)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "similar", "999"])
        assert result.exit_code == 0
        assert "No similar" in result.stdout or "0" in result.stdout


class TestExplainCommand:
    """Test cases for the explain command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_recommendation_client(self):
        return MagicMock()

    @pytest.fixture
    def sample_explanation(self):
        return {
            "resource_id": 1,
            "score": 0.95,
            "reasons": ["Similar to your recent reads", "High quality score", "Popular in your field"],
            "factors": {"content_similarity": 0.8, "user_interest_match": 0.9, "quality_score": 0.95},
            "similar_users": 15,
            "related_resources": [{"id": 2, "title": "Related Resource 1"}, {"id": 3, "title": "Related Resource 2"}],
        }

    def test_explain_basic(self, runner, mock_recommendation_client, sample_explanation):
        """Test basic explain command."""
        mock_recommendation_client.explain_recommendation.return_value = sample_explanation
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "explain", "1"])
        assert result.exit_code == 0
        assert "Similar to your recent reads" in result.stdout or "0.95" in result.stdout
        mock_recommendation_client.explain_recommendation.assert_called_once()
        call_kwargs = mock_recommendation_client.explain_recommendation.call_args[1]
        assert call_kwargs["resource_id"] == 1
        assert call_kwargs["user_id"] is None

    def test_explain_with_user(self, runner, mock_recommendation_client, sample_explanation):
        """Test explain command with --user option."""
        mock_recommendation_client.explain_recommendation.return_value = sample_explanation
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "explain", "1", "--user", "1"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.explain_recommendation.call_args[1]
        assert call_kwargs["user_id"] == 1

    def test_explain_json_output(self, runner, mock_recommendation_client, sample_explanation):
        """Test explain command with JSON output format."""
        mock_recommendation_client.explain_recommendation.return_value = sample_explanation
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "explain", "1", "--format", "json"])
        assert result.exit_code == 0
        assert "0.95" in result.stdout or "reasons" in result.stdout

    def test_explain_markdown_output(self, runner, mock_recommendation_client, sample_explanation):
        """Test explain command with markdown output format."""
        mock_recommendation_client.explain_recommendation.return_value = sample_explanation
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "explain", "1", "--format", "markdown"])
        assert result.exit_code == 0
        assert "Recommendation Explanation" in result.stdout or "Reasons" in result.stdout

    def test_explain_error_handling(self, runner, mock_recommendation_client):
        """Test explain command error handling."""
        mock_recommendation_client.explain_recommendation.side_effect = Exception("API error")
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "explain", "1"])
        assert result.exit_code == 1
        assert "Error" in result.stdout or "error" in result.stdout.lower()


class TestTrendingCommand:
    """Test cases for the trending command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_recommendation_client(self):
        return MagicMock()

    @pytest.fixture
    def sample_trending(self):
        return {
            "items": [{"id": 10, "title": "Trending Resource 1", "resource_type": "paper", "score": 0.98},
                      {"id": 11, "title": "Trending Resource 2", "resource_type": "code", "score": 0.95}],
            "total": 2,
            "page": 1,
            "per_page": 10,
            "has_more": False,
        }

    def test_trending_basic(self, runner, mock_recommendation_client, sample_trending):
        """Test basic trending command."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_trending_resources.return_value = PaginatedResponse(**sample_trending)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "trending"])
        assert result.exit_code == 0
        assert "Trending Resource 1" in result.stdout
        mock_recommendation_client.get_trending_resources.assert_called_once()
        call_kwargs = mock_recommendation_client.get_trending_resources.call_args[1]
        assert call_kwargs["limit"] == 10
        assert call_kwargs["time_range"] == "week"

    def test_trending_with_limit(self, runner, mock_recommendation_client, sample_trending):
        """Test trending command with --limit option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_trending_resources.return_value = PaginatedResponse(**sample_trending)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "trending", "--limit", "20"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_trending_resources.call_args[1]
        assert call_kwargs["limit"] == 20

    def test_trending_with_time_range(self, runner, mock_recommendation_client, sample_trending):
        """Test trending command with --time-range option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_trending_resources.return_value = PaginatedResponse(**sample_trending)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "trending", "--time-range", "day"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_trending_resources.call_args[1]
        assert call_kwargs["time_range"] == "day"

    def test_trending_invalid_time_range(self, runner):
        """Test trending command with invalid time range."""
        result = runner.invoke(main_app, ["recommend", "trending", "--time-range", "invalid"])
        assert result.exit_code == 1
        assert "Invalid" in result.stdout or "invalid" in result.stdout.lower()

    def test_trending_json_output(self, runner, mock_recommendation_client, sample_trending):
        """Test trending command with JSON output format."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_trending_resources.return_value = PaginatedResponse(**sample_trending)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "trending", "--format", "json"])
        assert result.exit_code == 0


class TestFeedCommand:
    """Test cases for the feed command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    @pytest.fixture
    def mock_recommendation_client(self):
        return MagicMock()

    @pytest.fixture
    def sample_feed(self):
        return {
            "items": [{"id": 20, "title": "Feed Item 1", "resource_type": "paper", "score": 0.93},
                      {"id": 21, "title": "Feed Item 2", "resource_type": "documentation", "score": 0.88}],
            "total": 2,
            "page": 1,
            "per_page": 20,
            "has_more": False,
        }

    def test_feed_basic(self, runner, mock_recommendation_client, sample_feed):
        """Test basic feed command."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_personalized_feed.return_value = PaginatedResponse(**sample_feed)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "feed", "1"])
        assert result.exit_code == 0
        assert "Feed Item 1" in result.stdout
        mock_recommendation_client.get_personalized_feed.assert_called_once()
        call_kwargs = mock_recommendation_client.get_personalized_feed.call_args[1]
        assert call_kwargs["user_id"] == 1
        assert call_kwargs["limit"] == 20

    def test_feed_with_limit(self, runner, mock_recommendation_client, sample_feed):
        """Test feed command with --limit option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_personalized_feed.return_value = PaginatedResponse(**sample_feed)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "feed", "1", "--limit", "50"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_personalized_feed.call_args[1]
        assert call_kwargs["limit"] == 50

    def test_feed_with_offset(self, runner, mock_recommendation_client, sample_feed):
        """Test feed command with --offset option."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_personalized_feed.return_value = PaginatedResponse(**sample_feed)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "feed", "1", "--offset", "20"])
        assert result.exit_code == 0
        call_kwargs = mock_recommendation_client.get_personalized_feed.call_args[1]
        assert call_kwargs["offset"] == 20

    def test_feed_json_output(self, runner, mock_recommendation_client, sample_feed):
        """Test feed command with JSON output format."""
        from pharos_cli.client.models import PaginatedResponse
        mock_recommendation_client.get_personalized_feed.return_value = PaginatedResponse(**sample_feed)
        with patch("pharos_cli.commands.recommend.get_recommendation_client", return_value=mock_recommendation_client):
            result = runner.invoke(main_app, ["recommend", "feed", "1", "--format", "json"])
        assert result.exit_code == 0


class TestRecommendCommandIntegration:
    """Integration tests for recommend command."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_recommend_help(self, runner):
        """Test recommend help command."""
        result = runner.invoke(main_app, ["recommend", "--help"])
        assert result.exit_code == 0
        assert "recommend" in result.stdout.lower()
        assert "for-user" in result.stdout or "user" in result.stdout.lower()
        assert "similar" in result.stdout
        assert "explain" in result.stdout
        assert "trending" in result.stdout
        assert "feed" in result.stdout

    def test_recommend_for_user_help(self, runner):
        """Test for-user subcommand help."""
        result = runner.invoke(main_app, ["recommend", "for-user", "--help"])
        assert result.exit_code == 0
        assert "User ID" in result.stdout
        assert "--limit" in result.stdout
        assert "--page" in result.stdout

    def test_recommend_similar_help(self, runner):
        """Test similar subcommand help."""
        result = runner.invoke(main_app, ["recommend", "similar", "--help"])
        assert result.exit_code == 0
        assert "Resource ID" in result.stdout
        assert "--limit" in result.stdout

    def test_recommend_explain_help(self, runner):
        """Test explain subcommand help."""
        result = runner.invoke(main_app, ["recommend", "explain", "--help"])
        assert result.exit_code == 0
        assert "Resource ID" in result.stdout
        assert "--user" in result.stdout

    def test_recommend_trending_help(self, runner):
        """Test trending subcommand help."""
        result = runner.invoke(main_app, ["recommend", "trending", "--help"])
        assert result.exit_code == 0
        assert "--limit" in result.stdout
        assert "--time-range" in result.stdout

    def test_recommend_feed_help(self, runner):
        """Test feed subcommand help."""
        result = runner.invoke(main_app, ["recommend", "feed", "--help"])
        assert result.exit_code == 0
        assert "User ID" in result.stdout
        assert "--limit" in result.stdout
        assert "--offset" in result.stdout