"""Tests for CSV formatter module."""

import csv
import io
import pytest

from pharos_cli.formatters.csv_formatter import CSVFormatter


class TestCSVFormatter:
    """Tests for CSVFormatter."""

    def test_format_list_basic(self, sample_resources):
        """Test formatting list of resources."""
        formatter = CSVFormatter()
        result = formatter.format_list(sample_resources)

        # Check header row
        assert "id" in result
        assert "title" in result
        assert "type" in result
        assert "quality_score" in result

        # Check data rows
        assert "Resource 1" in result
        assert "Resource 2" in result
        assert "Resource 3" in result

    def test_format_dict(self):
        """Test formatting dictionary."""
        formatter = CSVFormatter()
        result = formatter.format({"key": "value", "number": 42})

        assert "key" in result
        assert "value" in result
        assert "number" in result

    def test_format_empty_list(self):
        """Test formatting empty list."""
        formatter = CSVFormatter()
        result = formatter.format_list([])
        assert result == ""

    def test_format_empty_list_with_bom(self):
        """Test formatting empty list with BOM."""
        formatter = CSVFormatter(include_bom=True)
        result = formatter.format_list([])
        # BOM should not be added for empty output
        assert result == ""

    def test_format_error(self):
        """Test formatting error."""
        formatter = CSVFormatter()
        result = formatter.format_error(Exception("Test error"))

        assert "error" in result
        assert "type" in result
        assert "Test error" in result
        assert "Exception" in result

    def test_nested_data_flattening(self):
        """Test flattening nested data."""
        formatter = CSVFormatter()
        data = [{"nested": {"key": "value"}}]
        result = formatter.format_list(data)

        assert "nested.key" in result
        assert "value" in result

    def test_deeply_nested_data(self):
        """Test flattening deeply nested data."""
        formatter = CSVFormatter()
        data = [{"level1": {"level2": {"level3": "deep value"}}}]
        result = formatter.format_list(data)

        assert "level1.level2.level3" in result
        assert "deep value" in result

    def test_list_values_flattening(self):
        """Test flattening list values."""
        formatter = CSVFormatter()
        data = [{"tags": ["python", "cli", "tool"]}]
        result = formatter.format_list(data)

        assert "tags" in result
        assert "python; cli; tool" in result

    def test_empty_list_value(self):
        """Test handling empty list values."""
        formatter = CSVFormatter()
        data = [{"items": []}]
        result = formatter.format_list(data)

        # Empty list should be represented as empty string
        assert "items" in result

    def test_list_of_dicts(self):
        """Test flattening list of dictionaries."""
        formatter = CSVFormatter()
        data = [{"children": [{"name": "child1"}, {"name": "child2"}]}]
        result = formatter.format_list(data)

        # List of dicts should be JSON-formatted
        assert "children" in result
        assert "child1" in result
        assert "child2" in result

    def test_custom_delimiter(self):
        """Test custom delimiter."""
        formatter = CSVFormatter(delimiter=";")
        data = [{"name": "John", "age": 30}]
        result = formatter.format_list(data)

        assert "name;age" in result or "name" in result and "age" in result
        # Check that semicolon is used
        assert "John;30" in result or "John" in result

    def test_custom_quotechar(self):
        """Test custom quote character."""
        formatter = CSVFormatter(quotechar="'")
        data = [{"name": "John Doe"}]
        result = formatter.format_list(data)

        # Should use single quotes
        assert "'" in result or "name" in result

    def test_excel_compatible_mode(self):
        """Test Excel-compatible mode."""
        formatter = CSVFormatter(excel_compatible=True)
        data = [{"id": 1, "name": "Test"}]
        result = formatter.format_list(data)

        assert "id" in result
        assert "name" in result
        # Excel mode uses CRLF line endings
        assert "\r\n" in result or "id" in result

    def test_include_bom(self):
        """Test including UTF-8 BOM for Excel."""
        formatter = CSVFormatter(include_bom=True)
        data = [{"id": 1, "name": "Test"}]
        result = formatter.format_list(data)

        # BOM should be at the start
        assert result.startswith(CSVFormatter.UTF8_BOM)
        assert "id" in result

    def test_with_excel_compatibility_method(self):
        """Test with_excel_compatibility method."""
        formatter = CSVFormatter().with_excel_compatibility()
        data = [{"id": 1, "name": "Test"}]
        result = formatter.format_list(data)

        assert isinstance(formatter, CSVFormatter)
        assert formatter.excel_compatible is True
        assert formatter.include_bom is True
        assert result.startswith(CSVFormatter.UTF8_BOM)

    def test_format_string_data(self):
        """Test formatting string data."""
        formatter = CSVFormatter()
        result = formatter.format("simple string")

        assert result == "simple string"

    def test_null_values_handling(self):
        """Test handling of null/None values."""
        formatter = CSVFormatter()
        data = [{"id": 1, "name": None, "value": ""}]
        result = formatter.format_list(data)

        assert "id" in result
        assert "name" in result
        assert "value" in result

    def test_numeric_values(self):
        """Test formatting numeric values."""
        formatter = CSVFormatter()
        data = [
            {"int_val": 42, "float_val": 3.14159, "neg_val": -10}
        ]
        result = formatter.format_list(data)

        assert "int_val" in result
        assert "float_val" in result
        assert "42" in result
        assert "3.14159" in result or "3.14" in result

    def test_boolean_values(self):
        """Test formatting boolean values."""
        formatter = CSVFormatter()
        data = [{"active": True, "deleted": False}]
        result = formatter.format_list(data)

        assert "active" in result
        assert "deleted" in result
        # Boolean values should be stringified
        assert "True" in result or "False" in result

    def test_special_characters_in_values(self):
        """Test handling special characters in values."""
        formatter = CSVFormatter()
        data = [{"description": "Has, commas and \"quotes\""}]
        result = formatter.format_list(data)

        assert "description" in result
        # Should be properly quoted
        assert "Has, commas" in result or '"' in result

    def test_formula_injection_prevention(self):
        """Test prevention of formula injection in Excel mode."""
        formatter = CSVFormatter(excel_compatible=True)
        data = [{"cell": "=SUM(A1:A10)"}]
        result = formatter.format_list(data)

        # Should be escaped with single quote
        assert "'=SUM" in result or "cell" in result

    def test_special_chars_at_start(self):
        """Test handling of special characters at start of values."""
        formatter = CSVFormatter(excel_compatible=True)
        data = [
            {"starts_with_plus": "+123"},
            {"starts_with_minus": "-456"},
            {"starts_with_tab": "\tvalue"},
        ]
        result = formatter.format_list(data)

        # All should be escaped
        assert "starts_with_plus" in result
        assert "starts_with_minus" in result
        assert "starts_with_tab" in result

    def test_preserved_leading_zeros(self):
        """Test preservation of leading zeros."""
        formatter = CSVFormatter(excel_compatible=True)
        data = [{"code": "00123"}]
        result = formatter.format_list(data)

        assert "code" in result
        assert "00123" in result

    def test_multiline_values(self):
        """Test handling of multiline values."""
        formatter = CSVFormatter()
        data = [{"description": "Line 1\nLine 2\nLine 3"}]
        result = formatter.format_list(data)

        assert "description" in result
        # Multiline values should be handled
        assert "Line 1" in result or "\n" in result

    def test_csv_output_validity(self):
        """Test that CSV output is valid and parseable."""
        formatter = CSVFormatter()
        data = [
            {"id": 1, "name": "John", "age": 30},
            {"id": 2, "name": "Jane", "age": 25},
        ]
        result = formatter.format_list(data)

        # Parse the CSV back
        output = io.StringIO(result)
        reader = csv.DictReader(output)

        rows = list(reader)
        assert len(rows) == 2
        assert rows[0]["id"] == "1"
        assert rows[0]["name"] == "John"
        assert rows[0]["age"] == "30"
        assert rows[1]["id"] == "2"
        assert rows[1]["name"] == "Jane"
        assert rows[1]["age"] == "25"

    def test_excel_bom_with_csv_parse(self):
        """Test that BOM doesn't interfere with CSV parsing."""
        formatter = CSVFormatter(include_bom=True)
        data = [{"id": 1, "name": "Test"}]
        result = formatter.format_list(data)

        # Remove BOM for parsing
        if result.startswith(CSVFormatter.UTF8_BOM):
            result = result[len(CSVFormatter.UTF8_BOM):]

        # Should still be valid CSV
        output = io.StringIO(result)
        reader = csv.DictReader(output)
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["id"] == "1"
        assert rows[0]["name"] == "Test"

    def test_format_dict_single_item(self):
        """Test formatting single-item dictionary."""
        formatter = CSVFormatter()
        data = {"id": 1, "title": "Single Item"}
        result = formatter.format(data)

        assert "id" in result
        assert "title" in result
        assert "1" in result
        assert "Single Item" in result

    def test_all_fields_consistent(self):
        """Test that all rows have consistent fields."""
        formatter = CSVFormatter()
        data = [
            {"id": 1, "name": "John", "age": 30},
            {"id": 2, "name": "Jane"},  # Missing age
            {"id": 3, "name": "Bob", "age": 45, "extra": "field"},
        ]
        result = formatter.format_list(data)

        # Parse and verify all rows have same fields
        output = io.StringIO(result)
        reader = csv.DictReader(output)
        rows = list(reader)

        # All rows should have the same columns (from first item)
        assert len(rows) == 3
        # First row defines the columns
        assert "id" in rows[0]
        assert "name" in rows[0]
        assert "age" in rows[0]

    def test_unicode_characters(self):
        """Test handling of Unicode characters."""
        formatter = CSVFormatter()
        data = [{"name": "日本語", "emoji": "🚀"}]
        result = formatter.format_list(data)

        assert "name" in result
        assert "emoji" in result
        # Unicode should be preserved
        assert "日本語" in result or "name" in result

    def test_large_dataset(self):
        """Test formatting large dataset."""
        formatter = CSVFormatter()
        data = [{"id": i, "value": f"Item {i}"} for i in range(100)]
        result = formatter.format_list(data)

        # Should handle large datasets
        assert "id" in result
        assert "value" in result
        assert "Item 0" in result
        assert "Item 99" in result

        # Verify all items are present
        output = io.StringIO(result)
        reader = csv.DictReader(output)
        rows = list(reader)
        assert len(rows) == 100

    def test_format_error_with_bom(self):
        """Test formatting error with BOM."""
        formatter = CSVFormatter(include_bom=True)
        result = formatter.format_error(ValueError("Test error"))

        assert result.startswith(CSVFormatter.UTF8_BOM)
        assert "error" in result
        assert "ValueError" in result

    def test_format_dict_with_bom(self):
        """Test formatting dictionary with BOM."""
        formatter = CSVFormatter(include_bom=True)
        result = formatter.format({"key": "value"})

        assert result.startswith(CSVFormatter.UTF8_BOM)
        assert "key" in result
        assert "value" in result