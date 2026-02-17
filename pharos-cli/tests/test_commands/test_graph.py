"""Integration tests for graph commands."""

import pytest
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app


class TestGraphCommands:
    """Test cases for graph commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_graph_client(self):
        """Create a mock graph client."""
        with patch("pharos_cli.commands.graph.get_graph_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_graph_stats_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph stats command."""
        mock_graph_client.get_stats.return_value = {
            "node_count": 100,
            "edge_count": 500,
            "connected_components": 10,
            "average_degree": 5.0,
        }

        result = runner.invoke(app, ["graph", "stats"])

        assert result.exit_code == 0
        assert "Graph Statistics" in result.stdout or "100" in result.stdout
        mock_graph_client.get_stats.assert_called_once()

    def test_graph_stats_json_format(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph stats with JSON output."""
        mock_graph_client.get_stats.return_value = {
            "node_count": 100,
            "edge_count": 500,
        }

        result = runner.invoke(app, ["graph", "stats", "--format", "json"])

        assert result.exit_code == 0
        assert "node_count" in result.stdout

    def test_graph_citations_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph citations command."""
        mock_graph_client.get_citations.return_value = {
            "resource_id": 1,
            "citations": [
                {"marker": "[1]", "position": 1250, "context": "...test [1]..."},
            ],
            "count": 1,
        }

        result = runner.invoke(app, ["graph", "citations", "1"])

        assert result.exit_code == 0
        mock_graph_client.get_citations.assert_called_once_with(1)

    def test_graph_citations_empty(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph citations when no citations found."""
        mock_graph_client.get_citations.return_value = {
            "resource_id": 1,
            "citations": [],
            "count": 0,
        }

        result = runner.invoke(app, ["graph", "citations", "1"])

        assert result.exit_code == 0
        assert "No citations found" in result.stdout

    def test_graph_related_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph related command."""
        mock_graph_client.get_related.return_value = {
            "node_id": 1,
            "similar_nodes": [
                {"node_id": 2, "similarity": 0.87, "title": "Similar Node"},
            ],
            "count": 1,
        }

        result = runner.invoke(app, ["graph", "related", "1"])

        assert result.exit_code == 0
        mock_graph_client.get_related.assert_called_once_with(1, limit=10)

    def test_graph_related_with_limit(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph related with custom limit."""
        mock_graph_client.get_related.return_value = {
            "node_id": 1,
            "similar_nodes": [],
            "count": 0,
        }

        result = runner.invoke(app, ["graph", "related", "1", "--limit", "20"])

        assert result.exit_code == 0
        mock_graph_client.get_related.assert_called_once_with(1, limit=20)

    def test_graph_related_invalid_limit(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph related with invalid limit."""
        result = runner.invoke(app, ["graph", "related", "1", "--limit", "200"])

        assert result.exit_code != 0
        assert "must be between 1 and 100" in result.stdout

    def test_graph_neighbors_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph neighbors command."""
        mock_graph_client.get_neighbors.return_value = {
            "nodes": [
                {"id": 1, "title": "Node 1", "type": "paper"},
            ],
            "edges": [],
        }

        result = runner.invoke(app, ["graph", "neighbors", "1"])

        assert result.exit_code == 0
        mock_graph_client.get_neighbors.assert_called_once_with(1, limit=10)

    def test_graph_overview_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph overview command."""
        mock_graph_client.get_overview.return_value = {
            "nodes": [{"id": 1, "title": "Node 1"}],
            "edges": [],
        }

        result = runner.invoke(app, ["graph", "overview"])

        assert result.exit_code == 0
        mock_graph_client.get_overview.assert_called_once_with(limit=50, vector_threshold=0.7)

    def test_graph_overview_custom_params(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph overview with custom parameters."""
        mock_graph_client.get_overview.return_value = {
            "nodes": [],
            "edges": [],
        }

        result = runner.invoke(app, ["graph", "overview", "--limit", "100", "--threshold", "0.8"])

        assert result.exit_code == 0
        mock_graph_client.get_overview.assert_called_once_with(limit=100, vector_threshold=0.8)

    def test_graph_export_command(
        self,
        runner: CliRunner,
        mock_graph_client,
        tmp_path,
    ) -> None:
        """Test graph export command."""
        mock_graph_client.export_graph.return_value = {
            "nodes": [{"id": 1}],
            "edges": [],
            "format": "json",
        }

        output_file = tmp_path / "graph.json"
        result = runner.invoke(app, ["graph", "export", "--format", "json", "--output", str(output_file)])

        assert result.exit_code == 0
        mock_graph_client.export_graph.assert_called_once_with(format="json")
        assert output_file.exists()

    def test_graph_contradictions_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph contradictions command."""
        mock_graph_client.get_contradictions.return_value = {
            "contradictions": [],
            "count": 0,
        }

        result = runner.invoke(app, ["graph", "contradictions"])

        assert result.exit_code == 0
        assert "No contradictions found" in result.stdout

    def test_graph_discover_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph discover command."""
        mock_graph_client.discover_hypotheses.return_value = {
            "concept_a": "machine learning",
            "concept_c": "drug discovery",
            "hypotheses": [
                {
                    "bridging_concept": "molecular modeling",
                    "support_strength": 0.85,
                    "novelty_score": 0.72,
                    "evidence_count": 15,
                }
            ],
            "count": 1,
            "execution_time": 3.5,
        }

        result = runner.invoke(app, ["graph", "discover", "machine learning", "drug discovery"])

        assert result.exit_code == 0
        mock_graph_client.discover_hypotheses.assert_called_once_with(
            concept_a="machine learning",
            concept_c="drug discovery",
            limit=50,
            start_date=None,
            end_date=None,
        )

    def test_graph_discover_with_dates(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph discover with date range."""
        mock_graph_client.discover_hypotheses.return_value = {
            "concept_a": "AI",
            "concept_c": "healthcare",
            "hypotheses": [],
            "count": 0,
            "execution_time": 2.0,
        }

        result = runner.invoke(app, [
            "graph", "discover", "AI", "healthcare",
            "--start-date", "2020-01-01",
            "--end-date", "2024-12-31",
        ])

        assert result.exit_code == 0
        call_args = mock_graph_client.discover_hypotheses.call_args
        assert call_args[1]["start_date"] == "2020-01-01"
        assert call_args[1]["end_date"] == "2024-12-31"

    def test_graph_centrality_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph centrality command."""
        mock_graph_client.get_centrality.return_value = {
            "scores": [
                {
                    "node": "Node 1",
                    "type": "paper",
                    "degree": 50,
                    "betweenness": 0.15,
                    "pagerank": 0.05,
                }
            ],
        }

        result = runner.invoke(app, ["graph", "centrality"])

        assert result.exit_code == 0
        mock_graph_client.get_centrality.assert_called_once_with(top_n=None)

    def test_graph_centrality_top_n(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph centrality with top N."""
        mock_graph_client.get_centrality.return_value = {
            "scores": [],
        }

        result = runner.invoke(app, ["graph", "centrality", "--top", "20"])

        assert result.exit_code == 0
        mock_graph_client.get_centrality.assert_called_once_with(top_n=20)

    def test_graph_entities_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph entities command."""
        mock_graph_client.get_entities.return_value = MagicMock(
            items=[{"id": "e1", "name": "Test", "type": "Concept"}],
            total=1,
            has_more=False,
        )

        result = runner.invoke(app, ["graph", "entities"])

        assert result.exit_code == 0
        mock_graph_client.get_entities.assert_called_once()

    def test_graph_entities_with_filters(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph entities with filters."""
        mock_graph_client.get_entities.return_value = MagicMock(
            items=[],
            total=0,
            has_more=False,
        )

        result = runner.invoke(app, ["graph", "entities", "--type", "Concept", "--name", "test", "--limit", "20"])

        assert result.exit_code == 0
        call_args = mock_graph_client.get_entities.call_args
        assert call_args[1]["entity_type"] == "Concept"
        assert call_args[1]["name_contains"] == "test"
        assert call_args[1]["limit"] == 20

    def test_graph_traverse_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph traverse command."""
        mock_graph_client.traverse_graph.return_value = {
            "start_entity": {"id": "e1", "name": "Start"},
            "entities": [],
            "relationships": [],
            "traversal_info": {
                "total_entities": 1,
                "total_relationships": 0,
            },
        }

        result = runner.invoke(app, ["graph", "traverse", "e1"])

        assert result.exit_code == 0
        mock_graph_client.traverse_graph.assert_called_once_with(
            start_entity_id="e1",
            relation_types=None,
            max_hops=2,
        )

    def test_graph_traverse_with_params(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph traverse with custom parameters."""
        mock_graph_client.traverse_graph.return_value = {
            "start_entity": {"id": "e1"},
            "entities": [],
            "relationships": [],
            "traversal_info": {"total_entities": 1, "total_relationships": 0},
        }

        result = runner.invoke(app, [
            "graph", "traverse", "e1",
            "--relations", "EXTENDS,SUPPORTS",
            "--hops", "3",
        ])

        assert result.exit_code == 0
        call_args = mock_graph_client.traverse_graph.call_args
        assert call_args[1]["relation_types"] == ["EXTENDS", "SUPPORTS"]
        assert call_args[1]["max_hops"] == 3

    def test_graph_embeddings_command(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph embeddings command."""
        mock_graph_client.generate_embeddings.return_value = {
            "status": "success",
            "embeddings_computed": 1000,
            "dimensions": 128,
            "execution_time": 45.0,
        }

        result = runner.invoke(app, ["graph", "embeddings"])

        assert result.exit_code == 0
        mock_graph_client.generate_embeddings.assert_called_once()

    def test_graph_embeddings_custom_params(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph embeddings with custom parameters."""
        mock_graph_client.generate_embeddings.return_value = {
            "status": "success",
            "embeddings_computed": 500,
            "dimensions": 256,
            "execution_time": 60.0,
        }

        result = runner.invoke(app, [
            "graph", "embeddings",
            "--algorithm", "deepwalk",
            "--dimensions", "256",
        ])

        assert result.exit_code == 0
        call_args = mock_graph_client.generate_embeddings.call_args
        assert call_args[1]["algorithm"] == "deepwalk"
        assert call_args[1]["dimensions"] == 256

    def test_graph_help(self, runner: CliRunner) -> None:
        """Test graph command help."""
        result = runner.invoke(app, ["graph", "--help"])

        assert result.exit_code == 0
        assert "Knowledge graph" in result.stdout or "graph" in result.stdout

    def test_graph_subcommand_help(self, runner: CliRunner) -> None:
        """Test graph subcommand help."""
        result = runner.invoke(app, ["graph", "stats", "--help"])

        assert result.exit_code == 0
        assert "format" in result.stdout


class TestGraphCommandsErrorHandling:
    """Error handling tests for graph commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_graph_client(self):
        """Create a mock graph client."""
        with patch("pharos_cli.commands.graph.get_graph_client") as mock:
            client = MagicMock()
            mock.return_value = client
            yield client

    def test_graph_stats_api_error(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph stats with API error."""
        mock_graph_client.get_stats.side_effect = Exception("API error")

        result = runner.invoke(app, ["graph", "stats"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_graph_citations_api_error(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph citations with API error."""
        mock_graph_client.get_citations.side_effect = Exception("Network error")

        result = runner.invoke(app, ["graph", "citations", "1"])

        assert result.exit_code != 0
        assert "Error" in result.stdout

    def test_graph_related_api_error(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph related with API error."""
        mock_graph_client.get_related.side_effect = Exception("API error")

        result = runner.invoke(app, ["graph", "related", "1"])

        assert result.exit_code != 0

    def test_graph_discover_api_error(
        self,
        runner: CliRunner,
        mock_graph_client,
    ) -> None:
        """Test graph discover with API error."""
        mock_graph_client.discover_hypotheses.side_effect = Exception("Timeout")

        result = runner.invoke(app, ["graph", "discover", "A", "C"])

        assert result.exit_code != 0