"""Annotation client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import Annotation, PaginatedResponse


class AnnotationClient:
    """Client for annotation operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the annotation client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def create(
        self,
        resource_id: int,
        text: str,
        annotation_type: str = "highlight",
        start_offset: Optional[int] = None,
        end_offset: Optional[int] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a new annotation on a resource.

        Args:
            resource_id: The ID of the resource to annotate.
            text: The annotation text (note or highlighted text).
            annotation_type: Type of annotation (highlight, note, tag).
            start_offset: Start character offset in the resource (for highlights).
            end_offset: End character offset in the resource (for highlights).
            tags: List of tags for the annotation.

        Returns:
            The created annotation data.
        """
        payload: Dict[str, Any] = {
            "text": text,
            "annotation_type": annotation_type,
        }
        
        if start_offset is not None:
            payload["start_offset"] = start_offset
        if end_offset is not None:
            payload["end_offset"] = end_offset
        if tags is not None:
            payload["tags"] = tags

        return self.api.post(f"/api/v1/resources/{resource_id}/annotations", json=payload)

    def list_for_resource(
        self,
        resource_id: int,
        include_shared: bool = False,
        tags: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """List all annotations for a specific resource.

        Args:
            resource_id: The ID of the resource.
            include_shared: Include shared annotations from other users.
            tags: Filter by tags.

        Returns:
            List of annotations for the resource.
        """
        params: Dict[str, Any] = {}
        if include_shared:
            params["include_shared"] = "true"
        if tags is not None:
            params["tags"] = ",".join(tags)

        response = self.api.get(f"/api/v1/resources/{resource_id}/annotations", params=params)
        if isinstance(response, list):
            return response
        elif isinstance(response, dict):
            return response.get("items", [])
        return []

    def list_all(
        self,
        limit: int = 50,
        offset: int = 0,
        sort_by: str = "recent",
    ) -> PaginatedResponse:
        """List all annotations for the authenticated user across all resources.

        Args:
            limit: Number of annotations to return (1-100).
            offset: Number of annotations to skip.
            sort_by: Sort order: "recent" or "oldest".

        Returns:
            Paginated response containing annotations.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
            "sort_by": sort_by,
        }

        response = self.api.get("/api/v1/annotations", params=params)
        return PaginatedResponse(**response)

    def get(self, annotation_id: int) -> Annotation:
        """Get a specific annotation by ID.

        Args:
            annotation_id: The ID of the annotation to retrieve.

        Returns:
            The annotation data as an Annotation model.

        Raises:
            AnnotationNotFoundError: If the annotation with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            data = self.api.get(f"/api/v1/annotations/{annotation_id}")
            return Annotation(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import AnnotationNotFoundError
                raise AnnotationNotFoundError(
                    f"Annotation with ID {annotation_id} not found"
                ) from e
            raise

    def update(
        self,
        annotation_id: int,
        text: Optional[str] = None,
        annotation_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> Annotation:
        """Update an existing annotation.

        Args:
            annotation_id: The ID of the annotation to update.
            text: New text for the annotation.
            annotation_type: New annotation type.
            tags: New tags for the annotation.

        Returns:
            The updated annotation as an Annotation model.

        Raises:
            AnnotationNotFoundError: If the annotation with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        updates: Dict[str, Any] = {}
        if text is not None:
            updates["text"] = text
        if annotation_type is not None:
            updates["annotation_type"] = annotation_type
        if tags is not None:
            updates["tags"] = tags

        try:
            data = self.api.put(f"/api/v1/annotations/{annotation_id}", json=updates)
            return Annotation(**data)
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import AnnotationNotFoundError
                raise AnnotationNotFoundError(
                    f"Annotation with ID {annotation_id} not found"
                ) from e
            raise

    def delete(self, annotation_id: int) -> Dict[str, Any]:
        """Delete an annotation.

        Args:
            annotation_id: The ID of the annotation to delete.

        Returns:
            The response data containing deletion confirmation.

        Raises:
            AnnotationNotFoundError: If the annotation with the given ID is not found.
            APIError: If the API request fails for other reasons.
            NetworkError: If there's a network connectivity issue.
        """
        from pharos_cli.client.exceptions import APIError

        try:
            return self.api.delete(f"/api/v1/annotations/{annotation_id}")
        except APIError as e:
            if e.status_code == 404:
                from pharos_cli.client.exceptions import AnnotationNotFoundError
                raise AnnotationNotFoundError(
                    f"Annotation with ID {annotation_id} not found"
                ) from e
            raise

    def search_fulltext(
        self,
        query: str,
        limit: int = 50,
    ) -> Dict[str, Any]:
        """Full-text search across annotation notes and highlighted text.

        Args:
            query: Search query.
            limit: Maximum results (1-100).

        Returns:
            Search results with annotations.
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        return self.api.get("/api/v1/annotations/search/fulltext", params=params)

    def search_semantic(
        self,
        query: str,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Semantic search across annotation notes using embeddings.

        Args:
            query: Semantic search query.
            limit: Maximum results (1-50).

        Returns:
            Search results with annotations and similarity scores.
        """
        params: Dict[str, Any] = {
            "query": query,
            "limit": limit,
        }

        return self.api.get("/api/v1/annotations/search/semantic", params=params)

    def search_tags(
        self,
        tags: List[str],
        match_all: bool = False,
    ) -> Dict[str, Any]:
        """Search annotations by tags.

        Args:
            tags: Tags to search for.
            match_all: Match ALL tags (true) or ANY tag (false).

        Returns:
            Search results with annotations.
        """
        params: Dict[str, Any] = {
            "match_all": "true" if match_all else "false",
        }
        # Add tags as multiple query parameters
        for tag in tags:
            params.setdefault("tags", []).append(tag)

        return self.api.get("/api/v1/annotations/search/tags", params=params)

    def export_markdown(
        self,
        resource_id: Optional[int] = None,
    ) -> str:
        """Export annotations to Markdown format.

        Args:
            resource_id: Optional resource UUID to filter by.

        Returns:
            Markdown-formatted text.
        """
        params: Dict[str, Any] = {}
        if resource_id is not None:
            params["resource_id"] = resource_id

        return self.api.get("/api/v1/annotations/export/markdown", params=params)

    def export_json(
        self,
        resource_id: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Export annotations to JSON format.

        Args:
            resource_id: Optional resource UUID to filter by.

        Returns:
            List of annotations with complete metadata.
        """
        params: Dict[str, Any] = {}
        if resource_id is not None:
            params["resource_id"] = resource_id

        return self.api.get("/api/v1/annotations/export/json", params=params)