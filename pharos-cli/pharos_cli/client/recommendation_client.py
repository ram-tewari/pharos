"""Recommendation client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse, Resource


class RecommendationClient:
    """Client for recommendation operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the recommendation client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def get_user_recommendations(
        self,
        user_id: int,
        limit: int = 10,
        skip: int = 0,
        include_explanation: bool = False,
    ) -> PaginatedResponse:
        """Get recommendations for a user.

        Args:
            user_id: The ID of the user to get recommendations for.
            limit: Maximum number of recommendations to return.
            skip: Number of recommendations to skip (for pagination).
            include_explanation: Whether to include explanation for each recommendation.

        Returns:
            Paginated response containing recommended resources.
        """
        params: Dict[str, Any] = {
            "user_id": user_id,
            "limit": limit,
            "skip": skip,
        }

        if include_explanation:
            params["include_explanation"] = "true"

        response = self.api.get("/api/v1/recommendations", params=params)
        return PaginatedResponse(**response)

    def get_similar_resources(
        self,
        resource_id: int,
        limit: int = 10,
        skip: int = 0,
        include_explanation: bool = False,
    ) -> PaginatedResponse:
        """Get resources similar to the given resource.

        Args:
            resource_id: The ID of the resource to find similar resources for.
            limit: Maximum number of similar resources to return.
            skip: Number of similar resources to skip (for pagination).
            include_explanation: Whether to include explanation for each similarity.

        Returns:
            Paginated response containing similar resources.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "skip": skip,
        }

        if include_explanation:
            params["include_explanation"] = "true"

        response = self.api.get(
            f"/api/v1/resources/{resource_id}/similar",
            params=params,
        )
        return PaginatedResponse(**response)

    def explain_recommendation(
        self,
        resource_id: int,
        user_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get explanation for why a resource is recommended.

        Args:
            resource_id: The ID of the resource to explain.
            user_id: The ID of the user (optional, for personalized explanations).

        Returns:
            Dictionary containing explanation data.
        """
        params: Dict[str, Any] = {}
        if user_id is not None:
            params["user_id"] = user_id

        return self.api.get(
            f"/api/v1/recommendations/explain/{resource_id}",
            params=params,
        )

    def get_trending_resources(
        self,
        limit: int = 10,
        time_range: str = "week",
    ) -> PaginatedResponse:
        """Get trending resources.

        Args:
            limit: Maximum number of trending resources to return.
            time_range: Time range for trending (day, week, month).

        Returns:
            Paginated response containing trending resources.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "time_range": time_range,
        }

        response = self.api.get("/api/v1/recommendations/trending", params=params)
        return PaginatedResponse(**response)

    def get_personalized_feed(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
    ) -> PaginatedResponse:
        """Get a personalized feed of recommendations for a user.

        Args:
            user_id: The ID of the user.
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            Paginated response containing personalized feed items.
        """
        params: Dict[str, Any] = {
            "limit": limit,
            "offset": offset,
        }

        response = self.api.get(
            f"/api/v1/users/{user_id}/feed",
            params=params,
        )
        return PaginatedResponse(**response)