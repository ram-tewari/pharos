"""API response models for Pharos CLI."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    """Generic API response wrapper."""

    data: Any
    meta: Optional[Dict[str, Any]] = None


class PaginatedResponse(BaseModel):
    """Paginated API response."""

    items: List[Any] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    per_page: int = 100
    has_more: bool = False


class Resource(BaseModel):
    """Resource model."""

    id: int
    title: str
    content: Optional[str] = None
    resource_type: Optional[str] = None
    language: Optional[str] = None
    url: Optional[str] = None
    quality_score: Optional[float] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Collection(BaseModel):
    """Collection model."""

    id: int
    name: str
    description: Optional[str] = None
    owner_id: Optional[int] = None
    is_public: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    resource_count: int = 0


class Annotation(BaseModel):
    """Annotation model."""

    id: int
    resource_id: int
    text: str
    annotation_type: str = "highlight"
    start_offset: Optional[int] = None
    end_offset: Optional[int] = None
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SearchResult(BaseModel):
    """Search result model."""

    id: int
    title: str
    content: Optional[str] = None
    resource_type: Optional[str] = None
    language: Optional[str] = None
    score: float = 0.0
    highlights: List[str] = Field(default_factory=list)


class GraphNode(BaseModel):
    """Graph node model."""

    id: int
    type: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class GraphEdge(BaseModel):
    """Graph edge model."""

    source: int
    target: int
    relationship: str
    weight: float = 1.0


class GraphStats(BaseModel):
    """Graph statistics model."""

    node_count: int = 0
    edge_count: int = 0
    connected_components: int = 0
    average_degree: float = 0.0


class QualityScore(BaseModel):
    """Quality score model."""

    resource_id: int
    overall_score: float = 0.0
    clarity: float = 0.0
    completeness: float = 0.0
    correctness: float = 0.0
    originality: float = 0.0
    computed_at: Optional[str] = None


class TaxonomyNode(BaseModel):
    """Taxonomy node model."""

    id: int
    name: str
    parent_id: Optional[int] = None
    path: str = ""
    children_count: int = 0
    resource_count: int = 0


class User(BaseModel):
    """User model."""

    id: int
    username: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    created_at: Optional[str] = None


class HealthStatus(BaseModel):
    """Health status model."""

    status: str = "healthy"
    version: Optional[str] = None
    database: str = "unknown"
    cache: str = "unknown"
    details: Dict[str, Any] = Field(default_factory=dict)