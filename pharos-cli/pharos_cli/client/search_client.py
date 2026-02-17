"""Search client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse, SearchResult


class SearchClient:
    """Client for search operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the search client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def search(
        self,
        query: str,
        search_type: str = "keyword",
        weight: Optional[float] = None,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        min_quality: Optional[float] = None,
        max_quality: Optional[float] = None,
        tags: Optional[List[str]] = None,
        collection_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedResponse:
        """Search for resources.

        Args:
            query: The search query.
            search_type: Type of search (keyword, semantic, hybrid).
            weight: Weight for hybrid search (0.0-1.0, where 1.0 is fully semantic).
            resource_type: Filter by resource type (code, paper, documentation, etc.).
            language: Filter by programming language or natural language.
            min_quality: Minimum quality score filter (0.0-1.0).
            max_quality: Maximum quality score filter (0.0-1.0).
            tags: Filter by tags (list of tag names).
            collection_id: Filter by collection ID.
            skip: Number of results to skip (for pagination).
            limit: Maximum number of results to return.

        Returns:
            Paginated response containing search results.
        """
        params: Dict[str, Any] = {
            "query": query,
            "type": search_type,
            "skip": skip,
            "limit": limit,
        }

        if weight is not None:
            params["weight"] = weight
        if resource_type is not None:
            params["resource_type"] = resource_type
        if language is not None:
            params["language"] = language
        if min_quality is not None:
            params["min_quality"] = min_quality
        if max_quality is not None:
            params["max_quality"] = max_quality
        if tags is not None:
            params["tags"] = ",".join(tags)
        if collection_id is not None:
            params["collection_id"] = collection_id

        response = self.api.get("/api/v1/search", params=params)
        return PaginatedResponse(**response)

    def semantic_search(
        self,
        query: str,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        min_quality: Optional[float] = None,
        max_quality: Optional[float] = None,
        tags: Optional[List[str]] = None,
        collection_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedResponse:
        """Perform semantic search.

        Args:
            query: The search query.
            resource_type: Filter by resource type.
            language: Filter by language.
            min_quality: Minimum quality score filter.
            max_quality: Maximum quality score filter.
            tags: Filter by tags.
            collection_id: Filter by collection ID.
            skip: Number of results to skip.
            limit: Maximum number of results to return.

        Returns:
            Paginated response containing search results.
        """
        return self.search(
            query=query,
            search_type="semantic",
            resource_type=resource_type,
            language=language,
            min_quality=min_quality,
            max_quality=max_quality,
            tags=tags,
            collection_id=collection_id,
            skip=skip,
            limit=limit,
        )

    def hybrid_search(
        self,
        query: str,
        weight: float = 0.5,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        min_quality: Optional[float] = None,
        max_quality: Optional[float] = None,
        tags: Optional[List[str]] = None,
        collection_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedResponse:
        """Perform hybrid search combining keyword and semantic search.

        Args:
            query: The search query.
            weight: Weight for hybrid search (0.0-1.0, where 1.0 is fully semantic).
            resource_type: Filter by resource type.
            language: Filter by language.
            min_quality: Minimum quality score filter.
            max_quality: Maximum quality score filter.
            tags: Filter by tags.
            collection_id: Filter by collection ID.
            skip: Number of results to skip.
            limit: Maximum number of results to return.

        Returns:
            Paginated response containing search results.
        """
        return self.search(
            query=query,
            search_type="hybrid",
            weight=weight,
            resource_type=resource_type,
            language=language,
            min_quality=min_quality,
            max_quality=max_quality,
            tags=tags,
            collection_id=collection_id,
            skip=skip,
            limit=limit,
        )

    def keyword_search(
        self,
        query: str,
        resource_type: Optional[str] = None,
        language: Optional[str] = None,
        min_quality: Optional[float] = None,
        max_quality: Optional[float] = None,
        tags: Optional[List[str]] = None,
        collection_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> PaginatedResponse:
        """Perform keyword search.

        Args:
            query: The search query.
            resource_type: Filter by resource type.
            language: Filter by language.
            min_quality: Minimum quality score filter.
            max_quality: Maximum quality score filter.
            tags: Filter by tags.
            collection_id: Filter by collection ID.
            skip: Number of results to skip.
            limit: Maximum number of results to return.

        Returns:
            Paginated response containing search results.
        """
        return self.search(
            query=query,
            search_type="keyword",
            resource_type=resource_type,
            language=language,
            min_quality=min_quality,
            max_quality=max_quality,
            tags=tags,
            collection_id=collection_id,
            skip=skip,
            limit=limit,
        )