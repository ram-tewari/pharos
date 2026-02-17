"""Resource client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse, Resource


class ResourceClient:
    """Client for resource operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the resource client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def create(
        self,
        title: str,
        content: Optional[str] = None,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a new resource.

        Args:
            title: The title of the resource.
            content: The content of the resource.
            resource_type: The type of resource (code, paper, documentation, etc.).
            language: The programming language or natural language.
            url: The URL if the resource is from a remote source.
            metadata: Additional metadata for the resource.

        Returns:
            The created resource data.
        """
        payload: Dict[str, Any] = {"title": title}
        if content is not None:
            payload["content"] = content
        if resource_type is not None:
            payload["resource_type"] = resource_type
        if language is not None:
            payload["language"] = language
        if url is not None:
            payload["url"] = url
        if metadata is not None:
            payload["metadata"] = metadata

        return self.api.post("/api/v1/resources", json=payload)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        query: Optional[str] = None,
        min_quality: Optional[float] = None,
        collection_id: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> PaginatedResponse:
        """List resources with optional filters.

        Args:
            skip: Number of resources to skip (for pagination).
            limit: Maximum number of resources to return.
            resource_type: Filter by resource type.
            language: Filter by language.
            query: Search query for title/content.
            min_quality: Minimum quality score filter.
            collection_id: Filter by collection ID.
            tags: Filter by tags (list of tag names).

        Returns:
            Paginated response containing resources.
        """
        params: Dict[str, Any] = {"skip": skip, "limit": limit}

        if resource_type is not None:
            params["resource_type"] = resource_type
        if language is not None:
            params["language"] = language
        if query is not None:
            params["query"] = query
        if min_quality is not None:
            params["min_quality"] = min_quality
        if collection_id is not None:
            params["collection_id"] = collection_id
        if tags is not None:
            params["tags"] = ",".join(tags)

        response = self.api.get("/api/v1/resources", params=params)
        return PaginatedResponse(**response)

    def get(self, resource_id: int) -> Resource:
        """Get a resource by ID.

        Args:
            resource_id: The ID of the resource to retrieve.

        Returns:
            The resource data as a Resource model.

        Raises:
            ResourceNotFoundError: If the resource with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            data = self.api.get(f"/api/v1/resources/{resource_id}")
            return Resource(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import ResourceNotFoundError
                raise ResourceNotFoundError(
                    f"Resource with ID {resource_id} not found"
                ) from e
            raise

    def update(
        self,
        resource_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Resource:
        """Update a resource.

        Args:
            resource_id: The ID of the resource to update.
            title: New title (optional).
            content: New content (optional).
            resource_type: New resource type (optional).
            language: New language (optional).
            metadata: New metadata (optional).

        Returns:
            The updated resource as a Resource model.

        Raises:
            ResourceNotFoundError: If the resource with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        updates: Dict[str, Any] = {}
        if title is not None:
            updates["title"] = title
        if content is not None:
            updates["content"] = content
        if resource_type is not None:
            updates["resource_type"] = resource_type
        if language is not None:
            updates["language"] = language
        if metadata is not None:
            updates["metadata"] = metadata

        try:
            data = self.api.put(f"/api/v1/resources/{resource_id}", json=updates)
            return Resource(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import ResourceNotFoundError
                raise ResourceNotFoundError(
                    f"Resource with ID {resource_id} not found"
                ) from e
            raise

    def delete(self, resource_id: int) -> Dict[str, Any]:
        """Delete a resource.

        Args:
            resource_id: The ID of the resource to delete.

        Returns:
            The response data containing deletion confirmation.

        Raises:
            ResourceNotFoundError: If the resource with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            return self.api.delete(f"/api/v1/resources/{resource_id}")
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import ResourceNotFoundError
                raise ResourceNotFoundError(
                    f"Resource with ID {resource_id} not found"
                ) from e
            raise

    def add_to_collection(
        self,
        resource_id: int,
        collection_id: int,
    ) -> Dict[str, Any]:
        """Add a resource to a collection.

        Args:
            resource_id: The ID of the resource.
            collection_id: The ID of the collection.

        Returns:
            The response data.
        """
        return self.api.post(
            f"/api/v1/collections/{collection_id}/resources",
            json={"resource_id": resource_id},
        )

    def remove_from_collection(
        self,
        resource_id: int,
        collection_id: int,
    ) -> Dict[str, Any]:
        """Remove a resource from a collection.

        Args:
            resource_id: The ID of the resource.
            collection_id: The ID of the collection.

        Returns:
            The response data.
        """
        return self.api.delete(
            f"/api/v1/collections/{collection_id}/resources/{resource_id}",
        )

    def get_quality_score(self, resource_id: int) -> Dict[str, Any]:
        """Get the quality score for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            The quality score data.
        """
        return self.api.get(f"/api/v1/resources/{resource_id}/quality")

    def get_annotations(self, resource_id: int) -> List[Dict[str, Any]]:
        """Get annotations for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            List of annotations.
        """
        response = self.api.get(f"/api/v1/resources/{resource_id}/annotations")
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("items", [])
        return []