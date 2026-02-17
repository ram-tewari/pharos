"""Table formatter for Pharos CLI."""

from typing import Any, List, Dict, Optional, Callable
from rich.table import Table, Column
from rich.console import Console
from rich.text import Text

from pharos_cli.formatters.base import Formatter
from pharos_cli.utils.console import get_console


class TableFormatter(Formatter):
    """Table output formatter using Rich."""

    def __init__(
        self,
        console: Optional[Console] = None,
        max_column_width: int = 50,
        max_rows_per_page: int = 50,
        truncate_long_content: bool = True,
        auto_size_columns: bool = True,
    ):
        """Initialize the table formatter.

        Args:
            console: Rich console instance (default: get_console())
            max_column_width: Maximum width for any column (default: 50)
            max_rows_per_page: Maximum rows per page for pagination (default: 50)
            truncate_long_content: Whether to truncate long content (default: True)
            auto_size_columns: Whether to auto-size columns based on content (default: True)
        """
        self.console = console or get_console()
        self.max_column_width = max_column_width
        self.max_rows_per_page = max_rows_per_page
        self.truncate_long_content = truncate_long_content
        self.auto_size_columns = auto_size_columns

    def format(self, data: Any) -> str:
        """Format data as table."""
        if isinstance(data, list):
            return self.format_list(data)
        elif isinstance(data, dict):
            return self._format_dict(data)
        return str(data)

    def format_list(self, items: List[Dict]) -> str:
        """Format list of items as table with pagination support."""
        if not items:
            return "No results found."

        # Calculate column widths for auto-sizing
        if self.auto_size_columns:
            column_widths = self._calculate_column_widths(items)
        else:
            column_widths = None

        # Paginate if needed
        if len(items) > self.max_rows_per_page:
            return self._format_paginated(items, column_widths)

        return self._format_table(items, column_widths)

    def _calculate_column_widths(self, items: List[Dict]) -> Dict[str, int]:
        """Calculate optimal column widths based on content.

        Args:
            items: List of dictionaries to calculate widths from

        Returns:
            Dictionary mapping column names to their calculated widths
        """
        if not items:
            return {}

        column_widths = {}
        keys = list(items[0].keys())

        for key in keys:
            # Start with header width
            header = key.replace("_", " ").title()
            max_width = len(header)

            # Check each item's value width
            for item in items:
                value = item.get(key, "")
                formatted = self._format_value(value)
                # Strip Rich markup for width calculation
                plain_text = self._strip_markup(formatted)
                max_width = max(max_width, len(plain_text))

            # Apply max column width limit
            column_widths[key] = min(max_width, self.max_column_width)

        return column_widths

    def _strip_markup(self, text: str) -> str:
        """Strip Rich markup from text for width calculation.

        Args:
            text: Text that may contain Rich markup

        Returns:
            Plain text without markup
        """
        import re
        # Remove Rich markup patterns like [bold], [/bold], [red], etc.
        pattern = r'\[/[a-zA-Z0-9]+\]|\[[a-zA-Z0-9]+(=.*?)?\]'
        return re.sub(pattern, '', text)

    def _truncate_text(self, text: str, max_width: int) -> str:
        """Truncate text to fit within max width.

        Args:
            text: Text to truncate
            max_width: Maximum width allowed

        Returns:
            Truncated text with ellipsis if needed
        """
        plain_text = self._strip_markup(text)
        if len(plain_text) <= max_width:
            return text

        # Truncate and add ellipsis
        # Account for the 3 characters of ellipsis
        available_width = max_width - 3
        if available_width < 1:
            return "..."

        truncated = plain_text[:available_width]
        return f"{truncated}..."

    def _format_table(self, items: List[Dict], column_widths: Optional[Dict[str, int]] = None) -> str:
        """Format items as a single table.

        Args:
            items: List of dictionaries to format
            column_widths: Optional pre-calculated column widths

        Returns:
            Formatted table as string
        """
        # Create table
        table = Table(show_header=True, header_style="bold magenta")
        table.box = getattr(table, "box", None) or Table.box

        # Add columns from first item
        keys = list(items[0].keys())
        for key in keys:
            column_name = key.replace("_", " ").title()
            width = column_widths.get(key) if column_widths else None
            table.add_column(column_name, width=width, overflow="fold" if not self.truncate_long_content else None)

        # Add rows
        for item in items:
            row = []
            for key, value in item.items():
                formatted = self._format_value(value)
                if self.truncate_long_content and column_widths:
                    max_width = column_widths.get(key, self.max_column_width)
                    formatted = self._truncate_text(formatted, max_width)
                row.append(formatted)
            table.add_row(*row)

        # Render to string
        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _format_paginated(
        self, items: List[Dict], column_widths: Optional[Dict[str, int]] = None
    ) -> str:
        """Format items as multiple paginated tables.

        Args:
            items: List of dictionaries to format
            column_widths: Optional pre-calculated column widths

        Returns:
            Formatted paginated tables as string
        """
        output_parts = []
        total_pages = (len(items) + self.max_rows_per_page - 1) // self.max_rows_per_page

        for page_num in range(total_pages):
            start_idx = page_num * self.max_rows_per_page
            end_idx = min(start_idx + self.max_rows_per_page, len(items))
            page_items = items[start_idx:end_idx]

            # Add page header
            page_info = f"\n[dim]Page {page_num + 1} of {total_pages} ({len(items)} total items)[/dim]\n"
            output_parts.append(page_info)

            # Format the page
            page_table = self._format_table(page_items, column_widths)
            output_parts.append(page_table)

        return "".join(output_parts)

    def _format_dict(self, data: Dict) -> str:
        """Format dictionary as key-value table."""
        table = Table(show_header=False, box=None)
        table.add_column("Key", style="bold")
        table.add_column("Value")

        for key, value in data.items():
            table.add_row(key, self._format_value(value))

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()

    def _format_value(self, value: Any) -> str:
        """Format a single value for table display."""
        if value is None:
            return "[dim]-[/dim]"
        elif isinstance(value, bool):
            return "[green]Yes[/green]" if value else "[red]No[/red]"
        elif isinstance(value, list):
            if len(value) == 0:
                return "[dim]-[/dim]"
            elif len(value) <= 3:
                return ", ".join(str(v) for v in value)
            else:
                return f"{len(value)} items"
        elif isinstance(value, float):
            return f"{value:.2f}"
        else:
            return str(value)

    def format_error(self, error: Exception) -> str:
        """Format error as table."""
        from rich.panel import Panel

        panel = Panel(
            f"[red]{error}[/red]",
            title="Error",
            border_style="red",
        )

        with self.console.capture() as capture:
            self.console.print(panel)

        return capture.get()

    def format_list_with_custom_columns(
        self,
        items: List[Dict],
        column_config: Dict[str, Dict[str, Any]]
    ) -> str:
        """Format list with custom column configuration.

        Args:
            items: List of dictionaries to format
            column_config: Configuration for each column
                e.g., {"id": {"title": "ID", "width": 10, "align": "right"}}

        Returns:
            Formatted table as string
        """
        if not items:
            return "No results found."

        table = Table(show_header=True, header_style="bold magenta")
        table.box = getattr(table, "box", None) or Table.box

        keys = list(items[0].keys())
        for key in keys:
            config = column_config.get(key, {})
            title = config.get("title", key.replace("_", " ").title())
            width = config.get("width")
            align = config.get("align", "left")
            style = config.get("style")

            table.add_column(title, width=width, style=style)

        # Add rows
        for item in items:
            row = []
            for key, value in item.items():
                formatted = self._format_value(value)
                row.append(formatted)
            table.add_row(*row)

        with self.console.capture() as capture:
            self.console.print(table)

        return capture.get()