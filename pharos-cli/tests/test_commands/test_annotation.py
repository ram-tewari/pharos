"""Integration tests for annotation commands."""

import pytest
import json
from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from typing import Generator
from pathlib import Path

import sys

# Add pharos_cli to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the annotation module to ensure it's loaded
from pharos_cli.commands import annotation as annotation_module


@pytest.fixture
def runner() -> Generator[CliRunner, None, None]:
    """Create a CLI runner for testing commands."""
    yield CliRunner()


class TestAnnotationCreateCommand:
    """Test cases for annotation create command."""

    def test_create_annotation_basic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating an annotation with basic fields."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 1,
                "resource_id": 123,
                "text": "Test annotation",
                "annotation_type": "highlight",
                "tags": ["important"],
                "created_at": "2024-01-01T10:00:00Z",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["create", "123", "--text", "Test annotation", "--tags", "important"],
            )

            assert result.exit_code == 0
            assert "Annotation created successfully" in result.stdout
            assert "ID: 1" in result.stdout
            assert "Resource ID: 123" in result.stdout

    def test_create_annotation_with_offsets(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating an annotation with character offsets."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {
                "id": 2,
                "resource_id": 123,
                "text": "Highlighted text",
                "annotation_type": "highlight",
                "start_offset": 100,
                "end_offset": 150,
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["create", "123", "--text", "Highlighted text", "--start", "100", "--end", "150"],
            )

            assert result.exit_code == 0
            assert "Annotation created successfully" in result.stdout

    def test_create_annotation_missing_text(
        self,
        runner: CliRunner,
    ) -> None:
        """Test creating an annotation without required text."""
        result = runner.invoke(
            annotation_module.annotation_app,
            ["create", "123"],
        )

        # Typer shows help when required options are missing
        assert result.exit_code != 0
        # Check for help text or error message (output goes to stderr for errors)
        output = result.stdout + result.stderr
        assert "Usage:" in output or "Error" in output or "Missing option" in output or "Missing argument" in output


class TestAnnotationListCommand:
    """Test cases for annotation list command."""

    def test_list_annotations_for_resource(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing annotations for a specific resource."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list_for_resource.return_value = [
                {"id": 1, "text": "Note 1", "resource_id": 123},
                {"id": 2, "text": "Note 2", "resource_id": 123},
            ]
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["list", "--resource", "123"],
            )

            assert result.exit_code == 0
            assert "Note 1" in result.stdout
            assert "Note 2" in result.stdout

    def test_list_all_annotations(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing all annotations."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list_all.return_value = type(
                'obj', (object,), {
                    'items': [
                        {"id": 1, "text": "Note 1", "resource_id": 123},
                        {"id": 2, "text": "Note 2", "resource_id": 456},
                    ],
                    'total': 2,
                    'page': 1,
                    'per_page': 25,
                    'has_more': False,
                }
            )()
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["list", "--page", "1", "--per-page", "25"],
            )

            assert result.exit_code == 0
            assert "Note 1" in result.stdout
            assert "Note 2" in result.stdout

    def test_list_annotations_empty(
        self,
        runner: CliRunner,
    ) -> None:
        """Test listing annotations when none exist."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.list_for_resource.return_value = []
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["list", "--resource", "123"],
            )

            assert result.exit_code == 0
            assert "No annotations found" in result.stdout


class TestAnnotationGetCommand:
    """Test cases for annotation get command."""

    def test_get_annotation(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting an annotation by ID."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get.return_value = type(
                'obj', (object,), {
                    'id': 1,
                    'resource_id': 123,
                    'text': 'Test annotation',
                    'annotation_type': 'note',
                    'tags': ['important'],
                    'start_offset': None,
                    'end_offset': None,
                    'created_at': '2024-01-01T10:00:00Z',
                    'updated_at': '2024-01-01T10:00:00Z',
                    'model_dump': lambda: {
                        'id': 1,
                        'resource_id': 123,
                        'text': 'Test annotation',
                        'annotation_type': 'note',
                        'tags': ['important'],
                        'start_offset': None,
                        'end_offset': None,
                        'created_at': '2024-01-01T10:00:00Z',
                        'updated_at': '2024-01-01T10:00:00Z',
                    }
                }
            )()
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["get", "1"],
            )

            assert result.exit_code == 0
            assert "Test annotation" in result.stdout
            assert "Resource ID" in result.stdout and "123" in result.stdout

    def test_get_annotation_not_found(
        self,
        runner: CliRunner,
    ) -> None:
        """Test getting a non-existent annotation."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.get.side_effect = annotation_module.AnnotationNotFoundError("Annotation with ID 999 not found")
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["get", "999"],
            )

            assert result.exit_code != 0
            assert "Error" in result.stdout


class TestAnnotationUpdateCommand:
    """Test cases for annotation update command."""

    def test_update_annotation(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating an annotation."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.update.return_value = type(
                'obj', (object,), {
                    'id': 1,
                    'resource_id': 123,
                    'text': 'Updated annotation',
                    'annotation_type': 'note',
                    'tags': ['important', 'updated'],
                    'model_dump': lambda: {
                        'id': 1,
                        'resource_id': 123,
                        'text': 'Updated annotation',
                        'annotation_type': 'note',
                        'tags': ['important', 'updated'],
                    }
                }
            )()
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["update", "1", "--text", "Updated annotation", "--tags", "important,updated"],
            )

            assert result.exit_code == 0
            assert "Annotation updated successfully" in result.stdout
            assert "Updated annotation" in result.stdout

    def test_update_annotation_no_fields(
        self,
        runner: CliRunner,
    ) -> None:
        """Test updating an annotation without specifying any fields."""
        result = runner.invoke(
            annotation_module.annotation_app,
            ["update", "1"],
        )

        assert result.exit_code != 0
        assert "Error" in result.stdout
        assert "Must specify at least one field" in result.stdout


