"""Unit tests for RAGClient."""

import pytest
from unittest.mock import MagicMock, patch
from typing import Generator
import sys
from pathlib import Path

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pharos_cli.client.rag_client import RAGClient, RAGResponse
from pharos_cli.client.api_client import SyncAPIClient


class TestRAGClient:
    """Test cases for RAGClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        client = MagicMock(spec=SyncAPIClient)
        return client

    @pytest.fixture
    def rag_client(self, mock_api_client: MagicMock) -> RAGClient:
        """Create a RAGClient with mock API client."""
        return RAGClient(mock_api_client)

    def test_ask_basic(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test basic ask question."""
        mock_api_client.post.return_value = {
            "answer": "Gradient descent is an optimization algorithm.",
            "sources": [
                {"id": 1, "title": "ML Paper", "score": 0.92},
            ],
            "strategy": "hybrid",
            "confidence": 0.85,
        }

        result = rag_client.ask(question="What is gradient descent?")

        mock_api_client.post.assert_called_once()
        call_args = mock_api_client.post.call_args
        assert call_args[0][0] == "/api/v1/rag/ask"
        payload = call_args[1]["json"]
        assert payload["question"] == "What is gradient descent?"
        assert payload["strategy"] == "hybrid"
        assert payload["max_sources"] == 5

        assert result.answer == "Gradient descent is an optimization algorithm."
        assert len(result.sources) == 1
        assert result.sources[0]["title"] == "ML Paper"
        assert result.strategy == "hybrid"
        assert result.confidence == 0.85

    def test_ask_with_sources(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with source citations."""
        mock_api_client.post.return_value = {
            "answer": "Neural networks consist of layers of neurons.",
            "sources": [
                {"id": 1, "title": "Deep Learning Book", "score": 0.95},
                {"id": 2, "title": "Neural Networks Guide", "score": 0.88},
            ],
            "strategy": "graphrag",
            "confidence": 0.92,
        }

        result = rag_client.ask(
            question="Explain neural networks",
            show_sources=True,
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["include_sources"] is True

        assert len(result.sources) == 2
        assert result.confidence == 0.92

    def test_ask_with_custom_strategy(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with custom retrieval strategy."""
        mock_api_client.post.return_value = {
            "answer": "Answer using semantic search.",
            "sources": [],
            "strategy": "semantic",
        }

        result = rag_client.ask(
            question="Test question",
            strategy="semantic",
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["strategy"] == "semantic"

        assert result.strategy == "semantic"

    def test_ask_with_collection_filter(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with collection filter."""
        mock_api_client.post.return_value = {
            "answer": "Answer from collection.",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(
            question="Test question",
            collection_id=5,
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["collection_id"] == 5

    def test_ask_with_resource_ids_filter(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with specific resource IDs."""
        mock_api_client.post.return_value = {
            "answer": "Answer from specific resources.",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(
            question="Test question",
            resource_ids=[1, 2, 3],
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["resource_ids"] == [1, 2, 3]

    def test_ask_with_max_sources(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with custom max sources."""
        mock_api_client.post.return_value = {
            "answer": "Answer with limited sources.",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(
            question="Test question",
            max_sources=10,
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["max_sources"] == 10

    def test_get_available_strategies(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting available strategies."""
        mock_api_client.get.return_value = {
            "strategies": ["hybrid", "graphrag", "semantic", "parent-child"],
        }

        strategies = rag_client.get_available_strategies()

        mock_api_client.get.assert_called_once_with("/api/v1/rag/strategies")
        assert strategies == ["hybrid", "graphrag", "semantic", "parent-child"]

    def test_get_available_strategies_fallback(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting available strategies with fallback on error."""
        mock_api_client.get.side_effect = Exception("API error")

        strategies = rag_client.get_available_strategies()

        # Should return default strategies
        assert strategies == ["hybrid", "graphrag", "semantic"]

    def test_health_check_healthy(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check when service is healthy."""
        mock_api_client.get.return_value = {"status": True}

        result = rag_client.health_check()

        assert result is True

    def test_health_check_unhealthy(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check when service is unhealthy."""
        mock_api_client.get.return_value = {"status": False}

        result = rag_client.health_check()

        assert result is False

    def test_health_check_error(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check with error."""
        mock_api_client.get.side_effect = Exception("Connection error")

        result = rag_client.health_check()

        assert result is False


class TestRAGResponse:
    """Tests for RAGResponse model."""

    def test_rag_response_basic(self) -> None:
        """Test basic RAG response."""
        response = RAGResponse(
            answer="Test answer",
            sources=[],
            strategy="hybrid",
        )

        assert response.answer == "Test answer"
        assert response.sources == []
        assert response.strategy == "hybrid"
        assert response.confidence is None

    def test_rag_response_with_all_fields(self) -> None:
        """Test RAG response with all fields."""
        sources = [
            {"id": 1, "title": "Source 1", "score": 0.9},
            {"id": 2, "title": "Source 2", "score": 0.8},
        ]
        response = RAGResponse(
            answer="Complete answer",
            sources=sources,
            strategy="graphrag",
            confidence=0.95,
        )

        assert response.answer == "Complete answer"
        assert len(response.sources) == 2
        assert response.strategy == "graphrag"
        assert response.confidence == 0.95

    def test_rag_response_empty(self) -> None:
        """Test empty RAG response."""
        response = RAGResponse(
            answer="",
            sources=[],
            strategy="hybrid",
        )

        assert response.answer == ""
        assert response.sources == []


class TestRAGClientEdgeCases:
    """Edge case tests for RAGClient."""

    @pytest.fixture
    def mock_api_client(self) -> MagicMock:
        """Create a mock API client."""
        return MagicMock(spec=SyncAPIClient)

    @pytest.fixture
    def rag_client(self, mock_api_client: MagicMock) -> RAGClient:
        """Create a RAGClient with mock API client."""
        return RAGClient(mock_api_client)

    def test_ask_empty_question(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with empty question."""
        mock_api_client.post.return_value = {
            "answer": "",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question="")

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["question"] == ""

    def test_ask_very_long_question(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with very long question."""
        long_question = " ".join(["test"] * 1000)

        mock_api_client.post.return_value = {
            "answer": "Answer to long question.",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question=long_question)

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["question"] == long_question

    def test_ask_with_special_characters(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with special characters in question."""
        special_question = "What is the meaning of life? 🤔"

        mock_api_client.post.return_value = {
            "answer": "42",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question=special_question)

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]
        assert payload["question"] == special_question

    def test_ask_with_unicode_content(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with unicode content in answer."""
        mock_api_client.post.return_value = {
            "answer": "Answer with unicode: 你好世界 🌍",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question="Test")

        assert "你好世界" in result.answer
        assert "🌍" in result.answer

    def test_ask_with_code_in_answer(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with code blocks in answer."""
        mock_api_client.post.return_value = {
            "answer": "Here is a Python example:\n```python\nprint('hello')\n```",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question="Show me Python code")

        assert "print('hello')" in result.answer
        assert "```python" in result.answer

    def test_ask_with_many_sources(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with many sources."""
        sources = [{"id": i, "title": f"Source {i}", "score": 0.9} for i in range(10)]
        mock_api_client.post.return_value = {
            "answer": "Answer with many sources.",
            "sources": sources,
            "strategy": "hybrid",
        }

        result = rag_client.ask(question="Test", max_sources=10)

        assert len(result.sources) == 10

    def test_ask_with_empty_sources(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with no sources found."""
        mock_api_client.post.return_value = {
            "answer": "I couldn't find relevant information.",
            "sources": [],
            "strategy": "hybrid",
        }

        result = rag_client.ask(question="Very specific niche topic")

        assert len(result.sources) == 0
        assert "couldn't find" in result.answer.lower()

    def test_get_available_strategies_empty_response(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test getting available strategies with empty response."""
        mock_api_client.get.return_value = {}

        strategies = rag_client.get_available_strategies()

        # Should return default strategies
        assert strategies == ["hybrid", "graphrag", "semantic"]

    def test_health_check_connection_error(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test health check with connection error."""
        import httpx

        mock_api_client.get.side_effect = httpx.RequestError("Connection failed")

        result = rag_client.health_check()

        assert result is False

    def test_ask_with_all_options(
        self,
        rag_client: RAGClient,
        mock_api_client: MagicMock,
    ) -> None:
        """Test ask with all options specified."""
        mock_api_client.post.return_value = {
            "answer": "Complete answer",
            "sources": [{"id": 1, "title": "Source"}],
            "strategy": "graphrag",
            "confidence": 0.88,
        }

        result = rag_client.ask(
            question="Complex question",
            show_sources=True,
            strategy="graphrag",
            collection_id=10,
            resource_ids=[1, 2, 3],
            max_sources=8,
        )

        call_args = mock_api_client.post.call_args
        payload = call_args[1]["json"]

        assert payload["question"] == "Complex question"
        assert payload["include_sources"] is True
        assert payload["strategy"] == "graphrag"
        assert payload["collection_id"] == 10
        assert payload["resource_ids"] == [1, 2, 3]
        assert payload["max_sources"] == 8