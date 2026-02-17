"""Taxonomy client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse


class TaxonomyClient:
    """Client for taxonomy and classification operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the taxonomy client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def list_categories(
        self,
        parent_id: Optional[str] = None,
        depth: Optional[int] = None,
        include_counts: bool = True,
    ) -> Dict[str, Any]:
        """List taxonomy categories/nodes.

        Args:
            parent_id: Filter by parent category ID.
            depth: Maximum depth to traverse (1-10).
            include_counts: Include resource counts.

        Returns:
            Taxonomy tree or list of categories.
        """
        params: Dict[str, Any] = {
            "include_counts": include_counts,
        }
        if parent_id:
            params["parent_id"] = parent_id
        if depth is not None:
            params["depth"] = depth

        return self.api.get("/api/v1/taxonomy/categories", params=params)

    def get_category(self, category_id: str) -> Dict[str, Any]:
        """Get details for a specific category.

        Args:
            category_id: The ID of the category.

        Returns:
            Category details including children and resource counts.
        """
        return self.api.get(f"/api/v1/taxonomy/categories/{category_id}")

    def get_stats(self) -> Dict[str, Any]:
        """Get taxonomy statistics.

        Returns:
            Statistics including total categories, resources classified, etc.
        """
        return self.api.get("/api/v1/taxonomy/stats")

    def classify_resource(
        self,
        resource_id: str,
        force: bool = False,
    ) -> Dict[str, Any]:
        """Classify a resource using the taxonomy.

        Args:
            resource_id: The ID of the resource to classify.
            force: Force reclassification even if already classified.

        Returns:
            Classification result with categories and confidence scores.
        """
        params: Dict[str, Any] = {}
        if force:
            params["force"] = force

        return self.api.post(
            f"/api/v1/taxonomy/classify/{resource_id}",
            params=params,
        )

    def classify_resource_batch(
        self,
        resource_ids: List[str],
        force: bool = False,
    ) -> Dict[str, Any]:
        """Classify multiple resources using the taxonomy.

        Args:
            resource_ids: List of resource IDs to classify.
            force: Force reclassification even if already classified.

        Returns:
            Batch classification result with summary.
        """
        json_data: Dict[str, Any] = {
            "resource_ids": resource_ids,
        }
        if force:
            json_data["force"] = force

        return self.api.post(
            "/api/v1/taxonomy/classify/batch",
            json=json_data,
        )

    def get_classification(
        self,
        resource_id: str,
    ) -> Dict[str, Any]:
        """Get current classification for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Current classification with categories and confidence.
        """
        return self.api.get(f"/api/v1/taxonomy/resources/{resource_id}/classification")

    def remove_classification(
        self,
        resource_id: str,
    ) -> Dict[str, Any]:
        """Remove classification from a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Confirmation of removal.
        """
        return self.api.delete(f"/api/v1/taxonomy/resources/{resource_id}/classification")

    def train_model(
        self,
        categories: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Train or retrain the taxonomy classification model.

        Args:
            categories: Optional list of category IDs to train on (None for all).

        Returns:
            Training result with status and metrics.
        """
        json_data: Dict[str, Any] = {}
        if categories:
            json_data["categories"] = categories

        return self.api.post("/api/v1/taxonomy/train", json=json_data)

    def get_training_status(self) -> Dict[str, Any]:
        """Get current training status.

        Returns:
            Training status including progress and ETA.
        """
        return self.api.get("/api/v1/taxonomy/train/status")

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current classification model.

        Returns:
            Model information including version, accuracy, and last trained.
        """
        return self.api.get("/api/v1/taxonomy/model")

    def get_distribution(
        self,
        dimension: str = "category",
    ) -> Dict[str, Any]:
        """Get classification distribution.

        Args:
            dimension: Distribution dimension (category, confidence, depth).

        Returns:
            Distribution data with counts and percentages.
        """
        return self.api.get(
            "/api/v1/taxonomy/distribution",
            params={"dimension": dimension},
        )

    def search_categories(
        self,
        query: str,
        limit: int = 20,
    ) -> PaginatedResponse:
        """Search taxonomy categories by name or description.

        Args:
            query: Search query.
            limit: Maximum results (1-100).

        Returns:
            Paginated response with matching categories.
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        response = self.api.get("/api/v1/taxonomy/search", params=params)
        return PaginatedResponse(**response)

    def get_health(self) -> Dict[str, Any]:
        """Health check for Taxonomy module.

        Returns:
            Health status including database and model availability.
        """
        return self.api.get("/api/v1/taxonomy/health")

    def get_similar_categories(
        self,
        category_id: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get similar/related categories.

        Args:
            category_id: The ID of the category.
            limit: Maximum similar categories to return (1-20).

        Returns:
            Similar categories with similarity scores.
        """
        return self.api.get(
            f"/api/v1/taxonomy/categories/{category_id}/similar",
            params={"limit": limit},
        )

    def export_taxonomy(
        self,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export taxonomy data.

        Args:
            format: Export format (json, csv).

        Returns:
            Exported taxonomy data.
        """
        return self.api.get(
            "/api/v1/taxonomy/export",
            params={"format": format},
        )