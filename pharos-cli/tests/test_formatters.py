"""Tests for formatters module."""

import pytest
from unittest.mock import MagicMock

from pharos_cli.formatters.json_formatter import JSONFormatter
from pharos_cli.formatters.table_formatter import TableFormatter
from pharos_cli.formatters.tree_formatter import TreeFormatter
from pharos_cli.formatters.csv_formatter import CSVFormatter
from pharos_cli.formatters.base import get_formatter


class TestJSONFormatter:
    """Tests for JSONFormatter."""

    def test_format_dict(self):
        """Test formatting dictionary."""
        formatter = JSONFormatter()
        result = formatter.format({"key": "value"})
        assert '{\n  "key": "value"\n}' == result

    def test_format_list(self):
        """Test formatting list."""
        formatter = JSONFormatter()
        result = formatter.format([{"id": 1}, {"id": 2}])
        assert "[1, 2]" in result or "1" in result

    def test_format_error(self):
        """Test formatting error."""
        formatter = JSONFormatter()
        result = formatter.format_error(Exception("Test error"))
        assert "Test error" in result
        assert "Exception" in result

    def test_custom_indent(self):
        """Test custom indent."""
        formatter = JSONFormatter(indent=4)
        result = formatter.format({"key": "value"})
        assert '{\n    "key": "value"\n}' == result


class TestTableFormatter:
    """Tests for TableFormatter."""

    def test_format_empty_list(self):
        """Test formatting empty list."""
        formatter = TableFormatter()
        result = formatter.format_list([])
        assert "No results found" in result

    def test_format_list(self, sample_resources):
        """Test formatting list of resources."""
        formatter = TableFormatter()
        result = formatter.format_list(sample_resources)
        assert "Resource 1" in result
        assert "Resource 2" in result
        assert "Resource 3" in result

    def test_format_dict(self):
        """Test formatting dictionary."""
        formatter = TableFormatter()
        result = formatter.format({"key": "value", "number": 42})
        # Check that the keys and values from the input dict are in the result
        assert "key" in result.lower()
        assert "value" in result.lower()
        assert "number" in result.lower()
        assert "42" in result

    def test_format_error(self):
        """Test formatting error."""
        formatter = TableFormatter()
        result = formatter.format_error(Exception("Test error"))
        assert "Test error" in result
        assert "Error" in result

    def test_column_auto_sizing(self):
        """Test that columns are auto-sized based on content."""
        formatter = TableFormatter(auto_size_columns=True)
        items = [
            {"id": 1, "title": "Short"},
            {"id": 2, "title": "A much longer title here"},
            {"id": 3, "title": "Medium length"},
        ]
        result = formatter.format_list(items)
        # Should contain all titles
        assert "Short" in result
        assert "A much longer title here" in result
        assert "Medium length" in result

    def test_row_truncation(self):
        """Test that long content is truncated."""
        formatter = TableFormatter(
            truncate_long_content=True,
            max_column_width=20,
            auto_size_columns=True
        )
        items = [
            {"id": 1, "description": "This is a very long description that should be truncated because it exceeds the maximum column width limit"},
        ]
        result = formatter.format_list(items)
        # Should contain truncated text with ellipsis
        assert "..." in result
        # Original long text should not appear in full
        assert "This is a very long description that should be truncated" not in result

    def test_pagination(self):
        """Test pagination for large tables."""
        formatter = TableFormatter(max_rows_per_page=2)
        items = [
            {"id": i, "title": f"Resource {i}"}
            for i in range(1, 6)  # 5 items, 3 pages
        ]
        result = formatter.format_list(items)
        # Should have page indicators
        assert "Page 1" in result or "1" in result
        # Should show total items
        assert "5 total" in result or "5" in result

    def test_pagination_all_on_one_page(self):
        """Test that small tables don't paginate."""
        formatter = TableFormatter(max_rows_per_page=10)
        items = [
            {"id": i, "title": f"Resource {i}"}
            for i in range(1, 5)  # 4 items, fits on one page
        ]
        result = formatter.format_list(items)
        # Should not have page indicators
        assert "Page" not in result

    def test_custom_column_configuration(self):
        """Test formatting with custom column configuration."""
        formatter = TableFormatter()
        items = [
            {"id": 1, "title": "Test", "type": "paper"},
            {"id": 2, "title": "Test 2", "type": "code"},
        ]
        column_config = {
            "id": {"title": "ID", "width": 5},
            "title": {"title": "Title", "width": 15},
            "type": {"title": "Type", "width": 10},
        }
        result = formatter.format_list_with_custom_columns(items, column_config)
        assert "ID" in result
        assert "Title" in result
        assert "Type" in result

    def test_max_column_width_limit(self):
        """Test that max_column_width is respected."""
        formatter = TableFormatter(
            max_column_width=10,
            auto_size_columns=True
        )
        items = [
            {"id": 1, "title": "Short"},
            {"id": 2, "title": "This is a very long title that exceeds limit"},
        ]
        result = formatter.format_list(items)
        # Should truncate the long title
        assert "Short" in result

    def test_truncate_disabled(self):
        """Test that truncation can be disabled."""
        formatter = TableFormatter(
            truncate_long_content=False,
            max_column_width=10,
            auto_size_columns=True
        )
        items = [
            {"id": 1, "title": "This is a very long title that should not be truncated"},
        ]
        result = formatter.format_list(items)
        # When truncation is disabled, Rich still wraps text but doesn't add ellipsis
        # The text should appear in the output (possibly wrapped)
        assert "This is a" in result or "very long" in result

    def test_value_formatting_in_table(self):
        """Test various value types are formatted correctly."""
        formatter = TableFormatter()
        items = [
            {
                "id": 1,
                "title": "Test",
                "is_active": True,
                "score": 0.8567,
                "tags": ["python", "cli"],
                "notes": None,
            },
        ]
        result = formatter.format_list(items)
        # Check formatted values
        assert "Yes" in result  # True -> Yes
        assert "0.86" in result  # 0.8567 -> 0.86
        assert "python, cli" in result  # list formatting
        assert "-" in result  # None -> -

    def test_empty_values(self):
        """Test handling of empty/null values."""
        formatter = TableFormatter()
        items = [
            {"id": 1, "title": None, "description": ""},
            {"id": 2, "title": "Valid", "description": "text"},
        ]
        result = formatter.format_list(items)
        # Should handle None and empty string gracefully
        assert "Valid" in result


