"""Collection client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse, Collection, Resource


class CollectionClient:
    """Client for collection operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the collection client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def create(
        self,
        name: str,
        description: Optional[str] = None,
        is_public: bool = False,
    ) -> Dict[str, Any]:
        """Create a new collection.

        Args:
            name: The name of the collection.
            description: Optional description for the collection.
            is_public: Whether the collection is public.

        Returns:
            The created collection data.
        """
        payload: Dict[str, Any] = {"name": name}
        if description is not None:
            payload["description"] = description
        if is_public:
            payload["is_public"] = is_public

        return self.api.post("/api/v1/collections", json=payload)

    def list(
        self,
        skip: int = 0,
        limit: int = 100,
        query: Optional[str] = None,
    ) -> PaginatedResponse:
        """List collections with optional filters.

        Args:
            skip: Number of collections to skip (for pagination).
            limit: Maximum number of collections to return.
            query: Search query for collection name/description.

        Returns:
            Paginated response containing collections.
        """
        params: Dict[str, Any] = {"skip": skip, "limit": limit}

        if query is not None:
            params["query"] = query

        response = self.api.get("/api/v1/collections", params=params)
        return PaginatedResponse(**response)

    def get(self, collection_id: int) -> Collection:
        """Get a collection by ID.

        Args:
            collection_id: The ID of the collection to retrieve.

        Returns:
            The collection data as a Collection model.

        Raises:
            CollectionNotFoundError: If the collection with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            data = self.api.get(f"/api/v1/collections/{collection_id}")
            return Collection(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import CollectionNotFoundError
                raise CollectionNotFoundError(
                    f"Collection with ID {collection_id} not found"
                ) from e
            raise

    def get_contents(
        self,
        collection_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedResponse:
        """Get resources in a collection.

        Args:
            collection_id: The ID of the collection.
            skip: Number of resources to skip (for pagination).
            limit: Maximum number of resources to return.

        Returns:
            Paginated response containing resources in the collection.
        """
        params: Dict[str, Any] = {"skip": skip, "limit": limit}
        response = self.api.get(
            f"/api/v1/collections/{collection_id}/resources",
            params=params
        )
        return PaginatedResponse(**response)

    def update(
        self,
        collection_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        is_public: Optional[bool] = None,
    ) -> Collection:
        """Update a collection.

        Args:
            collection_id: The ID of the collection to update.
            name: New name (optional).
            description: New description (optional).
            is_public: New visibility (optional).

        Returns:
            The updated collection as a Collection model.

        Raises:
            CollectionNotFoundError: If the collection with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        updates: Dict[str, Any] = {}
        if name is not None:
            updates["name"] = name
        if description is not None:
            updates["description"] = description
        if is_public is not None:
            updates["is_public"] = is_public

        try:
            data = self.api.put(
                f"/api/v1/collections/{collection_id}",
                json=updates
            )
            return Collection(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import CollectionNotFoundError
                raise CollectionNotFoundError(
                    f"Collection with ID {collection_id} not found"
                ) from e
            raise

    def delete(self, collection_id: int) -> Dict[str, Any]:
        """Delete a collection.

        Args:
            collection_id: The ID of the collection to delete.

        Returns:
            The response data containing deletion confirmation.

        Raises:
            CollectionNotFoundError: If the collection with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            return self.api.delete(f"/api/v1/collections/{collection_id}")
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import CollectionNotFoundError
                raise CollectionNotFoundError(
                    f"Collection with ID {collection_id} not found"
                ) from e
            raise

    def add_resource(
        self,
        collection_id: int,
        resource_id: int,
    ) -> Dict[str, Any]:
        """Add a resource to a collection.

        Args:
            collection_id: The ID of the collection.
            resource_id: The ID of the resource to add.

        Returns:
            The response data.
        """
        return self.api.post(
            f"/api/v1/collections/{collection_id}/resources",
            json={"resource_id": resource_id},
        )

    def remove_resource(
        self,
        collection_id: int,
        resource_id: int,
    ) -> Dict[str, Any]:
        """Remove a resource from a collection.

        Args:
            collection_id: The ID of the collection.
            resource_id: The ID of the resource to remove.

        Returns:
            The response data.
        """
        return self.api.delete(
            f"/api/v1/collections/{collection_id}/resources/{resource_id}",
        )

    def export(
        self,
        collection_id: int,
        format: str = "json",
    ) -> Dict[str, Any]:
        """Export a collection.

        Args:
            collection_id: The ID of the collection to export.
            format: Export format (json, csv, zip).

        Returns:
            The export data or download URL.
        """
        return self.api.get(
            f"/api/v1/collections/{collection_id}/export",
            params={"format": format},
        )

    def get_stats(self, collection_id: int) -> Dict[str, Any]:
        """Get statistics for a collection.

        Args:
            collection_id: The ID of the collection.

        Returns:
            Collection statistics.
        """
        return self.api.get(f"/api/v1/collections/{collection_id}/stats")