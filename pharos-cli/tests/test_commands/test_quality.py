"""Integration tests for quality commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app


class TestQualityCommands:
    """Test cases for quality commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_quality_client(self):
        """Create a mock quality client."""
        with patch("pharos_cli.commands.quality.get_quality_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_quality_score_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality score command."""
        mock_quality_client.get_quality_score.return_value = {
            "resource_id": "1",
            "quality_overall": 0.85,
            "quality_dimensions": {
                "accuracy": 0.90,
                "completeness": 0.80,
                "consistency": 0.85,
                "timeliness": 0.75,
                "relevance": 0.95,
            },
            "is_quality_outlier": False,
            "needs_quality_review": False,
            "quality_last_computed": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["quality", "score", "1"])

        assert result.exit_code == 0
        mock_quality_client.get_quality_score.assert_called_once_with("1")
        assert "85" in result.stdout or "0.85" in result.stdout

    def test_quality_score_verbose(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality score command with verbose output."""
        mock_quality_client.get_quality_score.return_value = {
            "resource_id": "1",
            "quality_overall": 0.75,
            "quality_dimensions": {
                "accuracy": 0.80,
                "completeness": 0.70,
                "consistency": 0.75,
                "timeliness": 0.65,
                "relevance": 0.85,
            },
            "is_quality_outlier": False,
            "needs_quality_review": False,
            "quality_last_computed": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["quality", "score", "1", "--verbose"])

        assert result.exit_code == 0
        assert "Dimension Breakdown" in result.stdout

    def test_quality_score_low_score(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality score with low score (should show red)."""
        mock_quality_client.get_quality_score.return_value = {
            "resource_id": "1",
            "quality_overall": 0.35,
            "quality_dimensions": {
                "accuracy": 0.40,
                "completeness": 0.30,
                "consistency": 0.35,
                "timeliness": 0.25,
                "relevance": 0.45,
            },
            "is_quality_outlier": True,
            "needs_quality_review": True,
            "quality_last_computed": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["quality", "score", "1"])

        assert result.exit_code == 0
        assert "outlier" in result.stdout.lower() or "review" in result.stdout.lower()

    def test_quality_score_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality score with API error."""
        mock_quality_client.get_quality_score.side_effect = Exception("API error")

        result = runner.invoke(app, ["quality", "score", "1"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_quality_outliers_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers command."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_outliers.return_value = PaginatedResponse(
            items=[
                {
                    "resource_id": "1",
                    "title": "Test Resource 1",
                    "quality_overall": 0.30,
                    "outlier_score": 0.85,
                    "outlier_reasons": ["low_accuracy"],
                    "needs_quality_review": True,
                }
            ],
            total=1,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["quality", "outliers"])

        assert result.exit_code == 0
        mock_quality_client.get_outliers.assert_called_once()

    def test_quality_outliers_json_format(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers with JSON output."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_outliers.return_value = PaginatedResponse(
            items=[
                {
                    "resource_id": "1",
                    "title": "Test Resource",
                    "quality_overall": 0.30,
                    "outlier_score": 0.85,
                }
            ],
            total=1,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["quality", "outliers", "--format", "json"])

        assert result.exit_code == 0
        assert "resource_id" in result.stdout

    def test_quality_outliers_empty(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers when none exist."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_outliers.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["quality", "outliers"])

        assert result.exit_code == 0
        assert "No quality outliers found" in result.stdout

    def test_quality_outliers_with_filters(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers with filters."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_outliers.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=50,
            has_more=False,
        )

        result = runner.invoke(app, [
            "quality", "outliers",
            "--page", "2",
            "--limit", "50",
            "--min-score", "0.5",
        ])

        assert result.exit_code == 0
        call_args = mock_quality_client.get_outliers.call_args
        assert call_args[1]["page"] == 2
        assert call_args[1]["limit"] == 50
        assert call_args[1]["min_outlier_score"] == 0.5

    def test_quality_outliers_invalid_limit(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers with invalid limit."""
        result = runner.invoke(app, ["quality", "outliers", "--limit", "200"])

        assert result.exit_code != 0
        assert "must be between 1 and 100" in result.stdout

    def test_quality_recompute_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality recompute command."""
        mock_quality_client.recompute_quality.return_value = {
            "status": "accepted",
            "message": "Quality computation queued for 1 resource(s)",
        }

        result = runner.invoke(app, ["quality", "recompute", "1"])

        assert result.exit_code == 0
        mock_quality_client.recompute_quality.assert_called_once_with(resource_id="1")
        assert "queued" in result.stdout.lower() or "completed" in result.stdout.lower()

    def test_quality_recompute_async(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality recompute with async flag."""
        mock_quality_client.recompute_quality.return_value = {
            "status": "completed",
            "message": "Quality computation completed for 1 resource(s)",
        }

        result = runner.invoke(app, ["quality", "recompute", "1", "--async"])

        assert result.exit_code == 0

    def test_quality_recompute_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality recompute with API error."""
        mock_quality_client.recompute_quality.side_effect = Exception("API error")

        result = runner.invoke(app, ["quality", "recompute", "1"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_quality_report_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality report command."""
        mock_quality_client.get_collection_quality_report.return_value = {
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
            ],
            "outliers": [],
        }

        result = runner.invoke(app, ["quality", "report", "1"])

        assert result.exit_code == 0
        mock_quality_client.get_collection_quality_report.assert_called_once_with("1")
        assert "Quality Report" in result.stdout

    def test_quality_report_to_file(
        self,
        runner: CliRunner,
        mock_quality_client,
        tmp_path,
    ) -> None:
        """Test quality report output to file."""
        mock_quality_client.get_collection_quality_report.return_value = {
            "collection_id": "1",
            "summary": {"total_resources": 10},
        }

        output_file = tmp_path / "report.json"
        result = runner.invoke(app, ["quality", "report", "1", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

    def test_quality_distribution_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality distribution command."""
        mock_quality_client.get_distribution.return_value = {
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

        result = runner.invoke(app, ["quality", "distribution"])

        assert result.exit_code == 0
        mock_quality_client.get_distribution.assert_called_once()
        assert "Histogram" in result.stdout

    def test_quality_distribution_dimension(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality distribution with specific dimension."""
        mock_quality_client.get_distribution.return_value = {
            "dimension": "accuracy",
            "bins": 10,
            "distribution": [],
            "statistics": {"mean": 0.75, "median": 0.78, "std_dev": 0.12},
        }

        result = runner.invoke(app, ["quality", "distribution", "--dimension", "accuracy"])

        assert result.exit_code == 0
        call_args = mock_quality_client.get_distribution.call_args
        assert call_args[1]["dimension"] == "accuracy"

    def test_quality_distribution_invalid_dimension(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality distribution with invalid dimension."""
        result = runner.invoke(app, ["quality", "distribution", "--dimension", "invalid"])

        assert result.exit_code != 0
        assert "Invalid dimension" in result.stdout

    def test_quality_dimensions_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality dimensions command."""
        mock_quality_client.get_dimension_averages.return_value = {
            "dimensions": {
                "accuracy": {"avg": 0.75, "min": 0.50, "max": 0.95},
                "completeness": {"avg": 0.80, "min": 0.60, "max": 1.00},
            },
            "overall": {"avg": 0.78, "min": 0.55, "max": 0.98},
            "total_resources": 100,
        }

        result = runner.invoke(app, ["quality", "dimensions"])

        assert result.exit_code == 0
        mock_quality_client.get_dimension_averages.assert_called_once()
        assert "Dimension Breakdown" in result.stdout

    def test_quality_trends_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality trends command."""
        mock_quality_client.get_trends.return_value = {
            "dimension": "overall",
            "granularity": "weekly",
            "data_points": [
                {"period": "2024-W01", "avg_quality": 0.70, "resource_count": 50},
                {"period": "2024-W02", "avg_quality": 0.72, "resource_count": 55},
            ],
        }

        result = runner.invoke(app, ["quality", "trends"])

        assert result.exit_code == 0
        mock_quality_client.get_trends.assert_called_once()

    def test_quality_trends_with_dates(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality trends with date range."""
        mock_quality_client.get_trends.return_value = {
            "dimension": "overall",
            "granularity": "daily",
            "data_points": [],
        }

        result = runner.invoke(app, [
            "quality", "trends",
            "--start-date", "2024-01-01",
            "--end-date", "2024-01-31",
        ])

        assert result.exit_code == 0
        call_args = mock_quality_client.get_trends.call_args
        assert call_args[1]["start_date"] == "2024-01-01"
        assert call_args[1]["end_date"] == "2024-01-31"

    def test_quality_review_queue_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality review queue command."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_review_queue.return_value = PaginatedResponse(
            items=[
                {
                    "resource_id": "1",
                    "title": "Test Resource",
                    "quality_overall": 0.40,
                    "outlier_score": 0.90,
                    "quality_last_computed": "2024-01-15T10:30:00Z",
                }
            ],
            total=1,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["quality", "review-queue"])

        assert result.exit_code == 0
        mock_quality_client.get_review_queue.assert_called_once()

    def test_quality_review_queue_empty(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality review queue when empty."""
        from pharos_cli.client.models import PaginatedResponse

        mock_quality_client.get_review_queue.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["quality", "review-queue"])

        assert result.exit_code == 0
        assert "No resources need quality review" in result.stdout

    def test_quality_health_command(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality health command."""
        mock_quality_client.get_health.return_value = {
            "status": "healthy",
            "module": "quality",
            "database": True,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["quality", "health"])

        assert result.exit_code == 0
        mock_quality_client.get_health.assert_called_once()
        assert "healthy" in result.stdout.lower()

    def test_quality_health_unhealthy(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality health when unhealthy."""
        mock_quality_client.get_health.return_value = {
            "status": "unhealthy",
            "module": "quality",
            "database": False,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["quality", "health"])

        assert result.exit_code == 0
        assert "issues" in result.stdout.lower() or "unhealthy" in result.stdout.lower()

    def test_quality_help(
        self,
        runner: CliRunner,
    ) -> None:
        """Test quality command help."""
        result = runner.invoke(app, ["quality", "--help"])

        assert result.exit_code == 0
        assert "quality" in result.stdout.lower()

    def test_quality_subcommand_help(
        self,
        runner: CliRunner,
    ) -> None:
        """Test quality subcommand help."""
        result = runner.invoke(app, ["quality", "score", "--help"])

        assert result.exit_code == 0
        assert "resource" in result.stdout.lower()


class TestQualityCommandsErrorHandling:
    """Error handling tests for quality commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_quality_client(self):
        """Create a mock quality client."""
        with patch("pharos_cli.commands.quality.get_quality_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_quality_score_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality score with API error."""
        mock_quality_client.get_quality_score.side_effect = Exception("Network error")

        result = runner.invoke(app, ["quality", "score", "1"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_quality_outliers_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality outliers with API error."""
        mock_quality_client.get_outliers.side_effect = Exception("Timeout")

        result = runner.invoke(app, ["quality", "outliers"])

        assert result.exit_code != 0

    def test_quality_recompute_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality recompute with API error."""
        mock_quality_client.recompute_quality.side_effect = Exception("API error")

        result = runner.invoke(app, ["quality", "recompute", "1"])

        assert result.exit_code != 0

    def test_quality_report_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality report with API error."""
        mock_quality_client.get_collection_quality_report.side_effect = Exception("Not found")

        result = runner.invoke(app, ["quality", "report", "1"])

        assert result.exit_code != 0

    def test_quality_distribution_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality distribution with API error."""
        mock_quality_client.get_distribution.side_effect = Exception("API error")

        result = runner.invoke(app, ["quality", "distribution"])

        assert result.exit_code != 0

    def test_quality_trends_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality trends with API error."""
        mock_quality_client.get_trends.side_effect = Exception("Timeout")

        result = runner.invoke(app, ["quality", "trends"])

        assert result.exit_code != 0

    def test_quality_review_queue_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality review queue with API error."""
        mock_quality_client.get_review_queue.side_effect = Exception("API error")

        result = runner.invoke(app, ["quality", "review-queue"])

        assert result.exit_code != 0

    def test_quality_health_api_error(
        self,
        runner: CliRunner,
        mock_quality_client,
    ) -> None:
        """Test quality health with API error."""
        mock_quality_client.get_health.side_effect = Exception("Connection error")

        result = runner.invoke(app, ["quality", "health"])

        assert result.exit_code != 0