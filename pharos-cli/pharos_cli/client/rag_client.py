"""RAG (Retrieval-Augmented Generation) client for Pharos CLI."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from pharos_cli.client.api_client import SyncAPIClient


class RAGResponse(BaseModel):
    """Response from RAG query."""

    answer: str
    sources: List[Dict[str, Any]]
    strategy: str
    confidence: Optional[float] = None


class RAGClient:
    """Client for RAG operations."""

    def __init__(self, api_client: SyncAPIClient):
        """Initialize RAG client.

        Args:
            api_client: The sync API client instance.
        """
        self.api = api_client

    def ask(
        self,
        question: str,
        show_sources: bool = False,
        strategy: str = "hybrid",
        collection_id: Optional[int] = None,
        resource_ids: Optional[List[int]] = None,
        max_sources: int = 5,
    ) -> RAGResponse:
        """Ask a question and get an answer from the knowledge base.

        Args:
            question: The question to ask.
            show_sources: Whether to include source citations.
            strategy: Retrieval strategy (hybrid, graphrag, semantic).
            collection_id: Limit search to a specific collection.
            resource_ids: Limit search to specific resources.
            max_sources: Maximum number of sources to return.

        Returns:
            RAGResponse with answer and optional sources.
        """
        payload: Dict[str, Any] = {
            "question": question,
            "strategy": strategy,
            "max_sources": max_sources,
        }

        if show_sources:
            payload["include_sources"] = True

        if collection_id is not None:
            payload["collection_id"] = collection_id

        if resource_ids:
            payload["resource_ids"] = resource_ids

        response = self.api.post("/api/v1/rag/ask", json=payload)

        return RAGResponse(
            answer=response.get("answer", ""),
            sources=response.get("sources", []),
            strategy=response.get("strategy", strategy),
            confidence=response.get("confidence"),
        )

    def stream_ask(
        self,
        question: str,
        show_sources: bool = False,
        strategy: str = "hybrid",
        collection_id: Optional[int] = None,
        resource_ids: Optional[List[int]] = None,
        max_sources: int = 5,
    ):
        """Stream an answer from the knowledge base.

        Args:
            question: The question to ask.
            show_sources: Whether to include source citations.
            strategy: Retrieval strategy (hybrid, graphrag, semantic).
            collection_id: Limit search to a specific collection.
            resource_ids: Limit search to specific resources.
            max_sources: Maximum number of sources to return.

        Yields:
            Chunks of the answer as they are generated.
        """
        import httpx

        payload: Dict[str, Any] = {
            "question": question,
            "strategy": strategy,
            "max_sources": max_sources,
        }

        if show_sources:
            payload["include_sources"] = True

        if collection_id is not None:
            payload["collection_id"] = collection_id

        if resource_ids:
            payload["resource_ids"] = resource_ids

        # Create a streaming request
        with self.api._client.stream(
            method="POST",
            url="/api/v1/rag/ask",
            json=payload,
        ) as response:
            for line in response.iter_lines():
                if line:
                    try:
                        import json as json_module

                        data = json_module.loads(line)
                        yield data.get("chunk", "")
                    except json_module.JSONDecodeError:
                        yield line.decode("utf-8") if isinstance(line, bytes) else line

    def get_available_strategies(self) -> List[str]:
        """Get list of available RAG strategies.

        Returns:
            List of strategy names.
        """
        try:
            response = self.api.get("/api/v1/rag/strategies")
            return response.get("strategies", ["hybrid", "graphrag", "semantic"])
        except Exception:
            # Return defaults if endpoint not available
            return ["hybrid", "graphrag", "semantic"]

    def health_check(self) -> bool:
        """Check if RAG service is available.

        Returns:
            True if RAG service is healthy.
        """
        try:
            response = self.api.get("/api/v1/rag/health")
            return response.get("status", False)
        except Exception:
            return False