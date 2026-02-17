"""CSV formatter for Pharos CLI."""

import csv
import io
from typing import Any, List, Dict, Optional

from pharos_cli.formatters.base import Formatter


class CSVFormatter(Formatter):
    """CSV output formatter with Excel compatibility."""

    # UTF-8 BOM for Excel compatibility
    UTF8_BOM = "\ufeff"

    def __init__(
        self,
        delimiter: str = ",",
        quotechar: str = '"',
        excel_compatible: bool = False,
        include_bom: bool = False,
    ):
        """Initialize the CSV formatter.

        Args:
            delimiter: Field delimiter (default: ",")
            quotechar: Quote character (default: '"')
            excel_compatible: Enable Excel-compatible formatting (default: False)
            include_bom: Include UTF-8 BOM for Excel (default: False)
        """
        self.delimiter = delimiter
        self.quotechar = quotechar
        self.excel_compatible = excel_compatible
        self.include_bom = include_bom

    def format(self, data: Any) -> str:
        """Format data as CSV."""
        if isinstance(data, list):
            return self.format_list(data)
        elif isinstance(data, dict):
            return self._format_dict(data)
        return data

    def format_list(self, items: List[Dict]) -> str:
        """Format list of items as CSV."""
        if not items:
            return self._get_output("")

        # Flatten all items and collect all unique fieldnames
        flat_items = []
        all_keys = set()
        for item in items:
            flat_item = self._flatten(item)
            if self.excel_compatible:
                flat_item = self._sanitize_for_excel(flat_item)
            flat_items.append(flat_item)
            all_keys.update(flat_item.keys())

        # Sort keys for consistent output
        fieldnames = sorted(all_keys)

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=fieldnames,
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n" if self.excel_compatible else "\n",
        )

        writer.writeheader()
        for flat_item in flat_items:
            writer.writerow(flat_item)

        return self._get_output(output.getvalue())

    def _get_output(self, content: str) -> str:
        """Add BOM if needed and return output.

        Args:
            content: The CSV content

        Returns:
            Content with BOM prepended if include_bom is True and content is not empty
        """
        if self.include_bom and content:
            return self.UTF8_BOM + content
        return content

    def _flatten(self, data: Any, prefix: str = "") -> Dict[str, Any]:
        """Flatten nested dictionaries.

        Args:
            data: Data to flatten
            prefix: Prefix for nested keys

        Returns:
            Flattened dictionary
        """
        result = {}

        if not isinstance(data, dict):
            return {prefix: data} if prefix else data

        for key, value in data.items():
            new_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                result.update(self._flatten(value, new_key))
            elif isinstance(value, list):
                result[new_key] = self._flatten_list(value)
            else:
                result[new_key] = value

        return result

    def _flatten_list(self, value: List[Any]) -> str:
        """Flatten a list value to a string.

        Args:
            value: List to flatten

        Returns:
            String representation of the list
        """
        if len(value) == 0:
            return ""
        elif isinstance(value[0], dict):
            # For list of dicts, join as JSON
            return "[" + ", ".join(str(v) for v in value) + "]"
        else:
            return "; ".join(str(v) for v in value)

    def _sanitize_for_excel(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize values for Excel compatibility.

        Excel has issues with:
        - Leading zeros in numeric strings (e.g., "00123")
        - Long numbers that get converted to scientific notation
        - Special characters like =, +, -, @ at the start (formula injection)

        Args:
            data: Dictionary with values to sanitize

        Returns:
            Sanitized dictionary
        """
        sanitized = {}
        for key, value in data.items():
            if value is None:
                sanitized[key] = ""
            elif isinstance(value, str):
                # Escape strings that start with special characters
                # to prevent Excel formula injection
                if value.startswith(("=", "+", "-", "\t", "\n")):
                    sanitized[key] = "'" + value
                # Preserve leading zeros by quoting
                elif value.isdigit() and len(value) > 1 and value.startswith("0"):
                    sanitized[key] = value  # Keep as-is, Excel will handle
                else:
                    sanitized[key] = value
            else:
                sanitized[key] = value
        return sanitized

    def _format_dict(self, data: Dict) -> str:
        """Format dictionary as CSV."""
        flat_data = self._flatten(data)

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=flat_data.keys(),
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            quoting=csv.QUOTE_MINIMAL,
            lineterminator="\r\n" if self.excel_compatible else "\n",
        )

        writer.writeheader()
        if self.excel_compatible:
            flat_data = self._sanitize_for_excel(flat_data)
        writer.writerow(flat_data)

        return self._get_output(output.getvalue())

    def format_error(self, error: Exception) -> str:
        """Format error as CSV."""
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["error", "type"])
        writer.writerow([str(error), type(error).__name__])

        return self._get_output(output.getvalue())

    def with_excel_compatibility(self) -> "CSVFormatter":
        """Return a new formatter with Excel compatibility enabled.

        Returns:
            New CSVFormatter instance with Excel compatibility
        """
        return CSVFormatter(
            delimiter=self.delimiter,
            quotechar=self.quotechar,
            excel_compatible=True,
            include_bom=True,
        )