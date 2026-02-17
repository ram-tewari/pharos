"""Quality client for Pharos CLI."""

from typing import Any, Dict, List, Optional

from pharos_cli.client.api_client import SyncAPIClient
from pharos_cli.client.models import PaginatedResponse


class QualityClient:
    """Client for quality assessment operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize the quality client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def get_quality_details(self, resource_id: str) -> Dict[str, Any]:
        """Get full quality dimension breakdown for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Quality details including dimension scores and overall score.
        """
        return self.api.get(f"/api/v1/quality/resources/{resource_id}/quality-details")

    def get_quality_score(self, resource_id: str) -> Dict[str, Any]:
        """Get quality score summary for a resource.

        Args:
            resource_id: The ID of the resource.

        Returns:
            Quality score summary with overall and dimension scores.
        """
        details = self.get_quality_details(resource_id)
        return {
            "resource_id": details.get("resource_id"),
            "quality_overall": details.get("quality_overall"),
            "quality_dimensions": details.get("quality_dimensions"),
            "is_quality_outlier": details.get("is_quality_outlier"),
            "needs_quality_review": details.get("needs_quality_review"),
            "quality_last_computed": details.get("quality_last_computed"),
        }

    def get_outliers(
        self,
        page: int = 1,
        limit: int = 50,
        min_outlier_score: Optional[float] = None,
        reason: Optional[str] = None,
    ) -> PaginatedResponse:
        """List detected quality outliers with pagination and filtering.

        Args:
            page: Page number (1-indexed).
            limit: Results per page (1-100).
            min_outlier_score: Minimum outlier score filter.
            reason: Filter by specific outlier reason.

        Returns:
            Paginated response with outliers.
        """
        params: Dict[str, Any] = {
            "page": page,
            "limit": limit,
        }
        if min_outlier_score is not None:
            params["min_outlier_score"] = min_outlier_score
        if reason:
            params["reason"] = reason

        response = self.api.get("/api/v1/quality/quality/outliers", params=params)
        return PaginatedResponse(**response)

    def get_distribution(
        self,
        bins: int = 10,
        dimension: str = "overall",
    ) -> Dict[str, Any]:
        """Get quality score distribution histogram.

        Args:
            bins: Number of histogram bins (5-50).
            dimension: Quality dimension or 'overall'.

        Returns:
            Distribution data with histogram bins and statistics.
        """
        return self.api.get(
            "/api/v1/quality/quality/distribution",
            params={"bins": bins, "dimension": dimension},
        )

    def get_dimension_averages(self) -> Dict[str, Any]:
        """Get average scores per dimension across all resources.

        Returns:
            Dimension statistics including averages, mins, and maxes.
        """
        return self.api.get("/api/v1/quality/quality/dimensions")

    def get_trends(
        self,
        granularity: str = "weekly",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        dimension: str = "overall",
    ) -> Dict[str, Any]:
        """Get quality trends over time.

        Args:
            granularity: Time granularity (daily, weekly, monthly).
            start_date: Start date (YYYY-MM-DD).
            end_date: End date (YYYY-MM-DD).
            dimension: Quality dimension or 'overall'.

        Returns:
            Trend data points over time.
        """
        params: Dict[str, Any] = {
            "granularity": granularity,
            "dimension": dimension,
        }
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date

        return self.api.get("/api/v1/quality/quality/trends", params=params)

    def get_degradation_report(
        self,
        time_window_days: int = 30,
    ) -> Dict[str, Any]:
        """Get quality degradation report for specified time window.

        Args:
            time_window_days: Lookback period in days (1-365).

        Returns:
            Degradation report with degraded resources.
        """
        return self.api.get(
            "/api/v1/quality/quality/degradation",
            params={"time_window_days": time_window_days},
        )

    def get_review_queue(
        self,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "outlier_score",
    ) -> PaginatedResponse:
        """Get resources flagged for quality review with priority ranking.

        Args:
            page: Page number (1-indexed).
            limit: Results per page (1-100).
            sort_by: Sort field (outlier_score, quality_overall, updated_at).

        Returns:
            Paginated response with review queue items.
        """
        params: Dict[str, Any] = {
            "page": page,
            "limit": limit,
            "sort_by": sort_by,
        }

        response = self.api.get("/api/v1/quality/quality/review-queue", params=params)
        return PaginatedResponse(**response)

    def recompute_quality(
        self,
        resource_id: Optional[str] = None,
        resource_ids: Optional[List[str]] = None,
        weights: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Trigger quality recomputation for one or more resources.

        Args:
            resource_id: Single resource ID to recompute.
            resource_ids: List of resource IDs to recompute.
            weights: Optional custom weights for dimensions.

        Returns:
            Status message with computation result.
        """
        json_data: Dict[str, Any] = {}
        if resource_id:
            json_data["resource_id"] = resource_id
        if resource_ids:
            json_data["resource_ids"] = resource_ids
        if weights:
            json_data["weights"] = weights

        return self.api.post("/api/v1/quality/quality/recalculate", json=json_data)

    def get_collection_quality_report(
        self,
        collection_id: str,
    ) -> Dict[str, Any]:
        """Get quality report for a collection.

        Args:
            collection_id: The ID of the collection.

        Returns:
            Collection quality report with statistics and recommendations.
        """
        return self.api.get(f"/api/v1/quality/collections/{collection_id}/quality-report")

    def get_health(self) -> Dict[str, Any]:
        """Health check for Quality module.

        Returns:
            Health status including database connectivity.
        """
        return self.api.get("/api/v1/quality/quality/health")