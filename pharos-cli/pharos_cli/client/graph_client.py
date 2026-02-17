"""Graph client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse


class GraphClient:
    """Client for graph operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the graph client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def get_stats(self) -> Dict[str, Any]:
        """Get graph statistics.

        Returns:
            Graph statistics including node count, edge count, etc.
        """
        return self.api.get("/api/v1/graph/stats")

    def get_neighbors(
        self,
        resource_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get hybrid neighbors for a resource (mind-map view).

        Args:
            resource_id: The ID of the resource.
            limit: Maximum neighbors to return (1-20).

        Returns:
            Knowledge graph with nodes and edges.
        """
        return self.api.get(
            f"/api/v1/graph/resources/{resource_id}/neighbors",
            params={"limit": limit},
        )

    def get_citations(self, resource_id: int) -> Dict[str, Any]:
        """Get citations for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Citations data for the resource.
        """
        return self.api.get(f"/api/v1/graph/resources/{resource_id}/citations")

    def extract_citations(self, resource_id: int) -> Dict[str, Any]:
        """Extract citations from a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Extraction result with citations found.
        """
        return self.api.post(f"/api/v1/graph/resources/{resource_id}/extract-citations")

    def get_overview(
        self,
        limit: int = 50,
        vector_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Get global overview of strongest connections.

        Args:
            limit: Maximum edges to return (1-100).
            vector_threshold: Minimum vector similarity (0.0-1.0).

        Returns:
            Knowledge graph with strongest connections.
        """
        return self.api.get(
            "/api/v1/graph/overview",
            params={"limit": limit, "vector_threshold": vector_threshold},
        )

    def get_related(
        self,
        resource_id: int,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get related resources using graph embeddings.

        Args:
            resource_id: The ID of the resource.
            limit: Maximum similar nodes to return (1-100).

        Returns:
            Similar nodes based on graph embeddings.
        """
        return self.api.get(
            f"/api/v1/graph/embeddings/{resource_id}/similar",
            params={"limit": limit},
        )

    def get_embedding(self, node_id: str) -> Dict[str, Any]:
        """Get graph embedding for a specific node.

        Args:
            node_id: The ID of the node.

        Returns:
            Graph embedding data.
        """
        return self.api.get(f"/api/v1/graph/embeddings/{node_id}")

    def generate_embeddings(
        self,
        algorithm: str = "node2vec",
        dimensions: int = 128,
        walk_length: int = 80,
        num_walks: int = 10,
        p: float = 1.0,
        q: float = 1.0,
    ) -> Dict[str, Any]:
        """Generate graph embeddings.

        Args:
            algorithm: Algorithm name (node2vec or deepwalk).
            dimensions: Embedding dimensionality (32-512).
            walk_length: Length of random walks (10-200).
            num_walks: Number of walks per node (1-100).
            p: Return parameter for Node2Vec (0.1-10.0).
            q: In-out parameter for Node2Vec (0.1-10.0).

        Returns:
            Generation result with statistics.
        """
        return self.api.post(
            "/api/v1/graph/embeddings/generate",
            params={
                "algorithm": algorithm,
                "dimensions": dimensions,
                "walk_length": walk_length,
                "num_walks": num_walks,
                "p": p,
                "q": q,
            },
        )

    def discover_hypotheses(
        self,
        concept_a: str,
        concept_c: str,
        limit: int = 50,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Discover hypotheses using ABC pattern (Literature-Based Discovery).

        Args:
            concept_a: Starting concept.
            concept_c: Target concept.
            limit: Maximum hypotheses (1-100).
            start_date: Start date for time-slicing (ISO format).
            end_date: End date for time-slicing (ISO format).

        Returns:
            Hypotheses ranked by support strength and novelty.
        """
        params: Dict[str, Any] = {
            "concept_a": concept_a,
            "concept_c": concept_c,
            "limit": limit,
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        return self.api.post("/api/v1/graph/discover", params=params)

    def get_contradictions(self) -> Dict[str, Any]:
        """Get detected contradictions in the knowledge graph.

        Returns:
            Contradictions found in the graph.
        """
        return self.api.get("/api/v1/graph/contradictions")

    def get_centrality(
        self,
        top_n: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get centrality scores for nodes in the graph.

        Args:
            top_n: Return only top N nodes by centrality.

        Returns:
            Centrality scores for nodes.
        """
        params: Dict[str, Any] = {}
        if top_n is not None:
            params["top_n"] = top_n

        return self.api.get("/api/v1/graph/centrality", params=params)

    def export_graph(
        self,
        format: str = "graphml",
    ) -> Dict[str, Any]:
        """Export graph data.

        Args:
            format: Export format (graphml, json, csv).

        Returns:
            Exported graph data.
        """
        return self.api.get(
            "/api/v1/graph/export",
            params={"format": format},
        )

    def get_entities(
        self,
        entity_type: Optional[str] = None,
        name_contains: Optional[str] = None,
        limit: int = 50,
        skip: int = 0,
    ) -> PaginatedResponse:
        """List entities in the knowledge graph.

        Args:
            entity_type: Filter by entity type.
            name_contains: Filter by name (partial match).
            limit: Number of results.
            skip: Number of results to skip.

        Returns:
            Paginated response with entities.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "skip": skip,
        }
        if entity_type:
            params["entity_type"] = entity_type
        if name_contains:
            params["name_contains"] = name_contains

        response = self.api.get("/api/v1/graph/entities", params=params)
        return PaginatedResponse(**response)

    def get_entity_relationships(
        self,
        entity_id: str,
        relation_type: Optional[str] = None,
        direction: str = "both",
    ) -> Dict[str, Any]:
        """Get relationships for an entity.

        Args:
            entity_id: The ID of the entity.
            relation_type: Filter by relation type.
            direction: Filter by direction (outgoing, incoming, both).

        Returns:
            Relationships for the entity.
        """
        params: Dict[str, Any] = {"direction": direction}
        if relation_type:
            params["relation_type"] = relation_type

        return self.api.get(
            f"/api/v1/graph/entities/{entity_id}/relationships",
            params=params,
        )

    def traverse_graph(
        self,
        start_entity_id: str,
        relation_types: Optional[List[str]] = None,
        max_hops: int = 2,
    ) -> Dict[str, Any]:
        """Traverse the knowledge graph.

        Args:
            start_entity_id: Starting entity ID.
            relation_types: Relation types to follow.
            max_hops: Maximum traversal depth.

        Returns:
            Traversal result with entities and relationships.
        """
        params: Dict[str, Any] = {
            "start_entity_id": start_entity_id,
            "max_hops": max_hops,
        }
        if relation_types:
            params["relation_types"] = ",".join(relation_types)

        return self.api.get("/api/v1/graph/traverse", params=params)

    def get_hypothesis(self, hypothesis_id: str) -> Dict[str, Any]:
        """Get details for a specific hypothesis.

        Args:
            hypothesis_id: The ID of the hypothesis.

        Returns:
            Hypothesis details.
        """
        return self.api.get(f"/api/v1/graph/hypotheses/{hypothesis_id}")

    def extract_entities(self, chunk_id: str) -> Dict[str, Any]:
        """Extract entities and relationships from a document chunk.

        Args:
            chunk_id: The ID of the chunk.

        Returns:
            Extraction result with entities and relationships.
        """
        return self.api.post(f"/api/v1/graph/extract/{chunk_id}")