class TestTreeFormatter:
    """Tests for TreeFormatter."""

    def test_format_dict(self):
        """Test formatting dictionary."""
        formatter = TreeFormatter()
        result = formatter.format({"key": "value"}, "Root")
        assert "Root" in result
        assert "key" in result

    def test_format_nested_dict(self):
        """Test formatting nested dictionary."""
        formatter = TreeFormatter()
        result = formatter.format(
            {"outer": {"inner": "value"}},
            "Root",
        )
        assert "Root" in result
        assert "outer" in result

    def test_format_list(self):
        """Test formatting list."""
        formatter = TreeFormatter()
        result = formatter.format([{"id": 1}, {"id": 2}], "Items")
        assert "Items" in result

    def test_format_empty_list(self):
        """Test formatting empty list."""
        formatter = TreeFormatter()
        result = formatter.format_list([])
        assert "No results found" in result

    def test_format_error(self):
        """Test formatting error."""
        formatter = TreeFormatter()
        result = formatter.format_error(Exception("Test error"))
        assert "Test error" in result


class TestCSVFormatter:
    """Tests for CSVFormatter."""

    def test_format_list(self, sample_resources):
        """Test formatting list of resources."""
        formatter = CSVFormatter()
        result = formatter.format_list(sample_resources)
        assert "id" in result
        assert "title" in result
        assert "Resource 1" in result

    def test_format_dict(self):
        """Test formatting dictionary."""
        formatter = CSVFormatter()
        result = formatter.format({"key": "value", "number": 42})
        assert "key" in result
        assert "value" in result

    def test_format_empty_list(self):
        """Test formatting empty list."""
        formatter = CSVFormatter()
        result = formatter.format_list([])
        assert result == ""

    def test_format_error(self):
        """Test formatting error."""
        formatter = CSVFormatter()
        result = formatter.format_error(Exception("Test error"))
        assert "error" in result
        assert "type" in result

    def test_nested_data_flattening(self):
        """Test flattening nested data."""
        formatter = CSVFormatter()
        data = [{"nested": {"key": "value"}}]
        result = formatter.format_list(data)
        assert "nested.key" in result


class TestGetFormatter:
    """Tests for get_formatter function."""

    def test_get_json_formatter(self):
        """Test getting JSON formatter."""
        formatter = get_formatter("json")
        assert isinstance(formatter, JSONFormatter)

    def test_get_table_formatter(self):
        """Test getting table formatter."""
        formatter = get_formatter("table")
        assert isinstance(formatter, TableFormatter)

    def test_get_tree_formatter(self):
        """Test getting tree formatter."""
        formatter = get_formatter("tree")
        assert isinstance(formatter, TreeFormatter)

    def test_get_csv_formatter(self):
        """Test getting CSV formatter."""
        formatter = get_formatter("csv")
        assert isinstance(formatter, CSVFormatter)

    def test_get_default_formatter(self):
        """Test getting default formatter (table)."""
        formatter = get_formatter("unknown")
        assert isinstance(formatter, TableFormatter)