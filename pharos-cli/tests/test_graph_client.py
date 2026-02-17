"""Unit tests for GraphClient."""

import pytest
from unittest.mock import MagicMock
from typing import Generator

import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.graph_client import GraphClient
from pharos_cli.client.api_client import SyncAPIClient


class TestGraphClient:
    """Test cases for GraphClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def graph_client(self, mock_api_client: MagicMock) -> GraphClient:
        """Create a GraphClient with mock API client."""
        return GraphClient(mock_api_client)

    def test_get_stats(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting graph statistics."""
        mock_api_client.get.return_value = {
            "node_count": 100,
            "edge_count": 500,
            "connected_components": 10,
            "average_degree": 5.0,
            "entity_count": 150,
            "hypothesis_count": 25,
        }

        result = graph_client.get_stats()

        mock_api_client.get.assert_called_once_with("/api/v1/graph/stats")
        assert result["node_count"] == 100
        assert result["edge_count"] == 500
        assert result["connected_components"] == 10
        assert result["average_degree"] == 5.0

    def test_get_neighbors(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting neighbors for a resource."""
        mock_api_client.get.return_value = {
            "nodes": [
                {"id": 1, "title": "Node 1", "type": "paper", "quality_score": 0.85},
                {"id": 2, "title": "Node 2", "type": "code", "quality_score": 0.90},
            ],
            "edges": [
                {"source": 1, "target": 2, "weight": 0.87, "relationship_type": "semantic_similarity"},
            ],
        }

        result = graph_client.get_neighbors(resource_id=1, limit=10)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/resources/1/neighbors",
            params={"limit": 10},
        )
        assert len(result["nodes"]) == 2
        assert len(result["edges"]) == 1

    def test_get_citations(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting citations for a resource."""
        mock_api_client.get.return_value = {
            "resource_id": 1,
            "citations": [
                {"marker": "[1]", "position": 1250, "context": "...as shown in [1]..."},
                {"marker": "[2]", "position": 2500, "context": "...according to [2]..."},
            ],
            "count": 2,
        }

        result = graph_client.get_citations(resource_id=1)

        mock_api_client.get.assert_called_once_with("/api/v1/graph/resources/1/citations")
        assert result["count"] == 2
        assert len(result["citations"]) == 2

    def test_extract_citations(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test extracting citations from a resource."""
        mock_api_client.post.return_value = {
            "status": "success",
            "resource_id": 1,
            "citations": [
                {"marker": "[1]", "position": 100, "context": "...test [1]..."},
            ],
            "count": 1,
        }

        result = graph_client.extract_citations(resource_id=1)

        mock_api_client.post.assert_called_once_with("/api/v1/graph/resources/1/extract-citations")
        assert result["status"] == "success"
        assert result["count"] == 1

    def test_get_overview(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting global overview of connections."""
        mock_api_client.get.return_value = {
            "nodes": [
                {"id": 1, "title": "Overview Node 1"},
                {"id": 2, "title": "Overview Node 2"},
            ],
            "edges": [
                {"source": 1, "target": 2, "weight": 0.95, "relationship_type": "high_similarity"},
            ],
        }

        result = graph_client.get_overview(limit=50, vector_threshold=0.7)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/overview",
            params={"limit": 50, "vector_threshold": 0.7},
        )
        assert len(result["nodes"]) == 2

    def test_get_related(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting related resources using graph embeddings."""
        mock_api_client.get.return_value = {
            "node_id": 1,
            "similar_nodes": [
                {"node_id": 2, "similarity": 0.87, "title": "Similar Node 1", "type": "paper"},
                {"node_id": 3, "similarity": 0.82, "title": "Similar Node 2", "type": "code"},
            ],
            "count": 2,
        }

        result = graph_client.get_related(resource_id=1, limit=10)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/embeddings/1/similar",
            params={"limit": 10},
        )
        assert result["count"] == 2
        assert len(result["similar_nodes"]) == 2

    def test_get_embedding(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting graph embedding for a node."""
        mock_api_client.get.return_value = {
            "node_id": "node-1",
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5],
            "dimensions": 128,
        }

        result = graph_client.get_embedding(node_id="node-1")

        mock_api_client.get.assert_called_once_with("/api/v1/graph/embeddings/node-1")
        assert result["node_id"] == "node-1"
        assert len(result["embedding"]) == 5
        assert result["dimensions"] == 128

    def test_generate_embeddings(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test generating graph embeddings."""
        mock_api_client.post.return_value = {
            "status": "success",
            "embeddings_computed": 1250,
            "dimensions": 128,
            "execution_time": 45.3,
        }

        result = graph_client.generate_embeddings(
            algorithm="node2vec",
            dimensions=128,
            walk_length=80,
            num_walks=10,
            p=1.0,
            q=1.0,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/graph/embeddings/generate",
            params={
                "algorithm": "node2vec",
                "dimensions": 128,
                "walk_length": 80,
                "num_walks": 10,
                "p": 1.0,
                "q": 1.0,
            },
        )
        assert result["status"] == "success"
        assert result["embeddings_computed"] == 1250

    def test_discover_hypotheses(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test discovering hypotheses using ABC pattern."""
        mock_api_client.post.return_value = {
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

        result = graph_client.discover_hypotheses(
            concept_a="machine learning",
            concept_c="drug discovery",
            limit=50,
        )

        mock_api_client.post.assert_called_once_with(
            "/api/v1/graph/discover",
            params={
                "concept_a": "machine learning",
                "concept_c": "drug discovery",
                "limit": 50,
            },
        )
        assert result["concept_a"] == "machine learning"
        assert result["concept_c"] == "drug discovery"
        assert len(result["hypotheses"]) == 1

    def test_discover_hypotheses_with_dates(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test discovering hypotheses with date range."""
        mock_api_client.post.return_value = {
            "concept_a": "AI",
            "concept_c": "healthcare",
            "hypotheses": [],
            "count": 0,
            "execution_time": 2.0,
            "time_slice": {
                "start_date": "2020-01-01",
                "end_date": "2024-12-31",
            },
        }

        result = graph_client.discover_hypotheses(
            concept_a="AI",
            concept_c="healthcare",
            limit=20,
            start_date="2020-01-01",
            end_date="2024-12-31",
        )

        call_args = mock_api_client.post.call_args
        params = call_args[1]["params"]
        assert params["start_date"] == "2020-01-01"
        assert params["end_date"] == "2024-12-31"

    def test_get_contradictions(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting contradictions in the knowledge graph."""
        mock_api_client.get.return_value = {
            "contradictions": [
                {
                    "entity": "Gradient Descent",
                    "type": "contradiction",
                    "supporting_evidence": "Paper A shows GD converges",
                    "contradicting_evidence": "Paper B shows GD diverges",
                }
            ],
            "count": 1,
        }

        result = graph_client.get_contradictions()

        mock_api_client.get.assert_called_once_with("/api/v1/graph/contradictions")
        assert result["count"] == 1
        assert len(result["contradictions"]) == 1

    def test_get_centrality(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting centrality scores."""
        mock_api_client.get.return_value = {
            "scores": [
                {
                    "node": "Node 1",
                    "type": "paper",
                    "degree": 50,
                    "betweenness": 0.15,
                    "pagerank": 0.05,
                },
                {
                    "node": "Node 2",
                    "type": "code",
                    "degree": 35,
                    "betweenness": 0.10,
                    "pagerank": 0.03,
                },
            ],
        }

        result = graph_client.get_centrality(top_n=20)

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/centrality",
            params={"top_n": 20},
        )
        assert len(result["scores"]) == 2

    def test_export_graph(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting graph data."""
        mock_api_client.get.return_value = {
            "nodes": [{"id": 1, "title": "Test"}],
            "edges": [],
            "format": "graphml",
        }

        result = graph_client.export_graph(format="graphml")

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/export",
            params={"format": "graphml"},
        )
        assert result["format"] == "graphml"

    def test_get_entities(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test listing entities in the knowledge graph."""
        mock_api_client.get.return_value = {
            "items": [
                {"id": "e1", "name": "Gradient Descent", "type": "Concept"},
                {"id": "e2", "name": "Neural Networks", "type": "Concept"},
            ],
            "total": 10,
            "page": 1,
            "per_page": 50,
            "has_more": False,
        }

        result = graph_client.get_entities(
            entity_type="Concept",
            name_contains="gradient",
            limit=50,
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/entities",
            params={
                "entity_type": "Concept",
                "name_contains": "gradient",
                "limit": 50,
                "skip": 0,
            },
        )
        assert result.total == 10
        assert len(result.items) == 2

    def test_get_entity_relationships(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting relationships for an entity."""
        mock_api_client.get.return_value = {
            "entity": {"id": "e1", "name": "Gradient Descent", "type": "Concept"},
            "outgoing_relationships": [
                {
                    "id": "r1",
                    "target_entity": {"id": "e2", "name": "Optimization", "type": "Concept"},
                    "relation_type": "EXTENDS",
                    "weight": 0.9,
                }
            ],
            "incoming_relationships": [],
            "counts": {"outgoing": 1, "incoming": 0, "total": 1},
        }

        result = graph_client.get_entity_relationships(
            entity_id="e1",
            relation_type="EXTENDS",
            direction="outgoing",
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/entities/e1/relationships",
            params={"relation_type": "EXTENDS", "direction": "outgoing"},
        )
        assert len(result["outgoing_relationships"]) == 1

    def test_traverse_graph(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test traversing the knowledge graph."""
        mock_api_client.get.return_value = {
            "start_entity": {"id": "e1", "name": "Gradient Descent", "type": "Concept"},
            "entities": [
                {"id": "e2", "name": "SGD", "type": "Method"},
            ],
            "relationships": [
                {
                    "id": "r1",
                    "source_entity_id": "e2",
                    "target_entity_id": "e1",
                    "relation_type": "EXTENDS",
                    "weight": 0.9,
                }
            ],
            "traversal_info": {
                "max_hops": 2,
                "entities_by_hop": {"0": ["e1"], "1": ["e2"]},
                "total_entities": 2,
                "total_relationships": 1,
            },
        }

        result = graph_client.traverse_graph(
            start_entity_id="e1",
            relation_types=["EXTENDS", "SUPPORTS"],
            max_hops=2,
        )

        mock_api_client.get.assert_called_once_with(
            "/api/v1/graph/traverse",
            params={
                "start_entity_id": "e1",
                "relation_types": "EXTENDS,SUPPORTS",
                "max_hops": 2,
            },
        )
        assert result["traversal_info"]["total_entities"] == 2

    def test_get_hypothesis(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting a specific hypothesis."""
        mock_api_client.get.return_value = {
            "id": "h1",
            "hypothesis_type": "abc_pattern",
            "bridging_concept": "Molecular Modeling",
            "plausibility_score": 0.85,
            "path_strength": 0.78,
        }

        result = graph_client.get_hypothesis(hypothesis_id="h1")

        mock_api_client.get.assert_called_once_with("/api/v1/graph/hypotheses/h1")
        assert result["id"] == "h1"
        assert result["plausibility_score"] == 0.85

    def test_extract_entities(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test extracting entities from a chunk."""
        mock_api_client.post.return_value = {
            "status": "success",
            "chunk_id": "chunk-1",
            "entities": [
                {"id": "e1", "name": "Gradient Descent", "type": "Concept"},
            ],
            "relationships": [
                {
                    "id": "r1",
                    "source_entity": "SGD",
                    "target_entity": "Gradient Descent",
                    "relation_type": "EXTENDS",
                    "weight": 0.9,
                }
            ],
            "counts": {"entities": 1, "relationships": 1},
        }

        result = graph_client.extract_entities(chunk_id="chunk-1")

        mock_api_client.post.assert_called_once_with("/api/v1/graph/extract/chunk-1")
        assert result["status"] == "success"
        assert result["counts"]["entities"] == 1


class TestGraphClientEdgeCases:
    """Edge case tests for GraphClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def graph_client(self, mock_api_client: MagicMock) -> GraphClient:
        """Create a GraphClient with mock API client."""
        return GraphClient(mock_api_client)

    def test_get_stats_empty(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting stats for empty graph."""
        mock_api_client.get.return_value = {
            "node_count": 0,
            "edge_count": 0,
            "connected_components": 0,
            "average_degree": 0.0,
        }

        result = graph_client.get_stats()

        assert result["node_count"] == 0
        assert result["edge_count"] == 0

    def test_get_neighbors_limit_boundary(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test neighbors with boundary limit values."""
        mock_api_client.get.return_value = {"nodes": [], "edges": []}

        # Test minimum limit
        graph_client.get_neighbors(resource_id=1, limit=1)
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["limit"] == 1

        # Test maximum limit
        graph_client.get_neighbors(resource_id=1, limit=20)
        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["limit"] == 20

    def test_get_related_empty(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting related when no similar nodes exist."""
        mock_api_client.get.return_value = {
            "node_id": 1,
            "similar_nodes": [],
            "count": 0,
        }

        result = graph_client.get_related(resource_id=1, limit=10)

        assert result["count"] == 0
        assert len(result["similar_nodes"]) == 0

    def test_discover_hypotheses_no_results(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test discovering hypotheses when no results found."""
        mock_api_client.post.return_value = {
            "concept_a": "unrelated A",
            "concept_c": "unrelated C",
            "hypotheses": [],
            "count": 0,
            "execution_time": 1.0,
        }

        result = graph_client.discover_hypotheses(
            concept_a="unrelated A",
            concept_c="unrelated C",
            limit=10,
        )

        assert result["count"] == 0
        assert len(result["hypotheses"]) == 0

    def test_get_contradictions_empty(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting contradictions when none exist."""
        mock_api_client.get.return_value = {
            "contradictions": [],
            "count": 0,
        }

        result = graph_client.get_contradictions()

        assert result["count"] == 0
        assert len(result["contradictions"]) == 0

    def test_export_graph_json_format(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test exporting graph in JSON format."""
        mock_api_client.get.return_value = {
            "nodes": [{"id": 1}],
            "edges": [],
            "format": "json",
        }

        result = graph_client.export_graph(format="json")

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["format"] == "json"

    def test_traverse_graph_single_hop(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test traversing with single hop."""
        mock_api_client.get.return_value = {
            "start_entity": {"id": "e1", "name": "Start"},
            "entities": [],
            "relationships": [],
            "traversal_info": {
                "max_hops": 1,
                "entities_by_hop": {"0": ["e1"]},
                "total_entities": 1,
                "total_relationships": 0,
            },
        }

        result = graph_client.traverse_graph(
            start_entity_id="e1",
            max_hops=1,
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["max_hops"] == 1

    def test_generate_embeddings_deepwalk(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test generating embeddings with deepwalk algorithm."""
        mock_api_client.post.return_value = {
            "status": "success",
            "embeddings_computed": 1000,
            "dimensions": 256,
            "execution_time": 60.0,
        }

        result = graph_client.generate_embeddings(
            algorithm="deepwalk",
            dimensions=256,
        )

        call_args = mock_api_client.post.call_args
        assert call_args[1]["params"]["algorithm"] == "deepwalk"
        assert call_args[1]["params"]["dimensions"] == 256

    def test_get_entities_pagination(
        self,
        graph_client: GraphClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting entities with pagination."""
        mock_api_client.get.return_value = {
            "items": [{"id": "e1"}],
            "total": 100,
            "page": 2,
            "per_page": 10,
            "has_more": True,
        }

        result = graph_client.get_entities(
            limit=10,
            skip=10,  # Page 2
        )

        call_args = mock_api_client.get.call_args
        assert call_args[1]["params"]["limit"] == 10
        assert call_args[1]["params"]["skip"] == 10
        assert result.has_more is True