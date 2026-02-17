"""Integration tests for taxonomy commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app


class TestTaxonomyCommands:
    """Test cases for taxonomy commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_taxonomy_client(self):
        """Create a mock taxonomy client."""
        with patch("pharos_cli.commands.taxonomy.get_taxonomy_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_taxonomy_list_categories_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories command."""
        mock_taxonomy_client.list_categories.return_value = {
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

        result = runner.invoke(app, ["taxonomy", "list-categories"])

        assert result.exit_code == 0
        mock_taxonomy_client.list_categories.assert_called_once()

    def test_taxonomy_list_categories_json_format(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories with JSON output."""
        mock_taxonomy_client.list_categories.return_value = {
            "categories": [],
            "total_categories": 0,
        }

        result = runner.invoke(app, ["taxonomy", "list-categories", "--format", "json"])

        assert result.exit_code == 0
        assert "total_categories" in result.stdout

    def test_taxonomy_list_categories_with_parent(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories with parent filter."""
        mock_taxonomy_client.list_categories.return_value = {
            "categories": [],
            "total_categories": 0,
        }

        result = runner.invoke(app, ["taxonomy", "list-categories", "--parent", "cat-1"])

        assert result.exit_code == 0
        call_args = mock_taxonomy_client.list_categories.call_args
        assert call_args[1]["parent_id"] == "cat-1"

    def test_taxonomy_list_categories_invalid_depth(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories with invalid depth."""
        result = runner.invoke(app, ["taxonomy", "list-categories", "--depth", "20"])

        assert result.exit_code != 0
        assert "must be between 1 and 10" in result.stdout

    def test_taxonomy_list_categories_empty(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories when empty."""
        mock_taxonomy_client.list_categories.return_value = {
            "categories": [],
            "total_categories": 0,
        }

        result = runner.invoke(app, ["taxonomy", "list-categories"])

        assert result.exit_code == 0
        assert "No categories found" in result.stdout

    def test_taxonomy_classify_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify command."""
        mock_taxonomy_client.classify_resource.return_value = {
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

        result = runner.invoke(app, ["taxonomy", "classify", "1"])

        assert result.exit_code == 0
        mock_taxonomy_client.classify_resource.assert_called_once_with("1", force=False)
        assert "Machine Learning" in result.stdout

    def test_taxonomy_classify_with_force(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify with force flag."""
        mock_taxonomy_client.classify_resource.return_value = {
            "status": "success",
            "resource_id": "1",
            "categories": [],
        }

        result = runner.invoke(app, ["taxonomy", "classify", "1", "--force"])

        assert result.exit_code == 0
        call_args = mock_taxonomy_client.classify_resource.call_args
        assert call_args[1]["force"] is True

    def test_taxonomy_classify_verbose(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify with verbose output."""
        mock_taxonomy_client.classify_resource.return_value = {
            "status": "success",
            "resource_id": "1",
            "categories": [
                {
                    "category_id": "cat-1",
                    "name": "Machine Learning",
                    "confidence": 0.95,
                    "path": ["Technology", "AI"],
                },
                {
                    "category_id": "cat-2",
                    "name": "Deep Learning",
                    "confidence": 0.80,
                    "path": ["Technology", "AI", "Deep Learning"],
                },
            ],
        }

        result = runner.invoke(app, ["taxonomy", "classify", "1", "--verbose"])

        assert result.exit_code == 0
        assert "All Categories" in result.stdout

    def test_taxonomy_classify_failed(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify when failed."""
        mock_taxonomy_client.classify_resource.return_value = {
            "status": "failed",
            "error": "Model not available",
        }

        result = runner.invoke(app, ["taxonomy", "classify", "1"])

        assert result.exit_code == 0
        assert "failed" in result.stdout.lower()

    def test_taxonomy_classify_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify with API error."""
        mock_taxonomy_client.classify_resource.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "classify", "1"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_taxonomy_train_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy train command."""
        mock_taxonomy_client.train_model.return_value = {
            "status": "completed",
            "message": "Training completed successfully",
            "metrics": {
                "accuracy": 0.92,
                "f1_score": 0.89,
            },
        }

        result = runner.invoke(app, ["taxonomy", "train"])

        assert result.exit_code == 0
        mock_taxonomy_client.train_model.assert_called_once()

    def test_taxonomy_train_with_categories(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy train with specific categories."""
        mock_taxonomy_client.train_model.return_value = {
            "status": "started",
            "message": "Training started",
        }
        mock_taxonomy_client.get_training_status.return_value = {
            "status": "completed",
            "progress": 1.0,
        }

        result = runner.invoke(app, ["taxonomy", "train", "--categories", "cat-1,cat-2"])

        assert result.exit_code == 0
        call_args = mock_taxonomy_client.train_model.call_args
        assert call_args[1]["categories"] == ["cat-1", "cat-2"]

    def test_taxonomy_train_no_wait(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy train with no-wait flag."""
        mock_taxonomy_client.train_model.return_value = {
            "status": "started",
            "message": "Training started",
        }

        result = runner.invoke(app, ["taxonomy", "train", "--no-wait"])

        assert result.exit_code == 0
        assert "started" in result.stdout.lower()

    def test_taxonomy_stats_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy stats command."""
        mock_taxonomy_client.get_stats.return_value = {
            "total_categories": 50,
            "total_resources": 1000,
            "classified_resources": 800,
            "unclassified_resources": 200,
            "classification_rate": 0.80,
            "model_version": "v1.2.0",
            "last_trained": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["taxonomy", "stats"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_stats.assert_called_once()
        assert "50" in result.output or "Taxonomy Statistics" in result.output

    def test_taxonomy_stats_json_format(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy stats with JSON output."""
        mock_taxonomy_client.get_stats.return_value = {
            "total_categories": 50,
            "total_resources": 1000,
        }

        result = runner.invoke(app, ["taxonomy", "stats", "--format", "json"])

        assert result.exit_code == 0
        assert "total_categories" in result.stdout

    def test_taxonomy_category_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy category command."""
        mock_taxonomy_client.get_category.return_value = {
            "id": "cat-1",
            "name": "Machine Learning",
            "description": "ML category",
            "resource_count": 100,
            "depth": 0,
            "parent_id": None,
        }

        result = runner.invoke(app, ["taxonomy", "category", "cat-1"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_category.assert_called_once_with("cat-1")
        assert "Machine Learning" in result.stdout

    def test_taxonomy_category_with_children(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy category with children flag."""
        mock_taxonomy_client.get_category.return_value = {
            "id": "cat-1",
            "name": "Machine Learning",
            "resource_count": 100,
            "children": [
                {"id": "cat-2", "name": "Deep Learning", "resource_count": 50},
            ],
        }

        result = runner.invoke(app, ["taxonomy", "category", "cat-1", "--children"])

        assert result.exit_code == 0
        assert "Child Categories" in result.stdout

    def test_taxonomy_category_with_similar(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy category with similar flag."""
        mock_taxonomy_client.get_category.return_value = {
            "id": "cat-1",
            "name": "Machine Learning",
            "resource_count": 100,
        }
        mock_taxonomy_client.get_similar_categories.return_value = {
            "similar_categories": [
                {"id": "cat-2", "name": "Deep Learning", "similarity": 0.85},
            ],
        }

        result = runner.invoke(app, ["taxonomy", "category", "cat-1", "--similar"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_similar_categories.assert_called_once_with("cat-1", limit=5)

    def test_taxonomy_category_not_found(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy category when not found."""
        mock_taxonomy_client.get_category.return_value = None

        result = runner.invoke(app, ["taxonomy", "category", "nonexistent"])

        assert result.exit_code == 0
        assert "not found" in result.stdout.lower()

    def test_taxonomy_search_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy search command."""
        from pharos_cli.client.models import PaginatedResponse

        mock_taxonomy_client.search_categories.return_value = PaginatedResponse(
            items=[
                {
                    "id": "cat-1",
                    "name": "Machine Learning",
                    "description": "ML techniques",
                    "resource_count": 50,
                },
            ],
            total=1,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["taxonomy", "search", "machine"])

        assert result.exit_code == 0
        mock_taxonomy_client.search_categories.assert_called_once_with(
            query="machine",
            limit=20,
        )

    def test_taxonomy_search_with_limit(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy search with custom limit."""
        from pharos_cli.client.models import PaginatedResponse

        mock_taxonomy_client.search_categories.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=10,
            has_more=False,
        )

        result = runner.invoke(app, ["taxonomy", "search", "test", "--limit", "10"])

        assert result.exit_code == 0
        call_args = mock_taxonomy_client.search_categories.call_args
        assert call_args[1]["limit"] == 10

    def test_taxonomy_search_invalid_limit(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy search with invalid limit."""
        result = runner.invoke(app, ["taxonomy", "search", "test", "--limit", "200"])

        assert result.exit_code != 0
        assert "must be between 1 and 100" in result.stdout

    def test_taxonomy_search_no_results(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy search with no results."""
        from pharos_cli.client.models import PaginatedResponse

        mock_taxonomy_client.search_categories.return_value = PaginatedResponse(
            items=[],
            total=0,
            page=1,
            per_page=20,
            has_more=False,
        )

        result = runner.invoke(app, ["taxonomy", "search", "nonexistent"])

        assert result.exit_code == 0
        assert "No categories found" in result.stdout

    def test_taxonomy_distribution_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy distribution command."""
        mock_taxonomy_client.get_distribution.return_value = {
            "dimension": "category",
            "distribution": [
                {"name": "Machine Learning", "count": 100},
                {"name": "Deep Learning", "count": 75},
            ],
        }

        result = runner.invoke(app, ["taxonomy", "distribution"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_distribution.assert_called_once()

    def test_taxonomy_distribution_invalid_dimension(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy distribution with invalid dimension."""
        result = runner.invoke(app, ["taxonomy", "distribution", "--dimension", "invalid"])

        assert result.exit_code != 0
        assert "Invalid dimension" in result.stdout

    def test_taxonomy_model_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy model command."""
        mock_taxonomy_client.get_model_info.return_value = {
            "version": "v1.2.0",
            "status": "ready",
            "accuracy": 0.92,
            "last_trained": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["taxonomy", "model"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_model_info.assert_called_once()
        assert "v1.2.0" in result.stdout

    def test_taxonomy_health_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy health command."""
        mock_taxonomy_client.get_health.return_value = {
            "status": "healthy",
            "module": "taxonomy",
            "database": True,
            "model_available": True,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["taxonomy", "health"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_health.assert_called_once()
        assert "healthy" in result.stdout.lower()

    def test_taxonomy_health_unhealthy(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy health when unhealthy."""
        mock_taxonomy_client.get_health.return_value = {
            "status": "unhealthy",
            "module": "taxonomy",
            "database": True,
            "model_available": False,
            "timestamp": "2024-01-15T10:30:00Z",
        }

        result = runner.invoke(app, ["taxonomy", "health"])

        assert result.exit_code == 0
        assert "issues" in result.stdout.lower() or "unhealthy" in result.stdout.lower()

    def test_taxonomy_export_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
        tmp_path,
    ) -> None:
        """Test taxonomy export command."""
        mock_taxonomy_client.export_taxonomy.return_value = {
            "format": "json",
            "categories": [
                {"id": "cat-1", "name": "ML", "resource_count": 100},
            ],
        }

        output_file = tmp_path / "taxonomy.json"
        result = runner.invoke(app, ["taxonomy", "export", "--output", str(output_file)])

        assert result.exit_code == 0
        mock_taxonomy_client.export_taxonomy.assert_called_once()
        assert output_file.exists()

    def test_taxonomy_classification_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classification command."""
        mock_taxonomy_client.get_classification.return_value = {
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

        result = runner.invoke(app, ["taxonomy", "classification", "1"])

        assert result.exit_code == 0
        mock_taxonomy_client.get_classification.assert_called_once_with("1")
        assert "Machine Learning" in result.stdout

    def test_taxonomy_classification_not_classified(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classification when not classified."""
        mock_taxonomy_client.get_classification.return_value = {
            "resource_id": "1",
            "categories": [],
            "classified_at": None,
        }

        result = runner.invoke(app, ["taxonomy", "classification", "1"])

        assert result.exit_code == 0
        assert "no classification" in result.stdout.lower()

    def test_taxonomy_remove_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy remove command."""
        mock_taxonomy_client.remove_classification.return_value = {
            "status": "removed",
            "resource_id": "1",
        }

        result = runner.invoke(app, ["taxonomy", "remove", "1"])

        assert result.exit_code == 0
        mock_taxonomy_client.remove_classification.assert_called_once_with("1")
        assert "removed" in result.stdout.lower()

    def test_taxonomy_batch_classify_command(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy batch-classify command."""
        mock_taxonomy_client.classify_resource_batch.return_value = {
            "status": "completed",
            "processed": 3,
            "successful": 3,
            "failed": 0,
        }

        result = runner.invoke(app, ["taxonomy", "batch-classify", "1,2,3"])

        assert result.exit_code == 0
        mock_taxonomy_client.classify_resource_batch.assert_called_once_with(
            resource_ids=["1", "2", "3"],
            force=False,
        )

    def test_taxonomy_batch_classify_with_force(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy batch-classify with force flag."""
        mock_taxonomy_client.classify_resource_batch.return_value = {
            "status": "completed",
            "processed": 2,
            "successful": 2,
            "failed": 0,
        }

        result = runner.invoke(app, ["taxonomy", "batch-classify", "1,2", "--force"])

        assert result.exit_code == 0
        call_args = mock_taxonomy_client.classify_resource_batch.call_args
        assert call_args[1]["force"] is True

    def test_taxonomy_batch_classify_too_many(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy batch-classify with too many IDs."""
        result = runner.invoke(app, ["taxonomy", "batch-classify", "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101"])

        assert result.exit_code != 0
        assert "Maximum 100" in result.stdout

    def test_taxonomy_help(
        self,
        runner: CliRunner,
    ) -> None:
        """Test taxonomy command help."""
        result = runner.invoke(app, ["taxonomy", "--help"])

        assert result.exit_code == 0
        assert "taxonomy" in result.stdout.lower()

    def test_taxonomy_list_categories_subcommand_help(
        self,
        runner: CliRunner,
    ) -> None:
        """Test taxonomy list-categories subcommand help."""
        result = runner.invoke(app, ["taxonomy", "list-categories", "--help"])

        assert result.exit_code == 0
        assert "format" in result.output


class TestTaxonomyCommandsErrorHandling:
    """Error handling tests for taxonomy commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_taxonomy_client(self):
        """Create a mock taxonomy client."""
        with patch("pharos_cli.commands.taxonomy.get_taxonomy_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_taxonomy_list_categories_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy list-categories with API error."""
        mock_taxonomy_client.list_categories.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "list-categories"])

        assert result.exit_code != 0
        assert "Error" in result.output

    def test_taxonomy_classify_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classify with API error."""
        mock_taxonomy_client.classify_resource.side_effect = Exception("Network error")

        result = runner.invoke(app, ["taxonomy", "classify", "1"])

        assert result.exit_code != 0

    def test_taxonomy_train_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy train with API error."""
        mock_taxonomy_client.train_model.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "train"])

        assert result.exit_code != 0

    def test_taxonomy_stats_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy stats with API error."""
        mock_taxonomy_client.get_stats.side_effect = Exception("Timeout")

        result = runner.invoke(app, ["taxonomy", "stats"])

        assert result.exit_code != 0

    def test_taxonomy_category_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy category with API error."""
        mock_taxonomy_client.get_category.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "category", "cat-1"])

        assert result.exit_code != 0

    def test_taxonomy_search_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy search with API error."""
        mock_taxonomy_client.search_categories.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "search", "test"])

        assert result.exit_code != 0

    def test_taxonomy_distribution_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy distribution with API error."""
        mock_taxonomy_client.get_distribution.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "distribution"])

        assert result.exit_code != 0

    def test_taxonomy_model_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy model with API error."""
        mock_taxonomy_client.get_model_info.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "model"])

        assert result.exit_code != 0

    def test_taxonomy_health_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy health with API error."""
        mock_taxonomy_client.get_health.side_effect = Exception("Connection error")

        result = runner.invoke(app, ["taxonomy", "health"])

        assert result.exit_code != 0

    def test_taxonomy_export_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy export with API error."""
        mock_taxonomy_client.export_taxonomy.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "export"])

        assert result.exit_code != 0

    def test_taxonomy_classification_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy classification with API error."""
        mock_taxonomy_client.get_classification.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "classification", "1"])

        assert result.exit_code != 0

    def test_taxonomy_remove_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy remove with API error."""
        mock_taxonomy_client.remove_classification.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "remove", "1"])

        assert result.exit_code != 0

    def test_taxonomy_batch_classify_api_error(
        self,
        runner: CliRunner,
        mock_taxonomy_client,
    ) -> None:
        """Test taxonomy batch-classify with API error."""
        mock_taxonomy_client.classify_resource_batch.side_effect = Exception("API error")

        result = runner.invoke(app, ["taxonomy", "batch-classify", "1,2,3"])

        assert result.exit_code != 0