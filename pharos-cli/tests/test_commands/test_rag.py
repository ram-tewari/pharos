"""Integration tests for RAG commands."""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from pathlib import Path
import sys
from typer.testing import CliRunner

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from pharos_cli.cli import app
from pharos_cli.client.rag_client import RAGClient, RAGResponse


class TestRAGCommands:
    """Test cases for RAG CLI commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    @pytest.fixture
    def mock_rag_response(self):
        """Create a mock RAG response."""
        return RAGResponse(
            answer="Gradient descent is an optimization algorithm used to minimize loss functions.",
            sources=[
                {"id": 1, "title": "Deep Learning Book", "score": 0.95, "resource_type": "paper"},
                {"id": 2, "title": "ML Tutorial", "score": 0.88, "resource_type": "code"},
            ],
            strategy="hybrid",
            confidence=0.92,
        )

    def _create_mock_client(self, mock_rag_response):
        """Create a properly configured mock RAG client."""
        client = MagicMock()
        client.ask.return_value = mock_rag_response
        client.health_check.return_value = True
        client.stream_ask.return_value = iter([
            "Gradient ",
            "descent ",
            "is ",
            "an ",
            "optimization ",
            "algorithm."
        ])
        client.get_available_strategies.return_value = ["hybrid", "graphrag", "semantic"]
        return client

    def test_ask_basic(self, runner, mock_rag_response):
        """Test basic ask command."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "What is gradient descent?"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Gradient descent" in result.stdout
            mock_client.ask.assert_called_once()
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["question"] == "What is gradient descent?"
            assert call_kwargs["strategy"] == "hybrid"
            assert call_kwargs["show_sources"] is False

    def test_ask_with_sources(self, runner, mock_rag_response):
        """Test ask command with --show-sources flag."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "What is ML?", "--show-sources"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Sources" in result.stdout or "Deep Learning Book" in result.stdout
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["show_sources"] is True

    def test_ask_with_strategy(self, runner, mock_rag_response):
        """Test ask command with --strategy option."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "What is AI?", "--strategy", "graphrag"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["strategy"] == "graphrag"

    def test_ask_invalid_strategy(self, runner):
        """Test ask command with invalid strategy."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--strategy", "invalid"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Invalid strategy" in result.stdout or "invalid" in result.stdout

    def test_ask_with_collection(self, runner, mock_rag_response):
        """Test ask command with --collection option."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--collection", "5"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["collection_id"] == 5

    def test_ask_with_resources(self, runner, mock_rag_response):
        """Test ask command with --resources option."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--resources", "1,2,3"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["resource_ids"] == [1, 2, 3]

    def test_ask_with_invalid_resources(self, runner):
        """Test ask command with invalid resource IDs."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--resources", "a,b,c"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Invalid resource IDs" in result.stdout

    def test_ask_with_max_sources(self, runner, mock_rag_response):
        """Test ask command with --max-sources option."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--max-sources", "10"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["max_sources"] == 10

    def test_ask_with_output(self, runner, mock_rag_response, tmp_path):
        """Test ask command with --output option."""
        output_file = tmp_path / "answer.md"
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--output", str(output_file)])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert output_file.exists()
            content = output_file.read_text()
            assert "Gradient descent" in content

    def test_ask_with_json_format(self, runner, mock_rag_response):
        """Test ask command with --format json."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--format", "json"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            import json
            data = json.loads(result.stdout)
            assert "answer" in data
            assert data["answer"] == mock_rag_response.answer

    def test_ask_with_text_format(self, runner, mock_rag_response):
        """Test ask command with --format text."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question", "--format", "text"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert mock_rag_response.answer in result.stdout

    def test_ask_confidence_display(self, runner, mock_rag_response):
        """Test that confidence is displayed."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "0.92" in result.stdout or "Confidence" in result.stdout

    def test_ask_health_warning(self, runner, mock_rag_response):
        """Test that health warning is shown when service is unhealthy."""
        mock_client = self._create_mock_client(mock_rag_response)
        mock_client.health_check.return_value = False
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Warning" in result.stdout or "RAG service" in result.stdout

    def test_ask_error_handling(self, runner):
        """Test error handling in ask command."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True
        mock_client.ask.side_effect = Exception("API error")
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test question"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Error" in result.stdout or "API error" in result.stdout

    def test_stream_ask(self, runner, mock_rag_response):
        """Test stream ask command."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "stream", "What is gradient descent?"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Gradient descent" in result.stdout
            mock_client.stream_ask.assert_called_once()

    def test_list_sources(self, runner, mock_rag_response):
        """Test list sources command."""
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "sources", "What is ML?"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Deep Learning Book" in result.stdout or "ML Tutorial" in result.stdout
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["show_sources"] is True

    def test_list_sources_with_output(self, runner, mock_rag_response, tmp_path):
        """Test list sources command with --output."""
        output_file = tmp_path / "sources.json"
        mock_client = self._create_mock_client(mock_rag_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "sources", "Test", "--output", str(output_file), "--format", "json"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert output_file.exists()

    def test_list_sources_empty(self, runner):
        """Test list sources command with no sources found."""
        empty_response = RAGResponse(
            answer="No answer needed",
            sources=[],
            strategy="hybrid",
        )
        mock_client = MagicMock()
        mock_client.ask.return_value = empty_response
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "sources", "Very specific niche topic"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "No relevant sources" in result.stdout or "No sources" in result.stdout

    def test_list_strategies(self, runner):
        """Test list strategies command."""
        mock_client = MagicMock()
        mock_client.get_available_strategies.return_value = ["hybrid", "graphrag", "semantic", "parent-child"]
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "strategies"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "hybrid" in result.stdout
            assert "graphrag" in result.stdout
            assert "semantic" in result.stdout

    def test_list_strategies_fallback(self, runner):
        """Test list strategies command with fallback."""
        mock_client = MagicMock()
        mock_client.get_available_strategies.side_effect = Exception("API error")
        mock_client.get_available_strategies.return_value = ["hybrid", "graphrag", "semantic"]
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "strategies"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "hybrid" in result.stdout

    def test_rag_health_healthy(self, runner):
        """Test RAG health command when healthy."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "health"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "healthy" in result.stdout.lower() or "✓" in result.stdout

    def test_rag_health_unhealthy(self, runner):
        """Test RAG health command when unhealthy."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = False
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "health"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "not available" in result.stdout.lower() or "✗" in result.stdout

    def test_rag_health_error(self, runner):
        """Test RAG health command with error."""
        mock_client = MagicMock()
        mock_client.health_check.side_effect = Exception("Connection error")
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "health"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "Error" in result.stdout


class TestRAGCommandEdgeCases:
    """Edge case tests for RAG commands."""

    @pytest.fixture
    def runner(self):
        """Create CLI runner."""
        return CliRunner()

    def _create_mock_client(self, response=None):
        """Create a properly configured mock RAG client."""
        client = MagicMock()
        if response is not None:
            client.ask.return_value = response
        client.health_check.return_value = True
        client.stream_ask.return_value = iter(["Chunk1 ", "Chunk2 ", "Chunk3"])
        return client

    def test_ask_empty_question(self, runner):
        """Test ask with empty question."""
        empty_response = RAGResponse(
            answer="",
            sources=[],
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(empty_response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", ""])

            # Should still work, just with empty question
            mock_client.ask.assert_called_once()

    def test_ask_very_long_question(self, runner):
        """Test ask with very long question."""
        long_question = " ".join(["test"] * 1000)
        response = RAGResponse(
            answer="Short answer.",
            sources=[],
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", long_question])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["question"] == long_question

    def test_ask_with_special_characters(self, runner):
        """Test ask with special characters in question."""
        special_question = "What is the meaning of life? 🤔"
        response = RAGResponse(
            answer="42",
            sources=[],
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", special_question])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"

    def test_ask_with_unicode_in_answer(self, runner):
        """Test ask with unicode in answer."""
        response = RAGResponse(
            answer="Answer with unicode: 你好世界 🌍",
            sources=[],
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "你好世界" in result.stdout

    def test_ask_with_code_in_answer(self, runner):
        """Test ask with code blocks in answer."""
        response = RAGResponse(
            answer="Here is Python code:\n```python\nprint('hello')\n```",
            sources=[],
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Show me code"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "print('hello')" in result.stdout

    def test_ask_with_many_sources(self, runner):
        """Test ask with many sources."""
        sources = [{"id": i, "title": f"Source {i}", "score": 0.9} for i in range(10)]
        response = RAGResponse(
            answer="Answer with many sources.",
            sources=sources,
            strategy="hybrid",
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test", "--show-sources"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"

    def test_ask_with_no_confidence(self, runner):
        """Test ask when confidence is None."""
        response = RAGResponse(
            answer="Answer without confidence.",
            sources=[],
            strategy="hybrid",
            confidence=None,
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test"])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            # Should not crash when confidence is None

    def test_ask_invalid_max_sources(self, runner):
        """Test ask with invalid --max-sources."""
        mock_client = self._create_mock_client()
        mock_client.health_check.return_value = True
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, ["ask", "Test", "--max-sources", "100"])

            assert result.exit_code != 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            assert "max-sources" in result.stdout.lower() or "between" in result.stdout

    def test_ask_with_all_options(self, runner):
        """Test ask with all options specified."""
        response = RAGResponse(
            answer="Complete answer.",
            sources=[{"id": 1, "title": "Source"}],
            strategy="graphrag",
            confidence=0.88,
        )
        mock_client = self._create_mock_client(response)
        with patch("pharos_cli.commands.rag.get_rag_client", return_value=mock_client):
            result = runner.invoke(app, [
                "ask",
                "Complex question",
                "--show-sources",
                "--strategy", "graphrag",
                "--collection", "10",
                "--resources", "1,2,3",
                "--max-sources", "8"
            ])

            assert result.exit_code == 0, f"Exit code: {result.exit_code}, Output: {result.stdout}"
            call_kwargs = mock_client.ask.call_args[1]
            assert call_kwargs["question"] == "Complex question"
            assert call_kwargs["show_sources"] is True
            assert call_kwargs["strategy"] == "graphrag"
            assert call_kwargs["collection_id"] == 10
            assert call_kwargs["resource_ids"] == [1, 2, 3]
            assert call_kwargs["max_sources"] == 8