"""API client module for Pharos CLI."""

from pharos_cli.client.api_client import APIClient, SyncAPIClient
from pharos_cli.client.exceptions import (
    PharosError,
    APIError,
    NetworkError,
    ConfigError,
    AuthenticationError,
    ResourceNotFoundError,
    CollectionNotFoundError,
    PermissionError,
    AnnotationNotFoundError,
)
from pharos_cli.client.models import APIResponse, PaginatedResponse
from pharos_cli.client.resource_client import ResourceClient
from pharos_cli.client.search_client import SearchClient
from pharos_cli.client.rag_client import RAGClient, RAGResponse
from pharos_cli.client.recommendation_client import RecommendationClient
from pharos_cli.client.graph_client import GraphClient
from pharos_cli.client.annotation_client import AnnotationClient
from pharos_cli.client.quality_client import QualityClient
from pharos_cli.client.taxonomy_client import TaxonomyClient
from pharos_cli.client.code_client import CodeClient
from pharos_cli.client.system_client import SystemClient

__all__ = [
    "APIClient",
    "SyncAPIClient",
    "PharosError",
    "APIError",
    "NetworkError",
    "ConfigError",
    "AuthenticationError",
    "ResourceNotFoundError",
    "CollectionNotFoundError",
    "PermissionError",
    "AnnotationNotFoundError",
    "APIResponse",
    "PaginatedResponse",
    "ResourceClient",
    "SearchClient",
    "RAGClient",
    "RAGResponse",
    "RecommendationClient",
    "GraphClient",
    "AnnotationClient",
    "QualityClient",
    "TaxonomyClient",
    "CodeClient",
    "SystemClient",
]