class TestAnnotationDeleteCommand:
    """Test cases for annotation delete command."""

    def test_delete_annotation_with_confirmation(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting an annotation with confirmation."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            # Mock get for confirmation
            mock_client.get.return_value = type(
                'obj', (object,), {
                    'id': 1,
                    'resource_id': 123,
                    'text': 'Test annotation',
                    'annotation_type': 'note',
                }
            )()
            # Mock delete
            mock_client.delete.return_value = {"success": True}
            mock_get_client.return_value = mock_client

            # Simulate user confirming deletion
            result = runner.invoke(
                annotation_module.annotation_app,
                ["delete", "1"],
                input="y\n",
            )

            assert result.exit_code == 0
            assert "Annotation 1 deleted successfully" in result.stdout

    def test_delete_annotation_force(
        self,
        runner: CliRunner,
    ) -> None:
        """Test deleting an annotation with --force flag."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.delete.return_value = {"success": True}
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["delete", "1", "--force"],
            )

            assert result.exit_code == 0
            assert "Annotation 1 deleted successfully" in result.stdout


class TestAnnotationSearchCommand:
    """Test cases for annotation search command."""

    def test_search_annotations_fulltext(
        self,
        runner: CliRunner,
    ) -> None:
        """Test full-text search for annotations."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.search_fulltext.return_value = {
                "items": [
                    {"id": 1, "text": "Note about machine learning"},
                    {"id": 2, "text": "Another note about AI"},
                ],
                "total": 2,
                "query": "machine learning",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["search", "machine learning", "--type", "fulltext"],
            )

            assert result.exit_code == 0
            # Strip ANSI codes for text comparison
            output = result.stdout
            # Check for key content (without ANSI codes)
            assert "machine learning" in output or "ML" in output.replace("machine learning", "ML")
            # Check for count (may be formatted with ANSI codes)
            assert "2" in output or "annotations" in output.lower()

    def test_search_annotations_semantic(
        self,
        runner: CliRunner,
    ) -> None:
        """Test semantic search for annotations."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.search_semantic.return_value = {
                "items": [
                    {"id": 1, "text": "Note about deep learning", "similarity_score": 0.87},
                ],
                "total": 1,
                "query": "deep learning concepts",
            }
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["search", "deep learning concepts", "--type", "semantic"],
            )

            assert result.exit_code == 0
            assert "deep learning" in result.stdout


class TestAnnotationExportCommand:
    """Test cases for annotation export command."""

    def test_export_annotations_markdown(
        self,
        runner: CliRunner,
    ) -> None:
        """Test exporting annotations to markdown."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.export_markdown.return_value = "# Annotations Export\n\n## Resource 123\n\n### Note 1\nText"
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["export", "--resource", "123", "--format", "markdown"],
            )

            assert result.exit_code == 0
            assert "# Annotations Export" in result.stdout

    def test_export_annotations_json(
        self,
        runner: CliRunner,
    ) -> None:
        """Test exporting annotations to JSON."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.export_json.return_value = [
                {"id": 1, "text": "Note 1", "resource_id": 123},
            ]
            mock_get_client.return_value = mock_client

            result = runner.invoke(
                annotation_module.annotation_app,
                ["export", "--resource", "123", "--format", "json"],
            )

            assert result.exit_code == 0
            # Check for JSON output
            assert '"id": 1' in result.stdout or "id" in result.stdout


class TestAnnotationImportCommand:
    """Test cases for annotation import command."""

    def test_import_annotations_dry_run(
        self,
        runner: CliRunner,
    ) -> None:
        """Test importing annotations in dry-run mode."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_get_client.return_value = mock_client

            # Create a temporary JSON file
            with runner.isolated_filesystem():
                annotations = [
                    {"id": 1, "text": "Note 1", "resource_id": 123},
                    {"id": 2, "text": "Note 2", "resource_id": 123},
                ]
                with open("annotations.json", "w") as f:
                    json.dump(annotations, f)

                result = runner.invoke(
                    annotation_module.annotation_app,
                    ["import", "annotations.json", "--dry-run"],
                )

                assert result.exit_code == 0
                assert "Dry run mode" in result.stdout
                assert "2 annotations would be imported" in result.stdout

    def test_import_annotations(
        self,
        runner: CliRunner,
    ) -> None:
        """Test importing annotations."""
        with patch.object(annotation_module, "get_annotation_client") as mock_get_client:
            mock_client = MagicMock()
            mock_client.create.return_value = {"id": 100, "resource_id": 123, "text": "Note 1"}
            mock_get_client.return_value = mock_client

            # Create a temporary JSON file
            with runner.isolated_filesystem():
                annotations = [
                    {"text": "Note 1", "resource_id": 123},
                    {"text": "Note 2", "resource_id": 123},
                ]
                with open("annotations.json", "w") as f:
                    json.dump(annotations, f)

                result = runner.invoke(
                    annotation_module.annotation_app,
                    ["import", "annotations.json", "--resource", "123"],
                )

                assert result.exit_code == 0
                # Check for key content (output may have ANSI codes)
                output = result.stdout
                assert "2" in output or "annotations" in output.lower()
                assert "Successful" in output or "2" in output